import re


def comp_case(name):
    return " ".join(w.capitalize() for w in name.split())


def decomp_case(name):
    return name.upper().replace("'", "''")


def clean_desc(raw):
    despaced = ' '.join(filter(lambda x: x != '', raw.split(' ')))
    item1 = re.compile('(\ *)ITEM 1(\.*) BUSINESS(\.*)', re.IGNORECASE)
    desc = item1.sub('', despaced).strip()
    return filter(lambda x: x != '', desc.split('\n'))
