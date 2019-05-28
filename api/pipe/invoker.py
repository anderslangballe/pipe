import fnmatch
import shutil
import subprocess
from enum import IntEnum
from tempfile import mktemp

from rewrites import *
from sources import fill_template

HOME = '/opt/pipe'
LOG_BASE = os.path.join(HOME, 'logs')

LIBRARIES = os.path.join(HOME, 'libs')
JENA = os.path.join(LIBRARIES, 'apache-jena-2.13.0')
JACKSON = os.path.join(LIBRARIES, 'Jackson')
OPTIMIZER = os.path.join(LIBRARIES, 'optimizerResult')

ENGINES = os.path.join(HOME, 'engines')
FEDX = os.path.join(ENGINES, 'fedX')
SPLENDID = os.path.join(ENGINES, 'rdffederator')
SEMAGROW = os.path.join(ENGINES, 'semagrow')
HIBISCUS = os.path.join(ENGINES, 'hibiscus')
ODYSSEY = os.path.join(ENGINES, 'odyssey')


class InvokeState(IntEnum):
    SUCCESS = 0
    TIMEOUT = 1
    UNKNOWN_ERROR = 2
    MISMATCH = 3
    NO_RESULTS = 4


def get_class_path(paths: list):
    path = '.'

    for lib in paths:
        path += ':{}/lib/*'.format(lib)

    return path


def invoke_class(job, base_path, class_path, class_name, *args):
    err = open(os.path.join(LOG_BASE, 'stderr.log'), 'a')
    out = open(os.path.join(LOG_BASE, 'stdout.log'), 'a')

    os.chdir(base_path)

    command = ['java', '-Xmx4G', '-cp', class_path, class_name, *args]

    process = subprocess.Popen(command, stdout=out, stderr=err)
    job.set_current_process(process)
    print(process.args)
    if job.get_timeout() > 0:
        try:
            process.wait(job.get_timeout())
        except subprocess.TimeoutExpired:
            process.kill()

            err.write('Timed out\n')

            return InvokeState.TIMEOUT
    else:
        process.wait()
        process.kill()

    for handle in [err, out]:
        handle.write("\n\n\n")

        handle.flush()
        handle.close()

    return InvokeState.SUCCESS


class TemporaryFile:
    def __init__(self, class_name):
        self.file_path = mktemp(class_name)

    def __enter__(self):
        pass

    def get_name(self):
        return self.file_path

    def get_contents(self):
        if not os.path.isfile(self.file_path):
            return None

        with open(self.file_path, 'r') as f:
            return f.read()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not os.path.isfile(self.file_path):
            return

        os.remove(self.file_path)


class SplendidInvoker:
    CLASS_NAME = 'de.uni_koblenz.west.splendid.SPLENDID'
    TEMPLATE_DIR = os.path.join(SPLENDID, 'template')
    FEDERATION_DIR = os.path.join(SPLENDID, 'federation')
    FEDERATION_FILE = 'splendidFedBenchFederationVirtuoso.n3'
    # Only need FedX to use OptimizerResult and Jena to use Jackson
    # FedX gives the wrong Sesame JARs, should be avoided
    CLASSPATH = get_class_path([SPLENDID, OPTIMIZER, JACKSON])

    @staticmethod
    def get_name():
        return 'SPLENDID'

    def perform_rewrites(self, result):
        result['plan'] = rewrite_named_sources(result['plan'], rewrite_semagrow_splendid)

        return result

    def perform_query(self, job):
        templates = [self.FEDERATION_FILE, 'chebi_void.n3', 'dbpedia_void.n3', 'drugbank_void.n3',
                     'geonames_void.n3', 'jamendo_void.n3', 'kegg_void.n3', 'lmdb_void.n3', 'nytimes_void.n3',
                     'swdf_void.n3']
        fill_template(job.get_sources(), templates, self.TEMPLATE_DIR, self.FEDERATION_DIR, ',')

        file = TemporaryFile(self.get_name())
        with file:
            state = invoke_class(job, os.path.join(SPLENDID, 'bin'), self.CLASSPATH, self.CLASS_NAME,
                                 os.path.join(self.FEDERATION_DIR, self.FEDERATION_FILE), job.get_query(),
                                 file.get_name())

            return state, file.get_contents()


class SemaGrowInvoker:
    CLASS_NAME = 'eu.semagrow.cli.CliMain'
    TEMPLATE_DIR = os.path.join(SEMAGROW, 'template')
    FEDERATION_DIR = os.path.join(SEMAGROW, 'federation')
    REPOSITORY_FILE = 'repository.ttl'
    METADATA_FILE = 'semagrowMetadata.ttl'
    # Only need Jena to use Jackson
    CLASSPATH = get_class_path([OPTIMIZER, JACKSON, os.path.join(SEMAGROW, 'WEB-INF')])

    @staticmethod
    def get_name():
        return 'SemaGrow'

    def perform_rewrites(self, result):
        result['plan'] = rewrite_named_sources(result['plan'], rewrite_semagrow_splendid)

        return result

    def perform_query(self, job):
        fill_template(job.get_sources(), [self.REPOSITORY_FILE, self.METADATA_FILE], self.TEMPLATE_DIR,
                      self.FEDERATION_DIR)

        file = TemporaryFile(self.get_name())
        with file:
            state = invoke_class(job, os.path.join(SEMAGROW, 'bin'), self.CLASSPATH, self.CLASS_NAME,
                                 os.path.join(self.FEDERATION_DIR, self.REPOSITORY_FILE), job.get_query(), 'out.json',
                                 file.get_name())

            return state, file.get_contents()


class FedXInvoker:
    CLASS_NAME = 'com.fluidops.fedx.CLI'
    FEDX_CONFIG = os.path.join(FEDX, 'config2')
    CLASSPATH = get_class_path([FEDX, OPTIMIZER, JENA])
    TEMPLATE_DIR = os.path.join(FEDX, 'template')
    FEDERATION_DIR = os.path.join(FEDX, 'federation')
    FEDERATION_FILE = 'fedBenchFederation.ttl'

    @staticmethod
    def get_name():
        return 'FedX'

    def perform_rewrites(self, result):
        result['plan'] = rewrite_named_sources(result['plan'], rewrite_fedx_odyssey)

        return result

    def perform_query(self, job):
        fill_template(job.get_sources(), [self.FEDERATION_FILE], self.TEMPLATE_DIR, self.FEDERATION_DIR)

        remove_files(FEDX, 'bin/cache.db')

        file = TemporaryFile(self.get_name())
        with file:
            state = invoke_class(job, os.path.join(FEDX, 'bin'), self.CLASSPATH, self.CLASS_NAME,
                                 '-c', self.FEDX_CONFIG, '-d', os.path.join(self.FEDERATION_DIR, self.FEDERATION_FILE),
                                 '-file', file.get_name(), '-q', job.get_query())

            return state, file.get_contents()


class HibiscusInvoker:
    CLASS_NAME = 'com.fluidops.fedx.CLI'
    CONFIG = os.path.join(HIBISCUS, 'config.properties')
    CLASSPATH = get_class_path([HIBISCUS, OPTIMIZER])
    TEMPLATE_DIR = os.path.join(HIBISCUS, 'template')
    FEDERATION_DIR = os.path.join(HIBISCUS, 'federation')
    FEDERATION_FILE = 'statsHibiscus.n3'

    @staticmethod
    def get_name():
        return 'HiBISCuS'

    def perform_rewrites(self, result):
        result['plan'] = rewrite_named_sources(result['plan'], rewrite_hibiscus)

        return result

    def perform_query(self, job):
        fill_template(job.get_sources(), [self.FEDERATION_FILE], self.TEMPLATE_DIR, self.FEDERATION_DIR)

        base = os.path.join(HIBISCUS, 'bin')
        remove_files(base, 'summaries*')

        file = TemporaryFile(self.get_name())
        with file:
            state = invoke_class(job, base, self.CLASSPATH, self.CLASS_NAME, '-c', self.CONFIG, '-file',
                                 file.get_name(), '-q', job.get_query())

            return state, file.get_contents()


class OdysseyInvoker:
    CLASS_NAME = 'evaluateSPARQLQuery'
    TEMPLATE_DIR = os.path.join(ODYSSEY, 'template')
    FEDERATION_DIR = os.path.join(ODYSSEY, 'federation')
    FEDERATION_FILE = 'fedBenchFederation.ttl'
    DATASETS_FILE = 'datasetsVirtuoso'
    DATASETS_PATH = os.path.join(FEDERATION_DIR, DATASETS_FILE)
    FEDBENCH_PATH = os.path.join(ODYSSEY, 'fedbench')
    BUDGET = '100000000'
    INCLUDE_MULTIPLICITY = 'true'
    ORIGINAL = 'false'
    CLASSPATH = get_class_path([JENA, FEDX, OPTIMIZER])

    @staticmethod
    def get_name():
        return 'Odyssey'

    def perform_rewrites(self, result):
        result['plan'] = rewrite_named_sources(result['plan'], rewrite_fedx_odyssey)

        return result

    def perform_query(self, job):
        fill_template(job.get_sources(), [self.FEDERATION_FILE, self.DATASETS_FILE], self.TEMPLATE_DIR,
                      self.FEDERATION_DIR)

        base = os.path.join(ODYSSEY, 'bin')
        remove_files(base, 'cache.db')

        file = TemporaryFile(self.get_name())
        with file:
            state = invoke_class(job, base, self.CLASSPATH, self.CLASS_NAME, job.get_query(), self.DATASETS_PATH,
                                 self.FEDBENCH_PATH, self.BUDGET, self.INCLUDE_MULTIPLICITY, self.ORIGINAL,
                                 file.get_name())

            return state, file.get_contents()


def remove_files(path, search_pattern):
    for element in os.listdir(path):
        if fnmatch.fnmatch(element, search_pattern):
            element = os.path.join(path, element)
            if os.path.isfile(element):
                os.remove(element)
            elif os.path.isdir(element):
                shutil.rmtree(element)

            break
    else:
        print(f'Could not delete {search_pattern}')
