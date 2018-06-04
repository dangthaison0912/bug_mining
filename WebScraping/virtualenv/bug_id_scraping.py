from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import urllib

FIXED_ROW = 6
def simple_get(url):
    """
    Attempts to get the content of the url by making an HTTP GET requestself.
    If the content-type of response is of type HTML/XML, return the content,
    otherwise return None
    """
    try:
        with closing(get(url, stream=True)) as response:
            if is_good_response(response):
                return response.content
            else:
                return None
    except RequestException as e:
        log_error('Error during requests to {0}: {1}'.format(url, str(e)))

def is_good_response(response):
    """
    Return True if the response seems to be HTML, false otherwise
    """
    content_type = response.headers['Content-Type'].lower()
    return (response.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

def log_error(error):
    """
    Handle error message
    """
    print(error)

def get_bugids():
    """
    Download the Chromium Bug Blog and return a list of fixed security bug ids
    """
    url = 'https://bugs.chromium.org/p/chromium/issues/list?can=1&q=label%3Asecurity%2C+status+%3D+fixed&colspec=ID+Pri+M+Stars+ReleaseBlock+Component+Status+Owner+Summary+OS+Modified&sort=&groupby=&mode=grid&y=Status&x=--&cells=ids&nobtn=Update'
    response = simple_get(url)

    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        table = html.find("table", {"class" : "results", "id"  : "resultstable"})
        ids = set()
        fixed = table.findAll('tr')[FIXED_ROW].findAll('td')[0]
        for id in fixed.findAll('a'):
            if len(id) > 0:
                ids.add(id.string)
        return list(ids)


if __name__ == '__main__':
    print('Getting list of bug ids')
    ids = get_bugids()
    ids.sort()
    ids.reverse()
    file = open("bug_id.txt", "w")
    file.write("\n".join(ids))
    file.close()
    print('Done')

    # for id in ids:
    #     print(str(id) + '\n')
    print('There are total {} bug ids found'.format(len(ids)))
