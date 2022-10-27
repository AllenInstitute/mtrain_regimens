from __future__ import print_function
import click
import requests
import os
import json
import yaml
import hashlib

def url_preprocessor(url=None, file_type='yaml'):
    
    result = requests.get(url)
    assert result.ok == True
    content = result.content

    if file_type == 'yaml':
        
        content = yaml.load(content, Loader=yaml.Loader)
    elif file_type == "json":
        pass
    else:
        raise

    if not isinstance(content, dict):
        raise Exception('Regimen not found at URL: {url}'.format(url=url))

    return content

api_base = 'http://mtrain:5000/'

@click.command()
@click.option('-r','--regimen',default='',help='Source regimen')
@click.option('--username', prompt=True,
              default=lambda: os.environ.get('USER', ''),
              show_default='current user')
@click.password_option()
@click.option('--dry-run', default=True, help='If `True`,  does not actually migrate subjects, but prints expected migration to screen.', type=bool)
def main(dry_run,username,password,regimen):

    if dry_run==True:
        print("DRY RUN")
    elif dry_run==False:
        print("REAL UPLOAD")
    else:
        raise RuntimeError('Dryrun not in (True, False): {dry_run} ({dry_run_type})'.format(dry_run=dry_run, dry_run_type=type(dry_run)))

    sess = requests.session()
    result = sess.post(api_base, data={'username':username, 'password':password})
    if result.status_code != 200:
        print(result.status_code, result.reason)
        raise Exception()
    else:
        print('Authenticate', result.status_code, 'OK')

    # Add dev regimen:
    regimen_dict = url_preprocessor('https://raw.githubusercontent.com/AllenInstitute/mtrain_regimens/%s/regimen.yml' % regimen)
    if regimen_dict['name'] != regimen:
        raise Exception('Regimen name in regimen.yml (%s) does not match name provided: %s' % (regimen_dict['name'], regimen))
    
    # Double-check regimen stages and transitions match:
    transition_source_target_set = set()
    for t in regimen_dict['transitions']:
        transition_source_target_set.add(t['source'])
        transition_source_target_set.add(t['dest'])
    stage_set = set(regimen_dict['stages'].keys())
    if not all([curr_stage in stage_set for curr_stage in transition_source_target_set]):
        raise Exception('Stages and source/dest of transitions are not consistent')

    if dry_run is False:
        result = sess.post(os.path.join(api_base, "set_regimen/"), data=json.dumps(regimen_dict))
        if result.status_code != 200:
            print(result.status_code, result.reason, result.text)
            raise Exception()
        else:
            print('Add regimen:', result.status_code, 'OK')
    else:
        print(regimen_dict)


if __name__ == '__main__':
    main()
