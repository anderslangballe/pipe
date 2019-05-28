import uuid

from flask import Flask, request
from flask import jsonify
from flask_cors import CORS

from job import *
from sources import load_sources

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
engines = [FedXInvoker, HibiscusInvoker, SemaGrowInvoker, SplendidInvoker, OdysseyInvoker]
jobs = dict()


@app.route('/api/job', methods=['POST'])
def perform_query():
    if not request.json or 'query' not in request.json or not request.json['query'] or not request.json['engines']:
        return jsonify(dict(message='Invalid query')), 400

    selected_engines = []
    for engine in request.json['engines']:
        if engine < 0 or engine >= len(engines):
            return jsonify(dict(message='Invalid engine.')), 400

        selected_engines.append(engines[engine]())

    available_sources = load_sources().items()
    selected_sources = {src: endpoint for src, endpoint in available_sources if src in request.json['sources']}
    if len(selected_sources) == 0:
        return jsonify(dict(message='You must select at least one valid source.')), 400

    timeout = 0
    if request.json['timeout']:
        timeout = request.json['timeout']

    # Create job with associated UUID
    job_uuid = str(uuid.uuid4())
    job = Job(timeout, request.json['query'], selected_engines, selected_sources)
    jobs[job_uuid] = job

    # Run job in separate thread
    job.run()

    return jsonify(dict(ticket=job_uuid))


@app.route('/api/job/<ticket>', methods=['DELETE'])
def delete_job(ticket):
    if ticket not in jobs:
        return jsonify(dict(message='Job not found.', state=JobState.ABORTED)), 404

    job = jobs[ticket]
    job.cancel()

    return jsonify(dict(success=True))


@app.route('/api/job/<ticket>', methods=['GET'])
def get_state(ticket):
    if ticket not in jobs:
        return jsonify(dict(message='Job not found.', state=JobState.ABORTED)), 404

    job = jobs[ticket]
    if job.get_state() != JobState.SUCCESS:
        return jsonify(dict(message=job.get_message(), state=job.get_state())), 200

    abbreviations = [{'abbreviation': v, 'value': k} for k, v in job.get_pattern_map().items()]
    source_map = {v: list(k) for k, v in job.get_sources_map().items()}

    return jsonify(dict(state=job.get_state(), results=job.get_results(), bindingNames=job.get_binding_names(),
                        tuples=job.get_tuples(), abbreviations=abbreviations, sourceMap=source_map))


@app.route('/api/engines', methods=['GET'])
def get_engines():
    return jsonify(dict(engines=[{'name': engine.get_name(), 'id': idx} for idx, engine in enumerate(engines)]))


@app.route('/api/sources', methods=['GET'])
def get_sources():
    sources = load_sources().items()
    return jsonify(dict(sources=[{'source': source, 'endpoint': endpoint} for source, endpoint in sources]))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
