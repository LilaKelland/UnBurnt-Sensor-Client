# from sqlalchemy import create_engine, orm
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# engine = create_engine('sqlite:///unburnt.db')
# # engine = create_engine('postgresql://usr:pass@localhost:5432/sqlalchemy')
# Session = sessionmaker(bind=engine)

# Base = declarative_base()
# Base.metadata.create_all(engine)

from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as db

Base = declarative_base()
engine = db.create_engine("sqlite:///unburnt.db")
Base.metadata.bind = engine
Session = orm.scoped_session(orm.sessionmaker())(bind=engine)
