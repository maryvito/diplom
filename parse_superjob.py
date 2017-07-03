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


def parse_html(html):
    bs = BeautifulSoup(html, 'html.parser')
    return bs.prettify()
    
    # title = bs.find_all('time', class_ = 'g-time')
   
    # for item in title:
    #     t = item.get('datetime')
    #     print (str(t))


def get_resume_from_superjob_and_parse_it():
    url = 'https://www.superjob.ru/resume/search_resume.html?sbmit=1&show_refused=0&t%5B0%5D=4&order_by%5Brank%5D=desc&keywords%5B0%5D%5Bkeys%5D=%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82+python&page={}'
    with open ('data_from_superjob.txt', 'w', encoding='utf-8') as f:
        number_page = 1
        print(url.format(number_page))
        while requests.get(url.format(number_page)).status_code == 200:

            html = get_html(url.format(number_page))
            f.write(html)
            number_page += 1

            
