import pytest
import requests


@pytest.fixture
def session_fixture():
    sess = ()
    # send init user script, 
    # we do it here so we can wait for the init, 
    # etc obviously not best practices but maybe best for our current solution


@pytest.fixture(scope='module', params=[])
def training_history_fixture():
    pass