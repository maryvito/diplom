from database import Resume
import simplejson
from sait import read_data_from_json
from database import db_session
import json
# from sqlalchemy import create_engine
# from sqlalchemy import Column, Integer, String, Boolean
# from sqlalchemy.orm import scoped_session, sessionmaker
# from sqlalchemy.ext.declarative import declarative_base

def put_data_in_base(fileName):
    resume_list = read_data_from_json(fileName)
    for resume in resume_list:
        if resume['gender'] == 'male':
            gender = 1
        else:
            gender = 0
        r = Resume(resume['title'], gender, resume['age'], resume['has_degree'], resume['city'], json.dumps(resume['keywords']), resume['url'])
        db_session.add(r)
    db_session.commit()

put_data_in_base('data.json')

