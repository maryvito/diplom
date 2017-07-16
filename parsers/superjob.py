import datetime
import sys

import requests
from bs4 import BeautifulSoup

# from config import cookies
# sys.path.append('/home/mashik/projects/site')
from models import Resume, Keywords 



def get_html(url):
    result = requests.get(url, cookies={
        '_ga': 'GA1.2.1443249344.1498982928',                        
            '_gid':'GA1.2.1464582966.1500041990',              
            '_sp_id.8ab7':'f883b4534fa8231b.1498982930.22.1500128364.1500122814.52262b70-4853-4372-8e9f-5de6c9b1c1e2',            
            '_sp_ses.8ab7': '*',                 
            '_ws': '5958aa0f04a4fda40a0a019b19f47a314fa5ace703596a246b2532e42a87cefc8ab3c2ea236bb4ce93ea0cc21e',               
            '_wss':'596a246b',               
            '_ym_isad':'1',                
            '_ym_uid': '149898292832444728',              
            '_ym_visorc_1605911':  'w',                
            '_ym_visorc_31419523': 'w',                
            'bl_iv':'b1dfa029a7edfb8645f00e35e45493b70a58a2c4',          
            'ctown':'4',
            'enter_date': '1499502266 0',              
            'enter_referer':'https%3A%2F%2Fwww.google.ru%2F',
            'enter_url':'www.superjob.ru%2F',               
            'jv_enter_ts_BRDRBHmcqd':'1499002237738',               
            'jv_pages_count_BRDRBHmcqd':'20',              
            'jv_utm_BRDRBHmcqd':'',                    
            'jv_visits_count_BRDRBHmcqd':'1',                 
            'quicksearchkey':  'python',              
            'sjvid':'c206ab014fd4ac65',               
            'ssl_check':'success',               
            'ssl_check':   'success',          
            'testcookie':'1498982926',              
            'tmr_detect':  '1%7C1500128366232',
        })     
    
    if result.status_code == requests.codes.ok:
        return result.text
    else:
        print('Something goes wrong.')
        return None 


def parse_salary(bs_resume):    
    # парсим строку вида "Резюме: Руководитель отдела, Москва, Образование: Высшее, Возраст: 25 лет, по договоренности.
    data_resume = bs_resume.find('meta', property='og:description').get('content').split(',')
    salary = data_resume[-1].strip()
    return salary


def parse_personal_info(bs_resume):
    personal_data = bs_resume.find('span', class_ = 'h_font_weight_medium').findNext('div').text.strip().split('\n')[0]
    # print(personal_data)
    # personal_data, city = personal_data_resume.split('\n')[0],[1]
    gender, birth_date = personal_data.split(',')[0],personal_data.split(',')[1]
    # print(str(gender)+"|"+str(birth_date))
    try:
        degree = personal_data.split(',')[2].strip()
        if degree == 'высшее образование':
            has_degree = True
        else:
            has_degree = False
    except IndexError:
        has_degree = None        

    if gender == 'Жен.':
        gender = 'female'
    else:
        gender = 'male'
            
    day, month, year = birth_date.split('(')[-1].strip(')').split(' ')
    RU_MONTH_VALUES = {
        'января': 1,
        'февраля': 2,
        'марта': 3,
        'апреля': 4,
        'мая': 5,
        'июня': 6,
        'июля': 7,
        'августа': 8,
        'сентября': 9,
        'октября': 10,
        'ноября': 10,
        'декабря': 12,
    }
    month = RU_MONTH_VALUES[month]
    birth_date = datetime.datetime(int(year), month, int(day))
    # current_day = datetime.datetime.now()
    # age = datetime.date(year = current_day.year - birth_date.year).year
    # age = current_day - birthday
    # age = int(age.days/365)
    
    return gender, has_degree, birth_date

def parse_skills(bs_resume):
    professional_skills = bs_resume.find(text='Профессиональные навыки')
    print(professional_skills)
    keywords_from_resume = []
    if professional_skills:
       professional_skills = bs_resume.find(text='Профессиональные навыки').findNext('div').text

        # TODO: оптимизировать подбор навыков
    keywords_from_resume = []
    keywords_from_base = Keywords.query.all()
    for item in keywords_from_base:
        if item.keyword.lower() in professional_skills:
            keywords_from_resume.append(item.keyword.lower())
   
    return keywords_from_resume


def parse_resume(bs_resume):
    gender, has_degree, birth_date = parse_personal_info(bs_resume)
    return {
        'gender': gender,
        'has_degree': has_degree,
        'birth_date': birth_date,
        'skills': parse_skills(bs_resume),
        'salary': parse_salary(bs_resume)
    }

   
    
def parse_html(html):
    data_resumes_list = []
    bs_resumes = BeautifulSoup(html, 'html.parser')        
    resumes_title_href = bs_resumes.find_all('a', class_ = 'sj_h3 ResumeListElementNew_profession')
    data_from_resume_dict = {}
    for item in resumes_title_href:
        url_resume = item.get('href').split('?')[0]        
        title = item.get('title')
        raw_resume_html = get_html(url_resume)
        data_from_resume_dict['url'] = url_resume
        data_from_resume_dict['title'] = title
        html_resume = get_html(url_resume)
        bs_resume = BeautifulSoup(html_resume,'html.parser')
        data_from_resume_dict = parse_resume(bs_resume) 
        data_resumes_list.append(data_from_resume_dict)   

    return data_resumes_list


def put_data_resume_in_base(data_resumes_list, db_session):
    for item in data_resumes_list:

        r = Resume(item['title'], item['gender'],
                   item['age'], item['has_degree'],
                   item['city'], item['keywords'],
                   item['salary'], item['url'])

        db_session.add(r)
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


# if __name__ == '__main__':
#     pass
