from .utils import load_regimen

regimen_data = load_regimen()

def test_stage_name_in_params():
    for stage_name, stage_dict in regimen_data['stages'].items():
        assert stage_dict['parameters']['stage']==stage_name, stage_name 
