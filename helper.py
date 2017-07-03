import simplejson
import json

from database import db_session
from database import Resume


def put_data_in_base(file_name):
    resume_list = read_data_from_json(file_name)
    for resume in resume_list:
        if resume['gender'] == 'male':
            gender = 1
        else:
            gender = 0
        resume = Resume(resume['title'], gender, resume['age'],
                   resume['has_degree'], resume['city'],
                   json.dumps(resume['keywords']), resume['url'])
        db_session.add(resume)
    db_session.commit()


def read_data_from_json(file_name):
    with open(fileName, 'r') as file_handler:
        return simplejson.loads(file_handler.read())


def read_all_keywords_from_resumes():
    resumes = Resume.query.all() 
    all_keywords = []
    for res in resumes:
        res_keyword_as_list = res.keywords[2:-2].split('\", \"')

        for keyword in res_keyword_as_list:

            if keyword not in all_keywords:
                all_keywords.append(keyword)
    return all_keywords


ALL_KEYWORDS = read_all_keywords_from_resumes()




    


