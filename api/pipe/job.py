import json
import threading

from invoker import *


class JobState(IntEnum):
    SUCCESS = 0
    IN_PROGRESS = 1
    ABORTED = 2


class Job:
    def __init__(self, timeout, query, invokers, sources):
        self._message = 'Initializing'
        self._thread = None
        self._state = JobState.IN_PROGRESS
        self._timeout = timeout
        self._query = query
        self._binding_names = list()
        self._tuples = list()
        self._results = list()
        self._pattern_map = dict()
        self._sources_map = dict()
        self._sources_count = 0  # Number of unique sources
        self._triples_count = 0  # Number of unique triple patterns
        self._invokers = invokers
        self._sources = sources
        self._current_process = None
        self._cancelled = False

    def get_tuples(self):
        return self._tuples

    def get_binding_names(self):
        return self._binding_names

    def get_results(self):
        return self._results

    def get_message(self):
        return self._message

    def get_state(self):
        return self._state

    def get_pattern_map(self):
        return self._pattern_map

    def get_sources_map(self):
        return self._sources_map

    def run(self):
        # Delete logs
        remove_files(LOG_BASE, 'stderr.log')
        remove_files(LOG_BASE, 'stdout.log')

        self._thread = threading.Thread(target=self._invoke)
        self._thread.start()

    def _abort(self, message):
        self._state = JobState.ABORTED
        self._message = message

        return False

    def _success(self):
        self._state = JobState.SUCCESS

        return True

    def get_sources(self):
        return self._sources

    def get_timeout(self):
        return self._timeout

    def get_query(self):
        return self._query

    def set_current_process(self, process):
        self._current_process = process

    def _run_invoker(self, invoker, index, num_invokers):
        self._message = 'Running {} ({}/{})'.format(invoker.get_name(), index + 1, num_invokers)
        state, result = invoker.perform_query(self)

        # Write result to file
        os.chdir(LOG_BASE)
        with open('{}.json'.format(invoker.get_name()), 'w+') as f:
            if not result:
                f.write('No result')
            else:
                f.write(result)

        if not result:
            if InvokeState.SUCCESS:
                return self._abort('Internal error occurred. {} returned no result.'.format(invoker.get_name()))
            else:
                plan = dict(value='N/A', sources=None)
                result = dict(name=invoker.get_name(), state=state, bindingNames=None, tuples=None, plan=plan,
                              executionTime=0, planningTime=0)
        else:
            # Parse result as JSON
            result = json.loads(result)

        # Ask the invoker to rewrite the result
        if result['plan']:
            result = invoker.perform_rewrites(result)

        # Take this optimizer's binding names and tuples
        # Names are sorted for the sake of list comparison
        cur_names = result['bindingNames']
        cur_tuples = result['tuples']

        if cur_names and cur_tuples:
            # If not first entry, check if list of binding names and tuples have same length
            if self._binding_names and self._tuples:
                if len(cur_names) != len(self._binding_names) or len(cur_tuples) != len(self._tuples):
                    state = InvokeState.MISMATCH
            else:
                self._binding_names = cur_names
                self._tuples = cur_tuples
        elif state == InvokeState.SUCCESS:
            state = InvokeState.NO_RESULTS

        # Update state if there is no plan
        plan = result['plan']
        if not plan and state != InvokeState.TIMEOUT:
            state = InvokeState.UNKNOWN_ERROR

        # Add the number of tuples to each plan
        result['numTuples'] = len(result['tuples']) if result['tuples'] else 0

        # Remove these entries from the result's dictionary
        del result['bindingNames']
        del result['tuples']

        result['state'] = state
        self._results.append(result)

        return True

    def cancel(self):
        self._cancelled = True

        if self._current_process:
            self._current_process.kill()

    def _walk_patterns(self, plan):
        if 'children' in plan:
            [self._walk_patterns(child) for child in plan['children']]

        if 'literal' in plan:
            if plan['literal'] not in self._pattern_map:
                self._triples_count += 1
                self._pattern_map[format(plan['literal'])] = 'TP{}'.format(self._triples_count)

            plan['value'] = self._pattern_map[plan['literal']]
            # We can discard the literal after adding the abbreviation
            del plan['literal']

    def _walk_sources(self, plan):
        if 'children' in plan:
            [self._walk_sources(child) for child in plan['children']]

        if plan['sources']:
            sources = frozenset(plan['sources'])

            if sources not in self._sources_map:
                self._sources_count += 1
                self._sources_map[sources] = 'SRC{}'.format(self._sources_count)

            plan['sourceId'] = self._sources_map[sources]

        del plan['sources']

    def _invoke(self):
        for index, invoker in enumerate(self._invokers):
            if self._cancelled:
                return self._abort('Job cancelled.')

            if not self._run_invoker(invoker, index, len(self._invokers)):
                break
        else:
            # Perform a walk over all plans to produce TP maps and source maps
            for result in self._results:
                if result['plan']:
                    self._walk_patterns(result['plan'])
                    self._walk_sources(result['plan'])

            return self._success()
