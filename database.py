from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import simplejson

engine = create_engine('sqlite:///resumes.sqlite')

db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

class Resume(Base):
    __tablename__ = 'resumes'
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    gender = Column(Integer)
    age = Column(Integer)
    has_degree = Column(Boolean)
    city = Column(String(50))
    keywords = Column(String)
    url = Column(String(10000), unique=True)

    @property
    def keywords_list(self):
        return simplejson.loads(self.keywords)

    def __init__(self, title=None, gender=None,
                 age=None, has_degree=None, 
                 city=None, keywords=None,
                 url=None):
        self.title = title
        self.gender = gender
        self.age = age
        self.has_degree = has_degree
        self.city = city
        self.keywords = keywords
        self.url = url
   

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
