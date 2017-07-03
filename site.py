import simplejson

from flask import Flask, render_template, request

from database import Resume
from helper import ALL_KEYWORDS
from parse_superjob import get_resume_from_superjob_and_parse_it

APP = Flask(__name__)


@APP.route('/')
def index():
    resumes = Resume.query.all() 
     
    return render_template('index.html', resumes=resumes, all_keywords=ALL_KEYWORDS) 


@APP.route('/selected_resumes_keywords/', methods=['POST'])
def select_resumes_by_keywords():

    resumes = Resume.query.all() 
    selected_keywords = request.form.getlist('keywords')

    selected_resumes = []
    for res in resumes:
        resume_keywords = simplejson.loads(res.keywords)
        if set(resume_keywords) >= set(selected_keywords):
            selected_resumes.append(res)    
                
    return render_template('selected_resumes_keywords.html',
                            selected_resumes=selected_resumes,
                            all_keywords=ALL_KEYWORDS)


@APP.route('/selected_resumes_gender/', methods=['POST'])
def select_resumes_by_gender():        
    gender = 0 if request.form.get('gender') == 'female' else 1
    selected_resumes = Resume.query.filter(Resume.gender == gender)

    return render_template('selected_resumes_gender.html',
                            selected_resumes=selected_resumes,
                            all_keywords=ALL_KEYWORDS)


if __name__ == '__main__':
    get_resume_from_superjob_and_parse_it()
    APP.run(debug = True)
