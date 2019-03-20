import datetime
import json
import os
import requests
import pandas as pd
import uuid

from visual_behavior.utilities import get_response_rates

from mtrain_api.app import create_app, db
from mtrain_api.user.models import User
from mtrain_api.utils import url_preprocessor
from mtrain_api.settings import TestConfig

from visual_behavior.translator.core import create_extended_dataframe
from visual_behavior.schemas.extended_trials import ExtendedTrialSchema
from visual_behavior.translator.foraging2 import data_to_change_detection_core

def create_mock_session(overrides):
    return


def create_transcript(transcript):
    meta = transcript.get('meta')
    session_overrides = transcript.get('session_overrides', [])