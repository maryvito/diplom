# -*- coding: utf-8 -*-

import pprint
import sys
import requests

from bs4 import BeautifulSoup


sys.path.append('/home/mashik/projects/site')
from models import Resume, Keywords


def get_html(url, params=None):
    user_agent = {'User-agent': 'Mozilla/5.0'}

    result = requests.Response
    result.status_code = None

    try:
        result = requests.get(url=url, headers=user_agent, params=params)
    except requests.RequestException as error:
        print(error)

    if result.status_code == requests.codes.ok:
        return result.text
    else:
        print('Something goes wrong.')
        return None


def fetch_page_resume_list(html_page):
    """
        The function parses resumes rows on each page of output listing.
        Then it creates the list of resumes.
        After that the function asdds the next information from the list to the resume list:
         - age
         - gender
         - url to personal resume

         Input: (str) HTML text
         Output: (list) list of resumes
    """

    page_soup = BeautifulSoup(html_page, 'html.parser')

    resume_list = []

    for row in page_soup.tr(class_='output__item'):

        # Fetch age, gender and url from output listing page
        tag_with_age = row.find('span', class_='output__age')
        tag_with_gender = row.find('meta', itemprop='gender')
        tag_with_url = row.find('a', itemprop='jobTitle')

        # strip years number off ' years'
        age = tag_with_age.text.strip().split('\xa0')[0]
        # check that the age is specified
        age = int(age) if age else None
        gender = tag_with_gender.attrs['content']
        url = 'https://hh.ru{}'.format(tag_with_url.attrs['href'])
        title = tag_with_url.text

        resume = {'gender': gender,
                  'url': url,
                  'title': title,
                  'age': age,
                  'has_degree': False,
                  'city': '',
                  'keywords': []}

        resume_list.append(resume)

    return resume_list


def fetch_info_from_resume(resume, resume_html):
    """
        The function adds the next information from personal resume page to the resume:
         - has_degree
         - keywords
         - city

         Input: (dict) resume, (str) resume_html
         Output: (dict) resume
    """

    resume_page_soup = BeautifulSoup(resume_html, 'html.parser')

    # Check that the resume page include a highschool/university degree mark
    resume_page_degree_mark = resume_page_soup.find_all(string='Высшее образование')
    # Add the degree mark to resume parameter
    if resume_page_degree_mark:
        resume['has_degree'] = True

    # Fetch the list tags with keywords
    resume_page_keywords_tags = resume_page_soup.find_all('span', class_='bloko-tag__section bloko-tag__section_text')
    resume_page_keywords_list = []
    # Add keywords to the list
    for tag in resume_page_keywords_tags:
        resume_page_keywords_list.append(tag.text)
    resume['keywords'] = resume_page_keywords_list

    # Fetch the city name
    resume_page_city_tag = resume_page_soup.find('span', itemprop='addressLocality')
    if resume_page_city_tag:
        resume['city'] = resume_page_city_tag.text

    resume_page_salary_tag = resume_page_soup.find('span', class_='resume-block__salary')
    if resume_page_salary_tag:
        resume['salary'] = resume_page_salary_tag.text


    return resume


def put_data_resume_in_base(data_from_resumes_list, db_session):
    all_keywords = []
    for item in data_from_resumes_list:

        r = Resume(item['title'], item['gender'],
                   item['age'], item['has_degree'],
                   item['city'], str(item['keywords']),
                   item['salary'], item['url'])

        db_session.add(r)
        # keywords_from_base = Keywords.query.all()
        for keyword in item['keywords']:
            # for item_key in keywords_from_base:
            # if item_key.keyword in professional_skills:
            # if keyword not in 
            if keyword not in all_keywords:
                k = Keywords(keyword.lower())
                db_session.add(k)
                all_keywords.append(keyword.lower())
    db_session.commit()


def fetch_resume_list_by_keyword(keyword):
    """
        The function fetch resume list from hh.ru by keyword

         Input: (str) keyword
         Output: (list) full list of resumes at hh.ru
    """

    full_resume_list = []

    # HH.ru limits page number value to 50 maximum
    for page_number in range(0, 1):
        url_args = {
            'exp_period': 'all_time',
            # HH.ru limits items max on page from 10 to 100
            'items_on_page': 10,
            'order_by': 'relevance',
            # Keyword 'python' to url argument
            'text': keyword,
            'pos': 'full_text',
            'source': 'resumes',
            'logic': 'normal',
            'clusters': 'true',
            'page': page_number
        }
        page_url = 'https://hh.ru/search/resume?'
        page_html_data = get_html(page_url, url_args)

        if page_html_data:
            page_resume_list = fetch_page_resume_list(page_html_data)
            # Add list of resumes for every output results page
            full_resume_list += page_resume_list
            page_number += 1

    for resume in full_resume_list:
        fetch_info_from_resume(resume, get_html(resume['url']))

    return full_resume_list

def parse_resumes(db_session):
    full_resume_list = fetch_resume_list_by_keyword('python')
    put_data_resume_in_base(full_resume_list, db_session)


if __name__ == '__main__':
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(fetch_resume_list_by_keyword('python'))
