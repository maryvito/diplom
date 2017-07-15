import datetime
import sys

import requests
from bs4 import BeautifulSoup

sys.path.append('/home/mashik/projects/site')
from models import Resume, Keywords 


def get_html(url):
    try:
        result = requests.get(url, cookies = {
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
            # 'ssl_check': 'success',
            # 'testcookie': '1498982926',
            # '_ym_uid': '149898292832444728',
            # 'jv_enter_ts_BRDRBHmcqd': '1499002237738',
            # 'jv_visits_count_BRDRBHmcqd': '1',
            # 'jv_utm_BRDRBHmcqd': '',
            # '_ym_isad': '1',
            # 'enter_referer': 'https%3A%2F%2Fwww.google.ru%2F',
            # 'enter_url': 'www.superjob.ru%2F',
            # 'enter_date': '1499502266',
            # 'sjvid': 'c206ab014fd4ac65',
            # 'quicksearchkey': '%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82+python',
            # 'jv_pages_count_BRDRBHmcqd': '13',
            # 'ctown': '4',
            # 'bl_iv': 'deb0d3dcf95dfdb2cc652303c26e7f1c99bf7b89',
            # '_wss': '5960f33b',
            # 'ssl_check': 'success',
            # '_ga': 'GA1.2.1443249344.1498982928',
            # '_gid': 'GA1.2.1780751538.1499502256',
            # '_ws': '5958aa0f04a4fda40a0a019b19f47a314fa5ace7035960f34002943467ea958e54e5ecfaf09205ef577934683a',
            # '_ym_visorc_31419523': 'w',
            # '_ym_visorc_1605911': 'w',
            # '_sp_id.8ab7': 'f883b4534fa8231b.1498982930.10.1499525954.1499521789.bb587ea2-4b29-4d3d-ae91-2207f13e54d1',
            # '_sp_ses.8ab7': '*',
            # 'uechat_34349_pages_count': '1',
            # 'uechat_34349_first_time': '1499525953838',
        })
        result.raise_for_status()
        html = result.text
        print(url)
        return html
    except requests.exceptions.RequestException as e:
        print(e)
        return False

# сделать чтоб функция принимала html
def parse_resume(url):
    html_resume = get_html(url)
    bs_resume = BeautifulSoup(html_resume, 'html.parser')
    
    salary_city = bs_resume.find('meta', property='og:description').get('content').split(',')
    salary =salary_city[-1][:-1].strip()
    if len(salary) != 17:
        salary = salary[:-13].replace(' ','')
    city = salary_city[1]
    
    # парсим строку вида "Резюме: Руководитель отдела, Москва, Образование: Высшее, Возраст: 25 лет, по договоренности.
    main_data_resume = bs_resume.find('span', class_ = 'h_font_weight_medium')
    gender_age_degree_city = main_data_resume.findNext('div').text.strip()
    gender_age_degree_city_list = gender_age_degree_city.split('\n')
    gender_age_degree = gender_age_degree_city_list[0].strip()
    gender_age_degree_list = gender_age_degree.split(',')
    gender = gender_age_degree_list[0]

    if gender == 'Жен.':
        gender = 'female'
    else:
        gender = 'male'
    
    if len(gender_age_degree_list) >= 3:
        if gender_age_degree_list[2] == 'высшее образование':
            has_degree = True
        else:
            has_degree = False 
    else:
        has_degree = None   
        
    day, month, year = gender_age_degree_list[1].split('(')[-1].strip(')').split(' ')
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
    birthday = datetime.datetime(int(year), month, int(day))
    current_day = datetime.datetime.now()
    age = current_day - birthday
    age = int(age.days/365) 

    professional_skills = bs_resume.find(text='Профессиональные навыки')
    keywords_from_resume = []
    if professional_skills:
        professional_skills = str(professional_skills.findNext('div'))[36:-6] # ???

        # TODO: оптимизировать подбор навыков
        keywords_from_resume = []
        keywords_from_base = Keywords.query.all()
        for item in keywords_from_base:
            if item.keyword.lower() in professional_skills:
                keywords_from_resume.append(item.keyword.lower())
    

    data_from_resume_dict = {'gender': gender, 'age': age, 'has_degree': has_degree,
                             'city': city, 'keywords': str(keywords_from_resume),
                             'salary': salary}
    print(data_from_resume_dict)
    return data_from_resume_dict


# def parse_resume(raw_resume_html):
#     bs = BeautifulSoup(...)
#     gender, has_degree, birth_date = parse_personal_info(raw_resume_html)
#     return {
#         'gender': gender,
#         'has_degree': has_degree,
#         'birth_date': birth_date,
#         'skills': parse_skills(raw_resume_html),
#     }

   
    
def parse_html(html):
    data_from_resumes_list = []
    bs_resumes = BeautifulSoup(html, 'html.parser')        
    resumes_title_href = bs_resumes.find_all('a', class_ = 'sj_h3 ResumeListElementNew_profession')
    
    for item in resumes_title_href:
        url_resume = item.get('href').split('?')[0]
        title = item.get('title')
        data_from_resume_dict = parse_resume(url_resume)
        data_from_resume_dict['title'] = title
        data_from_resume_dict['url'] = url_resume
        data_from_resumes_list.append(data_from_resume_dict)    

    return data_from_resumes_list


def put_data_resume_in_base(data_from_resumes_list, db_session):
    for item in data_from_resumes_list:

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
    # сделать чтоб  parse_html принимал html
    # data_from_resume_list = parse_html(html)
    print(html)
    data_from_resumes_list = parse_html(html)
    print(data_from_resumes_list)
    put_data_resume_in_base(data_from_resumes_list, db_session)


# if __name__ == '__main__':
#     pass
