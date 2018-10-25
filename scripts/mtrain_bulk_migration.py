import click
import requests
import pandas as pd
import os
import json

from utils import get_df

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

api_base = 'http://mtrain:5000/'

@click.command()
@click.option('-s','--source',default='',help='Source regimen')
@click.option('-t','--target',default='',help='Target regimen')
@click.option('--username', prompt=True,
              default=lambda: os.environ.get('USER', ''),
              show_default='current user')
@click.password_option()
@click.option('--dry-run', default=True, help='If `True`,  does not actually migrate subjects, but prints expected migration to screen.')
def main(dry_run,username,password,source,target):

    if dry_run==True:
        print("DRY RUN")
    else:
        print("REAL MIGRATION")
    # dry_run = False

    # src_regimen = 'v0.1.3'
    # tgt_regimen = 'VisualBehavior_Task1A_v0.2.3'

    src_regimen = source # 'VisualBehavior_Task1A_v0.2.2'
    tgt_regimen = target # 'VisualBehavior_Task1A_v0.3.1'

    # migration_dict = {
    #     "1_AutoRewards": "0_gratings_autorewards_15min",
    #     "static_full_field_gratings": "1_gratings",
    #     "static_full_field_gratings_flash_500ms": "2_gratings_flashed",
    #     "natural_images": "3_images_a_10uL_reward",
    #     "natural_images_drop_reward": "4_images_a_training",
    #     "ready_for_imaging": "4_images_a_handoff_ready",
    #     "not_ready_for_imaging": "4_images_a_handoff_lapsed",
    #     "ophys_A": "5_images_a_ophys",
    # }

    # migration_dict_rev = {}
    # for key, val in migration_dict.items():
    #     migration_dict_rev[val] = key


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
        tgt_stage_name = src_stage_name #migration_dict[src_stage_name]
        LabTracks_ID = row['LabTracks_ID']
        if dry_run==True:
            print("%s: %s/%s -> %s/%s" % (LabTracks_ID, src_regimen, src_stage_name, tgt_regimen, tgt_stage_name))
        else:
            result = sess.get(os.path.join(api_base, 'get_state/'), data=json.dumps({'regimen_name':tgt_regimen, 'stage_name':tgt_stage_name}))
            if result.status_code == requests.codes.ok:
                state_dict = result.json()

                result = sess.post(os.path.join(api_base, 'set_state/%s' % LabTracks_ID), data=json.dumps({'state':state_dict}))
                if result.status_code == requests.codes.ok:
                    print("MERGED! %s: %s/%s -> %s/%s" % (LabTracks_ID, src_regimen, src_stage_name, tgt_regimen, tgt_stage_name))
                else:
                    result.raise_for_status()

            else:
                result.raise_for_status()


if __name__ == '__main__':
    main()
