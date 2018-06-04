from selenium import webdriver
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from requests import get
import time

# setup chrome webdriver
path_to_chromedriver = '/usr/local/bin/chromedriver'
browser = webdriver.Chrome(executable_path = path_to_chromedriver)

# get info
def get_inner_html(url):
    """
    Attempts to get the content of the url by making an HTTP GET requestself.
    Since the content is JS-based, a webdriver is used to extract the generated data
    """
    try:
        with closing(get(url, stream=True)) as response:
            if is_good_response(response):
                browser.get(url)
                time.sleep(10) ## to give the browser time for js to generate content (?)
                innerHTML = browser.execute_script("return document.body.innerHTML") #returns the inner HTML as a string
                js_data_output = open("js_data.txt", "w")
                js_data_output.write(innerHTML)
                js_data_output.close()
                return innerHTML
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

def get_committed_files(innerhtml):
    """
    Extract the path of all files involved in fixing the bug
    """
    if innerhtml is not None:
        html = BeautifulSoup(innerhtml, 'html.parser')
        data_extracted = html.findAll("div", {"class" : "stickyArea style-scope gr-file-list"})
        files = []
        for d in data_extracted:
            path = d.find("span", {"class" : "fullFileName style-scope gr-file-list"})
            added = d.find("span", {"class" : "added style-scope gr-file-list"})
            deleted = d.find("span", {"class" : "removed style-scope gr-file-list"})
            file_information = []
            file_information.append(path.string)
            file_information.append(added.string)
            file_information.append(deleted.string)
            files.append(file_information)
        return list(files)


if __name__ == '__main__':
    print('Getting list of involved files...')
    url = 'https://chromium-review.googlesource.com/c/chromium/src/+/1070794/'
    innerhtml = get_inner_html(url)
    files = get_committed_files(innerhtml)
    js_commited_files = open("js_commited_files.txt", "w")
    for row in files:
        row_string = ""
        for column in row:
            row_string += column + " "
        js_commited_files.write(row_string)
    js_commited_files.close()
    print('Done')

    # for id in ids:
    #     print(str(id) + '\n')
    print('There are total {} files path found'.format(len(files)))
