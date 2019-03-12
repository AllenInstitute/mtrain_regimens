
def test_stage_name_in_params(regimen_dict):
    for stage_name, stage_dict in regimen_dict['stages'].items():
        stage_param = stage_dict['parameters']['stage']
        assert stage_param==stage_name, "stage: {}, param: {}".format(stage_name,stage_param)

def test_transitions_stages_match(regimen_dict):

    # Double-check regimen stages and transitions match:
    transition_source_target_set = set()
    for t in regimen_dict['transitions']:
        transition_source_target_set.add(t['source'])
        transition_source_target_set.add(t['dest'])
    stage_set = set(regimen_dict['stages'].keys())
    if not all([curr_stage in stage_set for curr_stage in transition_source_target_set]):
        raise Exception('Stages and source/dest of transitions are not consistent')