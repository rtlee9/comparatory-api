import re
import numpy as np
from scipy.sparse import csr_matrix

from connect import get_db


def comp_case(name):
    return " ".join(w.capitalize() for w in name.split())


def decomp_case(name):
    return name.upper().replace("'", "''")


def clean_desc(raw):
    despaced = ' '.join(filter(lambda x: x != '', raw.split(' ')))
    item1 = re.compile('(\ *)ITEM 1(\.*) BUSINESS(\.*)', re.IGNORECASE)
    desc = item1.sub('', despaced).strip()
    return filter(lambda x: x != '', desc.split('\n'))


def save_sparse_csr(filename, array):
    np.savez(
        filename,
        data=array.data,
        indices=array.indices,
        indptr=array.indptr,
        shape=array.shape,
    )


def load_sparse_csr(filename):
    loader = np.load(filename)
    return csr_matrix((
        loader['data'],
        loader['indices'],
        loader['indptr']),
        shape=loader['shape'],
    )


def clean_name(name_raw):
    """
    Clean company names
    """
    name = name_raw.upper()
    name = name.split('/')[0]
    name = name.replace('&AMP;', '&')
    name = name.replace('.', '')
    name = name.replace(',', '')
    return ' '.join(name.split())


def get_desc(id):
    cursor = get_db()
    cursor.execute("""
    select raw_description
    from company_dets
    where id = '{}'
    """.format(id))
    try:
        return clean_desc(cursor.fetchone()[0])
    except TypeError as e:
        print('No description found for {}'.format(id))
        return ''
