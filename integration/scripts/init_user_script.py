import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL

from mtrain_api.user.models import User


# TODO pass this down entirely as a container link
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

User.metadata.create_all(engine)

session.add(
    User(
        username=sys.argv[1], 
        password=sys.argv[2], 
        email='whoevencares@email.com', 
        active=True, 
    )
)
session.commit()