import json
import os
import pickle
import sys
import time
import urllib

import facebook

APPTOKEN = '788525671579898|LIbUwc62bJF0RSWkq9RkwR1wfJM'
TOKEN = 'EAALNKPCNAPoBAFWioQyKnExfkuqmtMTDvfe3kORXg8pjZBy9amFyei3dMCKwOEgDo8fxCgWHmWcJkbmFQ79pfTnX2Y6uPijuGvXQuyhoR5UVT5dOMGQrHg8UIgtZAWdYvCtZACHFOfhN7KmNG2aVLZAZAiph7TI0lhZCjnkJTNvQZDZD'
SAFE_CHARS = '-_() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
ID = 'me'

#graph = facebook.GraphAPI(access_token=userToken)


def save(res, name='data'):
    """Save data to a file"""
    with open('%s.lst' % name, 'w') as f:
        pickle.dump(res, f)


def read(name='data'):
    """Read data from a file"""
    with open('%s.lst' % name, 'r') as f:
        res = pickle.load(f)
    return res


def fetch(limit=1000, depth=10, last=None, id=ID, token=TOKEN):
    """Fetch the data using Facebook's Graph API"""
    lst = []
    graph = facebook.GraphAPI(token)
    url = '%s/photos/uploaded' % id

    if not last:
        args = {'fields': ['source', 'name'], 'limit': limit}
        res = graph.request('%s/photos/uploaded' % id, args)
        process(lst, res['data'])
    else:
        res = {'paging': {'next': last}}

    # continue fetching till all photos are found
    for _ in range(depth):
        if 'paging' not in res:
            break
        try:
            url = res['paging']['next']
            res = json.loads(urllib.urlopen(url).read())
            process(lst, res['data'])
        except:
            break

    save(url, 'last_url')

    return lst


def process(res, dat):
    """Extract required data from a row"""
    err = []
    for d in dat:
        if 'source' not in d:
            err.append(d)
            continue
        src = d['source']
        if 'name' in d:
            name = ''.join(c for c in d['name'][:99] if c in SAFE_CHARS) + src[-4:]
        else:
            name = src[src.rfind('/') + 1:]
        res.append({'name': name, 'src': src})
    if err:
        print
        '%d errors.' % len(err)
        print
        err
    print
    '%d photos found.' % len(dat)


def download(res):
    """Download the list of files"""
    start = time.clock()
    if not os.path.isdir(ID):
        os.mkdir(ID)
    os.chdir(ID)
    for p in res:
        # try to get a higher resolution of the photo
        p['src'] = p['src'].replace('_s', '_n')
        urllib.urlretrieve(p['src'], p['name'])
    print
    "Downloaded %s pictures in %.3f sec." % (len(res), time.clock() - start)


if __name__ == '__main__':
    # download 500 photos, fetch details about 100 at a time
    lst = fetch(limit=100, depth=5)
    save(lst, 'photos')
    download(lst)