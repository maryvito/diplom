import simplejson
from flask import Flask, render_template, request
from database import Resume


def read_data_from_json(fileName):
    with open (fileName, 'r') as f:
        d = f.read()
        data = simplejson.loads(d)
        return data

app = Flask(__name__)

@app.route('/')
def index():
    r = Resume
    resumes_db = r.query.all()   
    return render_template('index.html', resumes_db=resumes_db) 

@app.route('/changed_resume/', methods = ['POST'])
def index1():
    r = Resume
    resumes_db = r.query.all() 
    keyword = request.form.get('keyword')    
    changed_resumes = []
    for res in resumes_db:
    	if keyword in res.keywords:
    		changed_resumes.add(res)    
    return render_template('changed_resume.html', changed_resumes = changed_resumes)           

if __name__ == '__main__':
    app.run(debug = True)