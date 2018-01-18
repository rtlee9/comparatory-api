"""Index company descriptions to ElasticSearch index."""
import json
from os import path
import logging

from app.connect import _connect_es
from config import path_data, path_es

es = _connect_es()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_docs(descriptions_path):
    """Read company descriptions from disk."""
    logger.info('Reading descriptions from {}'.format(descriptions_path))
    with open(descriptions_path, 'r') as f:
        docs = json.load(f)
    return docs


def prep_index(index_nm):
    """Delete old index and prep mappings."""
    es.indices.delete(index=index_nm, ignore=[400, 404])  # TODO: zero downtime updates with aliasing
    logger.info('Deleted current index {}'.format(index_nm))

    # create index
    with open(path.join(path_es, 'settings.json'), 'r') as f:
        index_settings = json.load(f)
    es.indices.create(index=index_nm, body=index_settings)
    logger.info('Added new index {} with settings {}'.format(index_nm, index_settings))

    # add mapping
    with open(path.join(path_es, 'mapping.json'), 'r') as f:
        mapping = json.load(f)
    es.indices.put_mapping(
        index=index_nm, doc_type='company',
        body=mapping)
    logger.info('Added mapping {} to index'.format(mapping))


# Upload doc by doc to avoid batch limit
def put_docs_es(descriptions_path):
    """Doc-by-doc upload to AWS elasticseach node."""
    docs = get_docs(descriptions_path)
    for d in docs:
        _id = d['ticker']
        es.index(index='company_profile', doc_type='company', body=d, id=_id)
    logger.info('Indexed {:,} company descriptions'.format(len(docs)))


def main(local_load=False, aws_load=False):
    """Index company descriptions to ElasticSearch index."""
    prep_index('comparatory')
    put_docs_es(path.join(path_data, 'all_descriptions.json'))

if __name__ == "__main__":
    main()
