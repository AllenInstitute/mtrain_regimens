import yaml
import os
import hashlib
import warnings
import requests
import sys
import itertools
import pandas as pd

'''
Copy-pasted get_page and get_df; This is code duplication, but I dont want this to be an installed package, and both tests and scripts need this code
'''

def get_page(table_name, api_base='http://prodmtrain1:5000', get_obj=None, **kwargs):

    if get_obj is None:
        get_obj = requests

    data = {'total_pages':'--'}
    for ii in itertools.count(1):
        print('Downloading page: %s/%s ' % (ii , data['total_pages']), end='')
        sys.stdout.flush()

        tmp = get_obj.get(os.path.join(api_base, "api/v1/%s?page=%i" % (table_name, ii)), **kwargs)
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

def get_df(table_name, api_base='http://prodmtrain1:5000', get_obj=None, **kwargs):
    return pd.concat([df for df in get_page(table_name, api_base=api_base, get_obj=get_obj, **kwargs)], axis=0)


def test_script_files_download(regimen_dict):

    for stage_name, stage_dict in regimen_dict['stages'].items():
        if stage_dict['script'] == 'NotImplemented':
            warnings.warn('Stage "%s" Not Implemented' % stage_name)
        else:
            if 'raw' not in stage_dict['script']:
                raise Exception('URL appears to not be a raw file: %s' % stage_dict['script'])
            # if len(stage_dict['script'].split('/')[-2]) != 40:
            #     raise Exception('URL appears to not have a specific hash indicated: %s' % stage_dict['script'])
            result = requests.get(stage_dict['script'])
            if result.status_code != 200:
                raise Exception('Could not reach endpoint: %s' % stage_dict['script'])

            else:
                downloaded_md5 = hashlib.md5(result.content).hexdigest()
                assert downloaded_md5 == stage_dict['script_md5'], "{}:{}".format(stage_name,downloaded_md5)

def test_add_already_tracked_regimen(regimen_dict):

    api_base = 'http://prodmtrain1:5000'
    regimen_list = get_df('regimens', api_base=api_base)['name'].values
    if regimen_dict['name'] in regimen_list:
        raise Exception('Regimen name %s already tracked on server %s' % (regimen_dict['name'], api_base))
