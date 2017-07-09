import requests

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
