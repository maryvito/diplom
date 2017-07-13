import requests
from bs4 import BeautifulSoup
from parse_superjob import get_html


def parse_resume(url):
    html_resume = get_html(url)
    bs_resume = BeautifulSoup(html_resume, 'html.parser')
    main_data_resume = bs_resume.find('div', class_ = 'ResumeMainHRNew_content')
    gender = main_data_resume('div', limit = 3)[2]
    with open ('resume#1_data.html', 'w', encoding='utf-8') as f:
        f.write(gender.text)

parse_resume(url='https://www.superjob.ru/resume/programmist-python-20379183.html')