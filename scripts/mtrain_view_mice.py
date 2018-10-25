from __future__ import print_function
import pandas as pd
import click
from utils import get_df

# pd.set_option('display.height', 1000)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

@click.command()
def main():
    stages_df = get_df('stages').rename(columns={'id':'stage_id','name':'stage_name'}).drop(['parameters', 'script', 'script_md5', 'states'], axis=1)
    states_df = get_df('states').rename(columns={'id':'state_id'})
    subjects_df = get_df('subjects').rename(columns={'id':'state_id'})
    subjects_df['state_id'] = subjects_df['state'].map(lambda x:x['id'])
    subjects_df.drop(['state'], axis=1, inplace=True)
    stages_states_df = pd.merge(stages_df, states_df, on='stage_id')
    regimens_df = get_df('regimens').rename(columns={'id':'regimen_id','name':'regimen_name'}).drop(['states', 'active'], axis=1)
    stages_states_regimens_df = pd.merge(stages_states_df, regimens_df, on='regimen_id')

    # print stages_states_regimens_df

    # print subjects_df
    subjects_df = (
        pd
        .merge(stages_states_regimens_df, subjects_df, on='state_id')
        .sort_values('LabTracks_ID')
        .set_index('LabTracks_ID')
    )[['regimen_name','stage_name','regimen_id','stage_id','state_id']]

    print(subjects_df)

# # stages_df

# data = requests.get('http://prodmtrain1:5000/api/v1/training/subjects/%s' % LabTracks_ID)
# performance_df = pd.DataFrame(data.json()['behavior_sessions'])
# performance_df = pd.merge(stages_states_regimens_df, performance_df, on='state_id').sort_values('date')
# print(performance_df)



# stages_df.drop(['states', 'regimen_id', 'active', 'id', 'id_x', 'id_y'], axis=1, inplace=True)
# print(stages_df)





# # print(stages_df.columns)
# # print(performance_df.columns)



# print(df.columns)

# df.drop(['parameters', 'script', 'script_md5', 'states', 'state_id', 'id_x'], axis=1, inplace=True)
# print(df)


# df =

# df = pd.DataFrame(data.json()['behavior_sessions']).sort_values('date')


# from visual_behavior.translator.core import create_extended_dataframe
# from visual_behavior.schemas.extended_trials import ExtendedTrialSchema
# from visual_behavior.translator.foraging2 import data_to_change_detection_core
# import pandas as pd

# foraging_file_name = '/allen/aibs/mpe/Software/data/behavior/validation/stage_0/doc_gratings_7385e99_PerfectDoCMouse.pkl'
# # foraging_file_name = "/allen/programs/braintv/production/neuralcoding/prod0/specimen_652074249/behavior_session_702124059/180524160051_362201_a3bf7453-a9d9-42f6-9500-fea38f0a2700.pkl"
# # foraging_file_name = "/allen/programs/braintv/production/neuralcoding/prod0/specimen_651725156/behavior_session_703485615/180530092658_363894_81c53274-e9c7-4b94-b51d-78c76c494e9d.pkl"


# data = pd.read_pickle(foraging_file_name)
# core_data = data_to_change_detection_core(data)
# df = create_extended_dataframe(trials=core_data['trials'],metadata=core_data['metadata'],licks=core_data['licks'],time=core_data['time'],)

# print core_data.keys()


# from visual_behavior.translator.foraging2 import data_to_change_detection_core
# from visual_behavior.validation.qc import generate_qc_report


# foraging_file_name = '/allen/aibs/mpe/Software/data/behavior/validation/stage_0/doc_gratings_7385e99_PerfectDoCMouse.pkl'

# data = pd.read_pickle(foraging_file_name)
# core_data = data_to_change_detection_core(data)
# results = generate_qc_report(core_data)

# for key, val in results.items():
#     print key, val





# import glob
# import json
# import pandas as pd

# for fname in list(glob.glob('/allen/programs/braintv/production/neuralcoding/*/*/*/UPLOAD_TO_MTRAIN_QUEUE_*_output.json')):
#     input_data = json.load(open(fname, 'r'))
#     pname = input_data['input_parameters']['foraging_file_name']
#     data  = pd.read_pickle(pname)
#     print data['platform_info']['camstim'], input_data['status_code'], input_data['text']
# import pandas as pd
# import uuid

# from visual_behavior.translator.core import create_extended_dataframe
# from visual_behavior.translator.core import df_to_json
# from visual_behavior.translator import foraging2
# from visual_behavior.validation.extended_trials import validate_schema
# from visual_behavior.schemas.extended_trials import ExtendedTrialSchema


# foraging_file_name = '/allen/programs/braintv/production/neuralcoding/prod0/specimen_653517588/behavior_session_701073774/180523094628_363140_bd672473-d9ab-400c-828a-4f04cbb01e34.pkl'
# data = pd.read_pickle(foraging_file_name)
# core_data = foraging2.data_to_change_detection_core(data)

# df = create_extended_dataframe(
#     trials=core_data['trials'],
#     metadata=core_data['metadata'],
#     licks=core_data['licks'],
#     time=core_data['time'],
# )

# df['behavior_session_uuid'] = str(uuid.uuid4())

# ets = ExtendedTrialSchema()
# yy = df.to_dict('records')[:1]
# y = ets.dumps(yy, many=True)
# print y.errors
# print type(yy[0]['date'])
# z = ets.loads(y.data, many=True)
# print ets.validate(z, many=True)

if __name__ == '__main__':
    main()
