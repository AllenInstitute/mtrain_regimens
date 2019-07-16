import pytest

 # maybe we want remote logging or something...
 # really i have no idea...
import glob
import json
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

# py2 & 3 compat
try:
    basestring = basestring
except NameError:
    basestring = str

# from .progressions import progressions


# configurable
MTRAIN_USERNAME = os.environ['MTRAIN_USERNAME']
MTRAIN_PASSWORD = os.environ['MTRAIN_PASSWORD']
MTRAIN_ROOT = os.environ['MTRAIN_ROOT']


# not
TEST_ROOT = os.path.dirname(os.path.abspath(__file__))
REGIMEN_YML = os.path.join(TEST_ROOT, './assets/regimen.yml', )
TRAINING_OUTPUTS = glob.glob(os.path.join(TEST_ROOT, './assets/*.pkl', ))
PROGRESSION_YMLS = glob.glob(os.path.join(TEST_ROOT,'./progressions/*.yml'))
MANUAL_YMLS = glob.glob(os.path.join(TEST_ROOT,'./manual/*.yml'))

# utils
def resolve_epoch_bound(value, n_trials):
    if isinstance(value, int):
        return value
    elif isinstance(value, basestring):
        if value == 'start':
            return 0
        elif value == 'middle':
            return n_trials // 2
        elif value == 'end':
            return n_trials
    else:
        raise ValueError(
            'unsupported epoch value type: {}' \
                .format(type(value)),
        )


# mtrain api client
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
        self.__api_session = requests.session()
        # always raise for status if we dont get 200
        # self.api_session.hooks['response'].append(
        #     lambda r, *args, **kwargs: r.raise_for_status(),
        # )
    
        # authenticate user
        print(username, password)
        response = self.api_session.post(
            'http://localhost:5000',
            data={
                'username': username,
                'password': password,
            }
        )
        
        if response.status_code != 200:
            response.raise_for_status()

    def create_mouse(self, mouse_id, initial_state):
        response = self.api_session \
            .post(
                self.mtrain_root + 'add_subject/',
                data=json.dumps({
                    'LabTracks_ID': mouse_id, 
                    'state': initial_state,
                }),
            )
        
        if response.status_code != 200:
            response.raise_for_status()

        return {
            'LabTracks_ID': mouse_id, 
            'state': initial_state,
        }  # the route doesnt return json

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
                    'api/v1/' + \
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

    def get_regimen_from_name(self, name):
        response = self.api_session \
            .get(self.mtrain_root + 'api/v1/' + 'regimens')
        
        if response.status_code != 200:
            response.raise_for_status()
        
        for regimen_pointer in response.json()['objects']:
            if regimen_pointer['name'] == name:
                return regimen_pointer
        else:
            raise Exception('regimen: %s not found' % name)


    def get_mouse(self, mouse_id, join=True):
        response = self.api_session \
            .get(
                self.mtrain_root + \
                    'api/v1/subjects/%s' % mouse_id,
            )

        if response.status_code != 200:
            response.raise_for_status()

        mouse_meta = response.json()

        if join:  # shared path thru code == better with less testing?
            mouse_meta['state'].update(
                self.get_state(
                    mouse_meta['state']['id'],
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
            response = self.api_session \
                .get(
                    self.mtrain_root + \
                        'api/v1/join/states/%s' % state_id
                )
        else:
            response = self.api_session \
                .get(
                    self.mtrain_root + \
                        'api/v1/states/%s' % state_id
                )
        
        if response.status_code != 200:
            response.raise_for_status()

        return response.json()

    def get_state_from_stage(
        self,
        regimen_name,
        stage_name,
    ):
        response = self.api_session \
            .get(
                self.mtrain_root + 'get_state/',
                data=json.dumps({
                    'regimen_name': regimen_name,
                    'stage_name': stage_name,
                })
            )

        if response.status_code != 200:
            response.raise_for_status()
        
        return response.json()

    def get_stage(
        self, 
        mouse_id,
    ):
        mouse_meta = self.get_mouse(
            mouse_id, 
            join=True, 
        )
        return mouse_meta['state']['stage']

    def set_stage(
        self, 
        mouse_id, 
        stage_name,
    ):
        mouse_meta = self.get_mouse(
            mouse_id, 
            join=False,
        )
        regimen = self.get_regimen(
            mouse_meta['state']['regimen_id'],
            join=True,
        )
        
        matches = list(filter(
            lambda state: state['stage']['name'] == stage_name, 
            regimen['states'],
        ))

        if not len(matches) > 0:
            raise Exception(
                'stage: {} not found for mouse_id: {}' \
                    .format(stage_name, mouse_id, )
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
        print(mouse_id, regimen_id, stage_id, state_id)
        response = self.api_session \
            .post(
                self.mtrain_root + \
                    'set_state/%s' % mouse_id,
                data=json.dumps({
                    "state": {
                        'id': state_id,
                        'stage_id': stage_id,
                        'regimen_id': regimen_id,
                    },
                }),
            )
        
        if response.status_code != 200:
            response.raise_for_status()
        
        # return response.json()  # doesnt return json response :(

    def progress(self, mouse_id, behavior_session):
        print('progres', 'mouse_id')
        response = self.api_session \
            .post(
                self.mtrain_root + 'set_behavior_session/',
                data=json.dumps(behavior_session),
            )
        
        if response.status_code != 200:
            response.raise_for_status()
        
        return response.json()


@pytest.fixture(scope='module')
def mtrain_client(request):
    return MtrainClient(
        username=MTRAIN_USERNAME,
        password=MTRAIN_PASSWORD,
        mtrain_root=MTRAIN_ROOT,
    )


@pytest.fixture(scope='module')
def regimen(mtrain_client):
    with open(REGIMEN_YML, 'r') as rstream:
        regimen_dict = yaml.load(rstream.read())
    
    try:
        mtrain_client.create_regimen(
            regimen_dict,
        )
    except:
        pass
    
    return mtrain_client.get_regimen(
        mtrain_client.get_regimen_from_name(regimen_dict['name'])['id'],
        join=True,
    )


@pytest.fixture(scope='module')  # hopefully we dont accidentally cause a sideeffect?
def behavior_session_base():
    core = data_to_change_detection_core(
        pd.read_pickle(TRAINING_OUTPUTS[0]),  # just use one for now...somehow couple it with progressions
    )
    return create_extended_dataframe(
        trials=core['trials'],
        metadata=core['metadata'],
        licks=core['licks'],
        time=core['time'],
    )


@pytest.fixture(scope='function')
def mouse_factory(mtrain_client):
    def wrapped_mouse_factory(initial_state):
        # its always random, ill build the non-random some other time?
        max_attempts = 15
        for _ in range(max_attempts):
            try:
                mouse_id = str(randint(100000, 999999))
                # print(mouse_id, initial_state)
                return mtrain_client \
                    .create_mouse(
                        mouse_id=mouse_id,
                        initial_state=initial_state,
                    )
            except Exception as e:
                raise e
        else:
            raise Exception(
                'exceeded max attempts: %s' % max_attempts,
            )

    return wrapped_mouse_factory


progression_ids = []
progression_params = []
for config_path in PROGRESSION_YMLS:
    with open(config_path, 'r', ) as pstream:
        progression_ids.append(
            os.path.basename(config_path)
        )
        progression_params.append(
            yaml.load(pstream.read()),
        )


@pytest.fixture(
    scope='function',
    ids=progression_ids,
    params=progression_params,
)
def progression_plan(
    mouse_factory,
    mtrain_client,
    regimen,
    request,
    behavior_session_base,
):
    initial_stage = request.param['initial_stage']
    initial_state = mtrain_client.get_state_from_stage(
        regimen_name=regimen['name'],
        stage_name=initial_stage,
    )
    
    mouse_meta = mouse_factory(
        initial_state=initial_state,
    )
    
    progression_plan = {
        'mouse_meta': mouse_meta,
        'initial_stage': initial_stage,
        'progressions': [],
    }
    for progression_dict in request.param['progressions']:
        progression = {
            'start_stage': \
                progression_dict['start_stage'],
            'end_stage': \
                progression_dict['end_stage'],
        }

        behavior_session = behavior_session_base \
            .copy(deep=True)
        behavior_session['mouse_id'] = \
            mouse_meta['LabTracks_ID']
        behavior_session['behavior_session_uuid'] = \
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
            {
                'data_list': data_list_cs_sc, 
            }
        
        progression_plan['progressions'] \
            .append(progression)
    
    return progression_plan


manual_transition_ids = []
manual_transition_params = []
for config_path in MANUAL_YMLS:
    with open(config_path, 'r', ) as pstream:
        manual_transition_ids.append(
            os.path.basename(config_path)
        )
        manual_transition_params.append(
            yaml.load(pstream.read()),
        )


@pytest.fixture(
    scope='function',
    ids=manual_transition_ids,
    params=manual_transition_params,
)
def manual_transition(
    mouse_factory,
    mtrain_client,
    regimen,
    request,
    behavior_session_base,
):
    initial_stage = request.param['initial_stage']

    initial_state = mtrain_client.get_state_from_stage(
        regimen_name=regimen['name'],
        stage_name=initial_stage,
    )

    mouse_meta = mouse_factory(
        initial_state=initial_state,
    )

    return {
        'mouse_meta': mouse_meta,
        'initial_stage': initial_stage,
        'transitions': [
            transition
            for transition in request.param['transitions']
        ],
    }