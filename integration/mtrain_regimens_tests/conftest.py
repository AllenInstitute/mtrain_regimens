import pytest

 # maybe we want remote logging or something...
 # really i have no idea...
import logging
import os
from random import randint
import requests
import yaml


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
    
    def _resolve_request_finisher(self):
        pass

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
        return self.api_session \
            .post(
                self.mtrain_root + 'set_regimen/',
                data=json.dumps(regimen_dict),
            )
        
    def get_mouse(self, mouse_id):
        return self.api_session \
            .get(
                self.mtrain_root + \
                    'subjects/%s' % mouse_id,
            )

    def set_state(
        self, 
        mouse_id, 
        regimen_id,
        stage_id,
        state_id, 
    ):
        return self.api_session \
            .post(
                self.mtrain_root + \
                    'set_state/%s' % mouse_id,
                data=json.dumps({
                    'id': state_id,
                    'stage_id': stage_id,
                    'regimen_id': regimen_id,
                }),
            )

    def progress(self, mouse_id, behavior_session):
        return self.api_session \
            .post(
                self.mtrain_root + \
                    'set_behavior_session/%s' % \
                    mouse_id,
                data=json.dumps(behavior_session),
            )
        
    

        
        
        


@pytest.fixture(
    scope='module',
    params=[
        {
            'username': \
                os.environ['MTRAIN_TEST_USERNAME'], 
            'password': \
                os.environ[''], 
        },
    ],
    ids=[
        'u:wut, p:did',
    ]
)
def mtrain_client(request):
    return MtrainClient(
        usernamerequest.param['username']
    )
    

@pytext.fixture(
    scope='module',
    params=[],
    ids=[],
)
def mouse_fixture(request, mtrain_client):
    max_attempts = 10
        for i in range(max_attempts):
            try:
                mid = randint(100000, 999999)
                session_fixture.post(
                    'http://localhost:5000',

                )
                return {
                    "id": mid, 
                }
        except:
            logging.info(
                'failed to make new mouse: %s' mid
            )
    else:
        logging.error('exceeded max attempts: %s' % max_attempts)
        raise Exception('exceeded max attempts: %s' % max_attempts)


@pytest.fixture(
    scope='module', 
    params=[
        {
            'mouse_id'
        }
    ], 
    ids=['dumb mouse', 'smart mouse', ],
)
def progression_fixture(request, session_fixture):
    # use session fixture to make mouse at certain stage
    # then use sess.post to progress it
    session_fixture.post(
        'http://localhost:5000/add_subject/{}' \
            .format(mouse_id),
        
    )