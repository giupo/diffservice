# -*- coding:utf-8 -*-

import logging
import datetime
import json

from applogging import getLogger
log = getLogger(__name__)

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import Text, ForeignKey, Boolean, Float
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.session import object_session

from config import config

engine = create_engine(config.get('DB', 'url'),
                       echo=log.level < logging.INFO)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class JsonMixin(object):
    """Export to json a class, given it has a to_dict method"""
    def to_json(self):
        return json.dumps(self.to_dict())


class SQLAlchemyDictView(object):
    """Extract a dict view of an SQLAlchemy Model"""
    def to_dict(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        return d


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
