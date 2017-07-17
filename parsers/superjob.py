import datetime 
import sys

import requests
from bs4 import BeautifulSoup

from config import cookies, RU_MONTH_VALUES 
# sys.path.append('/home/mashik/projects/site')
sys.path.append('D:\\fun\site')
from models import Resume, Keywords, db_session
from helper_for_parsers import calculate_age



def get_html(url):
    result = requests.get(url, cookies=cookies)     
    if result.status_code == requests.codes.ok:
        return result.text
    else:
        print('Something goes wrong.')
        return None 


def parse_salary(bs_resume):    
    # парсим строку вида "Резюме: Руководитель отдела, Москва, Образование: Высшее, Возраст: 25 лет, по договоренности.
    data_resume = bs_resume.find('meta', property='og:description').get('content').split(',')
    salary = data_resume[-1].strip().strip('.')
    if salary != 'по договоренности':
        salary = int(salary.split('руб')[0].replace(' ',''))
    else:
        salary = None
    return salary


def parse_personal_info(bs_resume):
    personal_data = bs_resume.find('span', class_ = 'h_font_weight_medium').findNext('div').text.strip().split('\n')[0]
    gender, birth_date = personal_data.split(',')[0],personal_data.split(',')[1]
    
    try:
        degree = personal_data.split(',')[2].strip()
        if degree == 'высшее образование':
            has_degree = True
        else:
            has_degree = False
    except IndexError:
        has_degree = None        
           
    day, month, year = birth_date.split('(')[-1].strip(')').split(' ')
    month = RU_MONTH_VALUES[month]
    birth_date = datetime.date(int(year), month, int(day))    
    age = calculate_age(birth_date)   
    return gender, has_degree, age


def parse_city(bs_resume):
    personal_data = bs_resume.find('span', class_ = 'h_font_weight_medium').findNext('div').text.strip().split('\n')
    city = personal_data[1].split(',')[0].strip()
    return city


# TODO: оптимизировать подбор навыков
def parse_skills(bs_resume):
    professional_skills = bs_resume.find(text='Профессиональные навыки')
    keywords_from_resume = []
    if professional_skills != None:
        professional_skills = bs_resume.find(text='Профессиональные навыки').findNext('div').text        
        keywords_from_resume = []
        keywords_from_base = Keywords.query.all()
        for item in keywords_from_base:
            if item.keyword.lower() in professional_skills:
                keywords_from_resume.append(item.keyword.lower())             
    return str(keywords_from_resume)


def parse_resume(bs_resume):
    gender, has_degree, birth_date = parse_personal_info(bs_resume)
    return {
        'gender': gender,
        'has_degree': has_degree,
        'age': birth_date,
        'keywords': parse_skills(bs_resume),
        'salary': parse_salary(bs_resume),
        'city': parse_city(bs_resume)
    }

    
def parse_html(html):
    data_resumes_list = []
    bs_resumes = BeautifulSoup(html, 'html.parser')
    resumes = bs_resumes.find_all('a', class_ = 'sj_h3 ResumeListElementNew_profession')
    data_from_resume_dict = {}
    for item in resumes:
        url_resume = item.get('href').split('?')[0] 
        html_resume = get_html(url_resume)
        bs_resume = BeautifulSoup(html_resume,'html.parser')
        data_from_resume_dict = parse_resume(bs_resume)
        data_from_resume_dict['url'] = url_resume
        data_from_resume_dict['title'] = item.get('title')
        data_resumes_list.append(data_from_resume_dict)
    return data_resumes_list


def put_data_resume_in_base(data_resumes_list, db_session):
    all_urls = []
    for item in Resume.query.all():
        all_urls.append(item.url)

    for item in data_resumes_list:
        if item['url'] not in all_urls:
            all_urls.append(item['url'])
            resume = Resume(item['title'], item['gender'],
                       item['age'], item['has_degree'],
                       item['city'], str(item['keywords']),
                       item['salary'], item['url'])
            db_session.add(resume)
    db_session.commit()
        
        
def parse_resumes(db_session):
    url = 'https://www.superjob.ru/resume/search_resume.html?sbmit=1&show_refused=0&t[]=4&order_by[rank]=desc&sbmit=1&order_by[rank]=desc&keywords[0][keys]=python&page={}'
    number_page = 1
    html = ''
    while requests.get(url.format(number_page)).status_code == 200 and number_page < 2:
        html += get_html(url.format(number_page))
        number_page += 1    
    data_resumes_list = parse_html(html)
    put_data_resume_in_base(data_resumes_list, db_session)


if __name__ == '__main__':
    parse_resumes(db_session)
