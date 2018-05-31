import yaml
import os
import hashlib
import warnings
import requests

def test_script_files_download():
    regimen_data = yaml.load(open(os.path.join(os.path.dirname(__file__), '..', 'regimen.yml'), 'r'))

    for stage_name, stage_dict in regimen_data['stages'].items(): 
        if stage_dict['script'] == 'NotImplemented':
            warnings.warn('Stage "%s" Not Implemented' % stage_name)
        else:
            if 'raw' not in stage_dict['script']:
                raise Exception('URL appears to not be a raw file: %s' % stage_dict['script'])
            if len(stage_dict['script'].split('/')[-2]) != 40:
                raise Exception('URL appears to not have a specific hash indicated: %s' % stage_dict['script'])
            result = requests.get(stage_dict['script'])
            if result.status_code != 200:
                raise Exception('Could not reach endpoint: %s' % stage_dict['script'])
                
            else:
                assert hashlib.md5(result.content).hexdigest() == stage_dict['script_md5']
