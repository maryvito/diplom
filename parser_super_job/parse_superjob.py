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
    print(main_data_resume)
    gender_age_degree_city = main_data_resume('div', limit = 3)[2].text.strip()

    gender_age_degree = gender_age_degree_city.split('\n')[0].strip()
    city = gender_age_degree_city.split('\n')[1].strip()
    gender_age_degree_list = gender_age_degree.split(',')
   
    if gender_age_degree[2] == 'высшее образование':
        has_degree = 'true'
    else:
        has_degree = 'false' 
    
    gender = gender_age_degree[0]
    if gender == 'Жен.':
        gender = 'female'
    else:
        gender == 'male'
    
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

    return [gender, age, has_degree, city] 
    
    
def parse_html(html):
    bs_resumes = BeautifulSoup(html, 'html.parser')
        
    resumes_title_href = bs_resumes.find_all('a', class_ = 'sj_h3 ResumeListElementNew_profession')

    with open ('data_new.json', 'w', encoding='utf-8') as f:
        f.write('[\n\t')
        for item in resumes_title_href:
            f.write('{\n\t\t\"title\": \"' + item.get('title')+'\"\n,')
            url_resume = item.get('href').split('?')[0]
            data_from_resume = parse_resume(url_resume)
            f.write('\t\t\"gender\": \"' + data_from_resume[0]+'\"\n,')
            f.write('\t\t\"age\": \"' + str(data_from_resume[1])+'\"\n,')
            f.write('\t\t\"has_degree\": \"' + data_from_resume[2]+'\"\n,')
            f.write('\t\t\"city\": \"' + data_from_resume[3]+'\"\n,')
            # f.write('\t\t\"keywords\": \"' + str(data_from_resume[?])+'\"\n,')
            f.write('\t\t\"url\": \"' + url_resume+'\"\n}\n,')
        f.write(']')       
        
        
def get_resume_from_superjob_and_parse_it():
    url = 'https://www.superjob.ru/resume/search_resume.html?sbmit=1&show_refused=0&t[]=4&order_by[rank]=desc&sbmit=1&order_by[rank]=desc&keywords[0][keys]=python&page={}'
    number_page = 1
    html = ''
    while requests.get(url.format(number_page)).status_code == 200 and number_page < 3:
        html += get_html(url.format(number_page))
        number_page += 1
    with open ('data_from_superjob.txt', 'w', encoding='utf-8') as f:
        f.write(html)
    parse_html(html)



# h = get_html('https://www.superjob.ru/resume/search_resume.html?sbmit=1&show_refused=0&t%5B0%5D=4&order_by%5Brank%5D=desc&keywords%5B0%5D%5Bkeys%5D=%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82+python&page=1')
# parse_html(h)
if __name__ == '__main__':
    # parse_resume(url='https://www.superjob.ru/resume/programmist-python-20379183.html')
    get_resume_from_superjob_and_parse_it()