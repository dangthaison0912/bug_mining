from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import urllib
import re
DELETED = 1
ADDED = 2


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

def get_release(url):
    """
    Scrape the stable release number
    """
    response = simple_get(url)
    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        release = html.find('span', {'class' : 'Breadcrumbs-crumb'})
        return release.text

def get_code_metrics(url):
    """
    Scrape file path and its code metrics from the stable release log_error
    """
    response = simple_get(url)

    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        diffs = html.findAll('ul', {'class' : 'DiffTree'})[:500]
        commits = html.findAll('pre', {'class' : 'u-pre u-monospace MetadataMessage'})[:500]
        bugs = []
        print("There are ", len(commits)," commits")
        print("There are ", len(diffs), " diffs")
        for commit in commits:
            list_of_bugids = ['-1']
            for line in commit.text.split("\n"):
                if ("bug: " in line.lower()) or ("bug=" in line.lower()):
                    list_of_bugids = re.findall(r'\d+', line)
                    # print(" ".join(list_of_bugids))
            bugs.append(list_of_bugids)
        files_code_change = []
        file_paths = []
        diff_links = []
        extended_bugs_list = []
        changesets = []
        count = 0
        total = len(diffs)
        for diff in diffs:
            all_as = diff.findAll('a')
            changeset = len(all_as)/2
            print(changeset)
            for a in all_as[0::2]:
                extended_bugs_list.append(bugs[count])
                file_paths.append(a.text)
                changesets.append(changeset)
            for a in all_as[1::2]:
                files_code_change.append(get_diff_value(a["href"]))
            count += 1
            print("Updated ", count, "/", total, " commits")
        files_added, files_deleted = zip(*files_code_change)
        files_metrics_bugs = list(zip(file_paths, files_added, files_deleted, changesets, extended_bugs_list))
        # print(*files_with_metrics, sep = "\n")
        # print(*files_info, sep = "\n")
        print(*files_metrics_bugs, sep = "\n")
        return files_metrics_bugs




def get_diff_value(link):
    """
    Collect Added and Deleted value for the given file
    """
    url = 'https://chromium.googlesource.com' + link
    response = simple_get(url)

    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        diff = html.find('span', {'class' : 'Diff-hunk'})
        string_parser = diff.text.split(" ")
        added = string_parser[ADDED].split(",")[1]
        deleted = string_parser[DELETED].split(",")[1]
        # return (added, deleted)
        return (added, deleted)

def check_vulnerability(url):
    """
    Check if the files from the list involved in any bug from the url
    """

    # response = simple_get(url)
    #
    # if response is not None:
    #     html = BeautifulSoup(response, 'html.parser')
    #     diffs = html.findAll('ul', {'class' : 'DiffTree'})
    #     commits = html.findAll('pre', {'class' : 'u-pre u-monospace MetadataMessage'})
    #     defected_files = set()
    #     counter = 0
    #     print(len(commits))
    #     for commit in commits:
    #         print("checking commit ", counter)
    #         if has_bugs(commit.text):
    #             all_as = diffs[counter].findAll('a')
    #             for a in all_as[0::2]:
    #                 defected_files.add(a.text)
    #                 print(a.text)
    #         counter += 1

    # return list(defected_files)

    with open('releaseMay29th.txt') as f:
        lines = f.read().splitlines()
    return lines



def has_bugs(commit):
    for line in commit.split("\n"):
        if "bug" in line.lower():
            return True
    return False

def get_occurrences(file_path_list, url):
    """
    Find the number of time each file is committed
    """
    response = simple_get(url)
    occurrences = []
    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        for file_path in file_path_list:
            occurrence = str(html).count(">"+file_path+"<")
            print(file_path, str(occurrence))
            occurrences.append(occurrence)
    files_occs_map = list(zip(file_path_list, occurrences))
    return files_occs_map

if __name__ == '__main__':
    print("Getting files and code metrics")
    url = 'https://chromium.googlesource.com/chromium/src/+log/66.0.3359.181..67.0.3396.62?pretty=fuller&n=10000'
    f = check_vulnerability(url)
    # print(get_release(url))
    file = open("releaseMay29th.txt", "w")
    file.write("\n".join(f))
    file.close()
