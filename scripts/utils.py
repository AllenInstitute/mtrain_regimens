from __future__ import print_function
import sys, os
import itertools
import requests
import pandas as pd

API_BASE = 'http://mtrain:5000'


def get_page(table_name, api_base=API_BASE, get_obj=None, **kwargs):

    if get_obj is None:
        get_obj = requests

    data = {'total_pages':'--'}
    for ii in itertools.count(1):
        print('Downloading page: %s/%s ' % (ii , data['total_pages']), end='')
        sys.stdout.flush()

        url = "{}/api/v1/{}?page={}".format(api_base, table_name, ii)
        print(url)
        tmp = get_obj.get(url, **kwargs)
        try:
            data = tmp.json()
        except TypeError:
            data = tmp.json
        print('... ', end='')
        if 'message' not in data:
            df = pd.DataFrame(data["objects"])
            print('done')
            sys.stdout.flush()
            yield df

        if 'total_pages' not in data or data['total_pages'] == ii:
            print('done')
            return

def get_df(table_name, api_base=API_BASE, get_obj=None, **kwargs):
    return pd.concat([df for df in get_page(table_name, api_base=api_base, get_obj=get_obj, **kwargs)], axis=0)
