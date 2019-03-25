import pytest

 # maybe we want remote logging or something...
 # really i have no idea...
import logging
import os
import pandas as pd
from random import randint
import requests
import uuid
import yaml

from visual_behavior.translator.core import create_extended_dataframe
from visual_behavior.schemas.extended_trials import ExtendedTrialSchema
from visual_behavior.translator.foraging2 import data_to_change_detection_core


MTRAIN_USERNAME = os.environ['MTRAIN_USERNAME']
MTRAIN_PASSWORD = os.environ['MTRAIN_PASSWORD']
MTRAIN_ROOT = os.environ['MTRAIN_ROOT']
TRAINING_OUTPUT = os.environ['TRAINING_OUTPUT']

# is this code structure great for easy reading in
# version control? i often code alone so i really have
# no idea..
class MtrainClient(object):
    """embedded because i prefer less files to look at...
    """
    @property
    def api_session(self):
        return self.__api_session

    @property
    def mtrain_root(self):
        return self.__mtrain_root
    
    def __init__(
        self, 
        username, 
        password, 
        mtrain_root,
    ):  
        self.__mtrain_root = mtrain_root
        self.__api_session = requests.Session()
    
        # authenticate user
        response = self.api_session.post(
            self.mtrain_root,
            data={
                'username': username,
                'password': password,
            }
        )
        
        if response.status_code != 200:
            response.raise_for_status()

    def create_mouse(self, mouse_id, initial_state):
        return self.api_session \
            .post(
                self.mtrain_root + 'add_subject/',
                {
                    'LabTracks_ID': mouse_id, 
                    'initial_state': initial_state,
                },
            )

    def create_regimen(self, regimen_dict):
        response = self.api_session \
            .post(
                self.mtrain_root + 'set_regimen/',
                data=json.dumps(regimen_dict),
            )
        
        if response.status_code != 200:
            response.raise_for_status()

        return response

    def get_regimen(self, regimen_id, join=True):
        response = self.api_session \
            .get(
                self.mtrain_root + \
                    'regimens/%s' % regimen_id
            )
        
        if response.status_code != 200:
            response.raise_for_status()

        regimen = response.json()
        if join:
            for state in regimen['states']:
                state.update(
                    self.get_state(state['id'])
                )

        return regimen

    def get_mouse(self, mouse_id, join=True):
        response = self.api_session \
            .get(
                self.mtrain_root + \
                    'subjects/%s' % mouse_id,
            )

        if response.status_coe != 200:
            response.raise_for_status()

        mouse_meta = response.json()

        if join:  # shared path thru code == better with less testing?
            mouse_meta['state'].update(
                self.get_state(
                    response['state']['id'],
                    join=True,  # one of two possible contracts to have with get_state...other relies on join default not changing...
                ),
            )  # update pointer with resolved object, we represent json as dict
        
        return mouse_meta

    def get_state(
        self,
        state_id, 
        join=True,
    ):
        """get mtrain's state
        """
        if join:
            response = self.api_session + \
                'join/states/%s' % state_id \
                .get()
        else:
            response = self.api_session + \
                'states/%s' % state_id \
                .get()
        
        if response.status_code != 200:
            response.raise_for_status()

        return response.json()

    def get_stage(
        self, 
        mouse_id,
    ):
        return self.get_mouse(mouse_id, join=True)['stage']

    def set_stage(
        self, 
        mouse_id, 
        stage_name,
    ):
        mouse_meta = self.get_mouse(mouse_id, join=False)
        regimen = self.get_regimen(
            mouse_meta['state']['regimen_id'],
            join=True,
        )
        
        matches = filter(
            lambda state: state['stage']['name'] == stage_name, 
            regimen['states'],
        )

        # use only values from the match just incase...        
        return self.set_state(
            mouse_id=mouse_id,
            regimen_id=matches[0]['regimen']['id'],
            stage_id=matches[0]['stage']['id'],
            state_id=matches[0]['id'],
        )

    def set_state(
        self, 
        mouse_id, 
        regimen_id,
        stage_id,
        state_id, 
    ):
        response = self.api_session \
            .post(
                self.mtrain_root + \
                    'set_state/%s' % mouse_id,
                data=json.dumps({
                    'id': state_id,
                    'stage_id': stage_id,
                    'regimen_id': regimen_id,
                }),
            )
        
        if response.status_code != 200:
            response.raise_for_status()
        
        return response.json()

    def progress(self, mouse_id, behavior_session):
        response = self.api_session \
            .post(
                self.mtrain_root + \
                    'set_behavior_session/%s' % \
                    mouse_id,
                data=json.dumps(behavior_session),
            )
        
        if response.status_code != 200:
            response.raise_for_status()
        
        return response.json()


@pytest.fixture(scope='module')
def regimen(mtrain_client):
    with open('../assets/regimen.yml', 'r') as rstream:
        response = mtrain_client.create_regimen(
            yaml.load(rstream.read()),
        )

    if response != 200:
        reponse.raise_for_status()
    
    return regimen.json()


@pytest.fixture(scope='module')  # hopefully we dont accidentally cause a sideeffect?
def behavior_session_base():
    core = data_to_change_detection_core(
        pd.read_pickle(TRAINING_OUTPUT),
    )
    return create_extended_dataframe(
        trials=core_data['trials'],
        metadata=core_data['metadata'],
        licks=core_data['licks'],
        time=core_data['time'],
    )


@pytest.fixture(
    scope='module',
)
def mtrain_client(request):
    return MtrainClient(
        username=MTRAIN_USERNAME,
        password=MTRAIN_PASSWORD,
        mtrain_root=MTRAIN_ROOT,
    )


@pytest.mark.fixture(
    scope='function',
)
def mouse_factory(mtrain_client):
    def wrapped_mouse_factory(initial_state):
        # its always random, ill build the non-random some other time?
        max_attempts = 15
        for _ in range(max_attempts):
            return mtrain_client \
                .create_mouse(
                    mouse_id=str(randint(100000, 999999)),
                    initial_state=initial_state,
                )
        else:
            raise Exception(
                'exceeded max attempts: %s' % max_attempts,
            )

    return wrapped_mouse_factory


progression_ids = []
progression_params = []
for config_name in os.listdir('./progressions'):
    config_path = os.path.join(
        './progressions', 
        config_name,
    )
    with open(config_path, 'r', ) as pstream:
        progression_ids.append(config_name)
        progression_params.append(
            yaml.load(pstream.read()),
        )


def resolve_epoch_bound(value, n_trials):
    if isinstance(value, int) or \
            isinstance(value, float):
        return value
    elif isinstance(value, basestring):
        if value == 'start':
            return 0
        elif value == 'middle':
            return n_trials / 2
        elif value == 'end':
            return n_trials
    else:
        raise ValueError(
            'unsupported epoch value type: {}' \
                .format(type(value)),
        )


@pytest.fixture(
    scope='function',
    ids=progression_ids,
    params=progression_params,
)
def progression_plan(
    mouse_factory,
    mtrain_client,
    request,
    behavior_session_base,
):
    initial_state = request.param['initial_state']
    mouse_meta = mouse_factory(
        initial_state=initial_state,
    )
    
    progression_plan = {
        'mouse_meta': mouse_meta,
        'initial_state': initial_state,
        'progressions': []
    }
    for progression_dict in request.param['progressions']:
        progression = {
            'start_state': \
                progression_dict['start_state'],
            'end_state': \
                progression_dict['end_state'],
        }

        behavior_session = behavior_session_base \
            .copy(deep=True)
        behavior_session_base['mouse_id'] = \
            mouse_meta['LabTracks_ID']
        behavior_session_base['behavior_session_uuid'] = \
            uuid.uuid4()
        for epoch in progression_dict['epochs']:
            idx_start = resolve_epoch_bound(
                epoch['start'], 
                len(behavior_session),  # n_trials
            )
            idx_end = resolve_epoch_bound(
                epoch['end'], 
                len(behavior_session),  # n_trials
            )

            for (name, override) in epoch['overrides'].items():
                getattr(behavior_session, name, ) \
                    .iloc[idx_start:idx_end] = override
            
            schema = ExtendedTrialSchema()
            data_list_cs = behavior_session\
                .to_dict('records')
            data_list_cs_sc = schema.dump(
                data_list_cs, 
                many=True,
            )
            progression['behavior_session'] = \
                json.dumps({
                    'data_list': data_list_cs_sc, 
                })
            
            progression_plan['progressions'] \
                .append(progression)
    
    return progression_plan