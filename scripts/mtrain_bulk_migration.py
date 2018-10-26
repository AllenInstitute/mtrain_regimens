import click
import requests
import yaml
import pandas as pd
import os
import json

from utils import get_df, API_BASE

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def parse_regimen_major(regimen_name):
    return '.'.join(regimen_name.split('.')[:-2])


def is_minor_change(source_regimen, target_regimen):
    return parse_regimen_major(source_regimen) == parse_regimen_major(target_regimen)


def get_mapping(source_regimen,target_regimen,migration):
    source = parse_regimen_major(source_regimen)
    target = parse_regimen_major(target_regimen)
    return migration[source][target]


@click.command()
@click.option('-s','--source',default='',help='Source regimen')
@click.option('-t','--target',default='',help='Target regimen')
@click.option('--migration_yml', default=None, help='Path to migration file.')
@click.option('--api-base', default=API_BASE, help='URL for API.')
@click.option('--username', prompt=True,
              default=lambda: os.environ.get('USER', ''),
              show_default='current user')
@click.password_option()
@click.option('--dry-run', default=True, help='If `True`,  does not actually migrate subjects, but prints expected migration to screen.')
def main(dry_run,username,password,source,target,migration_yml,api_base):

    if dry_run==True:
        print("DRY RUN")
    else:
        print("REAL MIGRATION")

    src_regimen = source
    tgt_regimen = target

    if not is_minor_change(src_regimen,tgt_regimen):
        needs_migration = True
        if migration_yml is None:
            dirname = os.path.dirname(__file__)
            migration_yml = os.path.join(dirname,'..','migrations.yml')

        with open(migration_yml,'rb') as f:
            migration = yaml.load(f)
            migration_dict = get_mapping(src_regimen,tgt_regimen,migration)
    else:
        needs_migration = False
        migration_dict = {}

    stages_df = get_df('stages').rename(columns={'id':'stage_id','name':'stage_name'}).drop(['parameters', 'script', 'script_md5', 'states'], axis=1)
    states_df = get_df('states').rename(columns={'id':'state_id'})
    subjects_df = get_df('subjects').rename(columns={'id':'state_id'})
    subjects_df['state_id'] = subjects_df['state'].map(lambda x:x['id'])
    subjects_df.drop(['state'], axis=1, inplace=True)
    stages_states_df = pd.merge(stages_df, states_df, on='stage_id')
    regimens_df = get_df('regimens').rename(columns={'id':'regimen_id','name':'regimen_name'}).drop(['states', 'active'], axis=1)
    stages_states_regimens_df = pd.merge(stages_states_df, regimens_df, on='regimen_id')

    subjects_df = pd.merge(stages_states_regimens_df, subjects_df, on='state_id')


    sess = requests.session()
    sess.post(api_base, data={'username':username, 'password':password})
    df = subjects_df[subjects_df['regimen_name']==src_regimen]

    if len(df)==0:
        print('There are no subjects on regimen "{}"'.format(src_regimen))

    for ii, row in df.iterrows():
        src_stage_name = row['stage_name']
        if needs_migration:
            tgt_stage_name = migration_dict[src_stage_name]
        else:
            tgt_stage_name = src_stage_name
        LabTracks_ID = row['LabTracks_ID']
        if dry_run==True:
            print("%s: %s/%s -> %s/%s" % (LabTracks_ID, src_regimen, src_stage_name, tgt_regimen, tgt_stage_name))
        else:
            result = sess.get('{}/get_state/'.format(api_base), data=json.dumps({'regimen_name':tgt_regimen, 'stage_name':tgt_stage_name}))
            if result.status_code == requests.codes.ok:
                state_dict = result.json()

                result = sess.post('{}/set_state/{}'.format(api_base, LabTracks_ID), data=json.dumps({'state':state_dict}))
                if result.status_code == requests.codes.ok:
                    print("MERGED! %s: %s/%s -> %s/%s" % (LabTracks_ID, src_regimen, src_stage_name, tgt_regimen, tgt_stage_name))
                else:
                    result.raise_for_status()

            else:
                "Uh oh. Can't find that regimen/stage combination."
                result.raise_for_status()


if __name__ == '__main__':
    main()
