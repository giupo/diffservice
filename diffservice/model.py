# -*- coding:utf-8 -*-

import logging
import datetime
import json

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import Text, ForeignKey, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.orm.session import object_session

from applogging import getLogger
from config import config

log = getLogger(__name__)

engine = create_engine(config.get('DB', 'url'),
                       echo=log.level < logging.INFO)
Session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class JsonMixin(object):
    """Export to json a class, given it has a to_dict method"""
    def to_json(self):
        return json.dumps(self.to_dict())


class SQLAlchemyDictView(object):
    """Extract a dict view of an SQLAlchemy Model"""
    def to_dict(self):
        d = {}
        for column in self.__table__.columns:
            obj = getattr(self, column.name)
            if isinstance(obj, datetime.datetime):
                obj = str(obj)
            d[column.name] = obj
        return d

    def update(self, **args):
        for k, v in args.iteritems():
            setattr(self, k, v)

RequestStatus = ('PENDING', 'RUNNING', 'ERROR', 'DONE')
status_enum = Enum(*RequestStatus, name="diff_status")


class DiffRequest(Base, JsonMixin, SQLAlchemyDictView):
    __tablename__ = "diff_request"
    id = Column(Integer, primary_key=True)
    tavola = Column(String, nullable=False)
    A = Column(String, nullable=False)
    B = Column(String, nullable=False)
    soglia = Column(Float, nullable=False, default=0.0)
    who = Column(String, nullable=False)
    when = Column(DateTime, nullable=False,
                  default=datetime.datetime.utcnow)
    status = Column(status_enum, nullable=False, default=RequestStatus[0])

    def __init__(self, **args):
        self.update(**args)

    @property
    def num(self):
        session = object_session(self)
        if session is None:
            raise Exception("No Session is bound")
        return session.query(DiffResult).filter_by(request_id=self.id).count()


class DiffResult(Base, JsonMixin, SQLAlchemyDictView):
    __tablename__ = "diff_results"
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey('diff_request.id'))
    request = relationship("DiffRequest")
    result_json = Column(Text)

    def __init__(self, **args):
        self.update(**args)

    @property
    def result(self):
        if self.result_json is None:
            return None
        else:
            return json.loads(self.result_json)

    @result.setter
    def result(self, value):
        self.result_json = json.dumps(value)


Base.metadata.create_all(engine)
