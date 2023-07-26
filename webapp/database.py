# Standard library
import os

# Packages
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


db_engine = create_engine(os.environ["POSTGRESQL_DB_CONNECT_STRING"])
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
)
