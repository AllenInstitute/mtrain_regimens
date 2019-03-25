# integration test runner written in python to coordinate 
# timing and intricate stuff? lel...
# no idea why this code looks so weird...~.~
import shutil
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


def init():
    # make a copy of the regimen for the tests
    _, regimen_yml = mkstemp(
        suffix='.yml',
        dir='./assets',
    )
    
    with open('../regimen.yml', 'r') as src, \
            open(regimen_yml, 'w') as dest:
        dest.write(src.read())

    return {
        'regimen_yml': regimen_yml, 
    }


def init_user(
    username, 
    password, 
    mtrain_api_container,
):
    _, vector_script, = mkstemp(
        suffix='.py',
        dir='./assets',
    )

    with open(vector_script, 'w') as fstream:
        fstream.write(
            INIT_USER_SCRIPT_TEMPLATE.format(
                username=username,
                password=password,
            )
        )
    
    subprocess.run([
        'docker cp {target} {dest}'.format(
            target=vector_script,
            dest='%s:/home/mtrain/app/mtrain_api' % \
                mtrain_api_container,
        ),
    ], check=True, shell=False, )

    subprocess.run([
        'docker exec {container_name} {command}'.format(
            container_name=mtrain_api_container,
            command='python %s' % vector_script,
        ),
    ], check=True, shell=False, )


def run_tests():
    subprocess.run([
        'pytest ./mtrain_regimens_tests',
    ], check=True, shell=False, )  # inherit parent process context


if __name__ == "__main__":
    import os

    meta = init()
    init_user( 
        username=os.environ['MTRAIN_USERNAME'], 
        password=os.environ['MTRAIN_PASSWORD'], 
        mtrain_api_container=os.environ['MTRAIN_CONTAINER_ID'],
    )

    # so we know where the regimen file is
    os.environ['MTRAIN_REGIMEN_YML'] = \
        meta['regimen_yml']
    
    run_tests()