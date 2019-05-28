import os

endpoint_to_identifier = {
    os.getenv('ENDPOINT_CHEBI'): 'ChEBI',
    os.getenv('ENDPOINT_KEGG'): 'KEGG',
    os.getenv('ENDPOINT_DRUGBANK'): 'Drugbank',
    os.getenv('ENDPOINT_GEONAMES'): 'Geonames',
    os.getenv('ENDPOINT_DBPEDIA'): 'DBpedia',
    os.getenv('ENDPOINT_JAMENDO'): 'Jamendo',
    os.getenv('ENDPOINT_NYTIMES'): 'NYTimes',
    os.getenv('ENDPOINT_SWDF'): 'SWDF',
    os.getenv('ENDPOINT_LMDB'): 'LMDB',
}


def get_identifier(endpoint):
    return endpoint_to_identifier[endpoint]


def rewrite_fedx_odyssey(source):
    if source.startswith('http'):
        return rewrite_semagrow_splendid(source)

    return source.replace('sparql', '').strip('_')


def rewrite_hibiscus(source):
    if source.startswith('http'):
        return rewrite_semagrow_splendid(source)

    return get_identifier(source.replace('sparql', '').strip('_').strip('/'))


def rewrite_semagrow_splendid(source):
    return get_identifier(source.replace('http://', '').replace('/sparql', ''))


def rewrite_named_sources(plan, rule):
    if 'children' in plan:
        [rewrite_named_sources(child, rule) for child in plan['children']]

    if plan['sources']:
        plan['sources'] = [rule(source) for source in plan['sources']]

    return plan
