from .utils import load_regimen

regimen_data = load_regimen()

def test_stage_name_in_params():
    for stage_name, stage_dict in regimen_data['stages'].items():
        stage_param = stage_dict['parameters']['stage']
        assert stage_param==stage_name, "stage: {}, param: {}".format(stage_name,stage_param)
