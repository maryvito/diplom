import datetime

import requests
from bs4 import BeautifulSoup


def get_html(url):
    try:
        result = requests.get(url)
        result.raise_for_status()
        html = result.text
        return html
    except requests.exceptions.RequestException as e:
        print(e)
        return False


def parse_resume(url):
    html_resume = get_html(url)
    bs_resume = BeautifulSoup(html_resume, 'html.parser')
    main_data_resume = bs_resume.find('div', class_ = 'ResumeMainHRNew_content')
    gender_age_degree_city = main_data_resume('div', limit = 3)[2].text.strip()
    gender_age_degree_city = gender_age_degree_city.split('\n')[0].strip()
    gender_age_degree_city_list = gender_age_degree_city.split(',')
    print(gender_age_degree_city_list)

    if gender_age_degree_city[2] == 'высшее образование':
        degree = 'true'
    else:
        degree = 'false' 
    
    gender = gender_age_degree_city[0]
    if gender == 'Жен.':
        gender = 'female'
    else:
        gender == 'male'
    print(gender_age_degree_city[1])
    day, month, year = gender_age_degree_city[1].split('(')[-1].strip(')').split(' ')
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

    month = RU_MONTH_VALUES(month)

    age = datetime.date(year, month, day)
    print(age)



    # details_resume = bs_resume.find(text='Профессиональные навыки')
    # keywords = str(details_resume.findNext('div'))[36:-6].  split('<br/>')
    # return [gender, age, degree, keywords]
    
    
def parse_html(html):
    bs_resumes = BeautifulSoup(html, 'html.parser')
        
    resumes_title_href = bs_resumes.find_all('a', class_ = 'sj_h3 ResumeListElementNew_profession')

    with open ('data_new.json', 'w', encoding='utf-8') as f:
        f.write('[\n\t')
        for item in resumes_title_href:
            f.write('{\n\t\t\"title\": \"' + item.get('title')+'\"\n,')
            url_resume = item.get('href').split('?')[0]
            city = item('span', limit = 3)[1].text
            data_from_resume = parse_resume(url_resume)
            f.write('\t\t\"gender\": \"' + data_from_resume[0]+'\"\n,')
            f.write('\t\t\"age\": \"' + data_from_resume[1]+'\"\n,')
            f.write('\t\t\"has_degree\": \"' + data_from_resume[2]+'\"\n,')
            f.write('\t\t\"city\": \"' + city+'\"\n,')
            f.write('\t\t\"keywords\": \"' + str(data_from_resume[3])+'\"\n,')
            f.write('\t\t\"url\": \"' + url_resume+'\"\n}\n,')
        f.write(']')       
        
        
def get_resume_from_superjob_and_parse_it():
    url = 'https://www.superjob.ru/resume/search_resume.html?sbmit=1&show_refused=0&t%5B0%5D=4&order_by%5Brank%5D=desc&keywords%5B0%5D%5Bkeys%5D=%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82+python&page={}'
    with open ('data_from_superjob.txt', 'w', encoding='utf-8') as f:
        number_page = 1
        while requests.get(url.format(number_page)).status_code == 200 and number_page < 3:
            html = get_html(url.format(number_page))
            f.write(html)
            number_page += 1

# h = get_html('https://www.superjob.ru/resume/search_resume.html?sbmit=1&show_refused=0&t%5B0%5D=4&order_by%5Brank%5D=desc&keywords%5B0%5D%5Bkeys%5D=%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82+python&page=1')
# parse_html(h)
if __name__ == '__main__':
    parse_resume(url='https://www.superjob.ru/resume/programmist-python-20379183.html')