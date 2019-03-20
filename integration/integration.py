# integration test runner written in python to coordinate 
# timing and intricate stuff? lel...
# no idea why this code looks so weird...~.~
import subprocess
from tempfile import mkstemp


INIT_USER_SCRIPT_TEMPLATE = \
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL

from mtrain_api.user.models import User


engine = create_engine(URL(
    'postgresql',
    username='postgres',
    password='postgres',
    port=5432,
    database='mtrain_test',
    host='postgres_testdb'
))

Session = sessionmaker(bind=engine)

session = Session()

session.add(
    User(
        username='{username}', 
        password='{password}', 
        email='whoevencares@email.com', 
        active=True, 
    )
)
session.commit()
"""


# def init_services():
#     subprocess.call([
#         'docker-compose -f docker-compose.yml -p regimentest up'
#     ])


def init_user(
    username, 
    password, 
    mtrain_api_container,
):
    # how get username, password into file?
    _, temp, = mkstemp(
        suffix='.py',
        dir='./temp',
    )

    with open(temp, 'w') as fstream:
        fstream.write(
            INIT_USER_SCRIPT_TEMPLATE.format(
                username=username,
                password=password,
            )
        )
    
    subprocess.call([
        (
            'docker cp '
            '{temp} ' 
            '{mtrain_api_container}:/home/mtrain/app/mtrain_api'
        ).format(
            temp=temp,
            mtrain_api_container=mtrain_api_container,
        ),
        (
            'docker exec ',
            '{mtrain_api_container} '
            'python {temp}'
        ).format(
            temp=temp,
            mtrain_api_container=mtrain_api_container,
        )
    ])


def run_tests(username, password):
    # use environment variables to pass in username, password
    result = subprocess.call([
        'export MTRAIN_API_USERNAME={}'.format(username),
        'export MTRAIN_API_PASSWORD={}'.format(password),
        'pytest ./mtrain_regimens_tests',
    ])  # inherit parent process context


if __name__ == "__main__":
    import time

    CONTAINER_NAME = 'regimentest_mtrain_api_1'
    USERNAME = 'wut'
    PASSWORD = 'did'

    init_user(
        username=USERNAME, 
        password=PASSWORD, 
        mtrain_api_container=CONTAINER_NAME,
    )

    time.sleep(5)

    run_tests(
        username=USERNAME, 
        password=PASSWORD,
    )