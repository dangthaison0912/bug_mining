from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from .models import Bug, File, Author, Release
from .bug_id_scraping import get_bugids, get_gerrit_links
from .js_scraping import get_inner_html, get_committed_files, get_authors, get_date
from .code_metrics_scraping import get_code_metrics, get_release, check_vulnerability
PATH = 0
ADDED = 1
DELETED = 2
CHANGESET = 3
BUGS = 4
def index(request):
    file_list = File.objects.order_by('-involved')
    template = loader.get_template('mining_main/index.html')
    context = {
        'file_list' : file_list
    }
    return render(request, 'mining_main/index.html', context)

def bug_detail(request, bug_id):
    bug = get_object_or_404(Bug, pk=bug_id)
    return render(request, 'mining_main/bug_detail.html', {'bug': bug})

def file_detail(request, file_id):
    file = get_object_or_404(File, pk=file_id)
    return render(request, 'mining_main/file_detail.html', {'file': file})

def author_detail(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    return render(request, 'mining_main/author_detail.html', {'author': author})

def update_bug_lists(request):
    ids = get_bugids()
    ids.sort()
    ids.reverse()
    top5 = ids[:100]
    i = 0
    for id in top5:
        try:
            b = Bug.objects.get(bug_id=str(id))
        except Bug.DoesNotExist:
            b = Bug(bug_id=str(id))
            b.save()
            get_info_from_bug(b)
            i += 1
            print("finished ", i, " bugs")
    # bug_list = Bug.objects.order_by('bug_id')
    # template = loader.get_template('mining_main/index.html')
    # context = {
    #     'bug_list': bug_list
    # }
    file_list = File.objects.order_by('-involved')[:10]
    template = loader.get_template('mining_main/index.html')
    context = {
        'file_list' : file_list
    }
    return render(request, 'mining_main/index.html', context)

def delete_all_bugs(request):
    Bug.objects.all().delete()
    File.objects.all().delete()
    Author.objects.all().delete()
    return index(request)

def get_info_from_bug(bug):
    url = "https://bugs.chromium.org/p/chromium/issues/detail?id=" + bug.bug_id
    links = get_gerrit_links(url)
    if links is not None:
        for link in links:
            innerhtml = get_inner_html(link)
            files = get_committed_files(innerhtml)
            author_name = get_authors(innerhtml)
            date = get_date(innerhtml)
            if files is not None:
                for file_info in files:
                    f = update_file_database(file_info, bug, len(files))
                    a = update_author_database(author_name,f)

def update_file_database(file_info, bug, changeset):
    path = file_info[PATH]
    added = file_info[ADDED]
    deleted = file_info[DELETED]
    try:
        f = File.objects.get(file_path=path)
        # f.added += int(added)
        # f.deleted += int(deleted)
        # f.involved += 1
        # f.total_changeset += changeset
        # f.bugs.add(bug)
        # f.save()
    except File.DoesNotExist:
        # f = File(file_path=path, added=added, deleted=deleted, involved=1, total_changeset = changeset)
        f = File(file_path=path)
        # f.bugs.add(bug)
        f.save()
    f.added += int(added)
    f.deleted += int(deleted)
    f.last_updated = bug.updated_date
    f.total_changeset += changeset
    try:
        b = f.bugs.get(bug)
    except Bug.DoesNotExist:
        f.bugs.add(bug)
        f.involved += 1
    f.save()
    return f

def get_metrics_from_git(request):
    url = "https://chromium.googlesource.com/chromium/src/+log/66.0.3359.117..66.0.3359.139?pretty=fuller&n=10000"
    release_number = get_release(url)
    print("Release number: ", release_number)
    try:
        release = Release.objects.get(release_number=release_number)
    except Release.DoesNotExist:
        release = Release(release_number=release_number)
    release.save()
    path_metrics_changeset_bugs = get_code_metrics(url)
    for file_info in path_metrics_changeset_bugs:
        update_files_from_git(file_info, release)
    return index(request)


def update_files_from_git(file_info, release):
    path = file_info[PATH]
    added = file_info[ADDED]
    deleted = file_info[DELETED]
    changeset = file_info[CHANGESET]
    bugids = file_info[BUGS]
    bugs = []
    for bugid in bugids:
        try:
            bug = Bug.objects.get(bug_id=str(bugid))
        except Bug.DoesNotExist:
            bug = Bug(bug_id=str(bugid))
            bug.save()
            print("added ", bugid)
        bugs.append(bug)

    try:
        f = File.objects.get(file_path=path, release=release)
    except File.DoesNotExist:
        f = File(file_path=path, release=release)
        f.save()
        print("added ", f.file_path)
    f.added += int(added)
    f.deleted += int(deleted)
    f.total_changeset += int(changeset)-1
    for bug in bugs:
        try:
            b = f.bugs.get(bug_id=bug.bug_id)
        except Bug.DoesNotExist:
            f.bugs.add(bug)
            f.involved += 1
    f.save()
    return f

def check_defects_in_next_release(request):
    # files_list = File.objects.filter(release__release_number='66.0.3359.170..66.0.3359.181
    files_list = File.objects.all()
    file_path_list = set()
    for file in files_list:
        file_path_list.add(file.file_path)



    url = "https://chromium.googlesource.com/chromium/src/+log/66.0.3359.181..67.0.3396.62?pretty=fuller&n=10000"
    next_release_defects = check_vulnerability(url)
    files_defects_map = map_files_and_bugs(file_path_list, next_release_defects)


    print_attributes(files_defects_map)

    template = loader.get_template('mining_main/result.html')
    context = {
        'files_defects_map' : files_defects_map
    }
    return render(request, 'mining_main/result.html', context)

def map_files_and_bugs(file_path_list, next_release_defects):
    bugs_in_files = []
    counter = 0

    for file in file_path_list:
        print("checking ", counter, "/", len(file_path_list))
        is_defected = False
        if file in next_release_defects:
            is_defected = True
        bugs_in_files.append(is_defected)
        counter += 1
    files_defects_map = zip(file_path_list, bugs_in_files)
    return files_defects_map

def update_author_database(author_name, file):
    try:
        author = Author.objects.get(author_name=author_name)
        # author.files.add(file)
    except Author.DoesNotExist:
        author = Author(author_name=author_name)
        author.save()
        # author.files.add()
    author.files.add(file)
    author.save()
    return author

def print_defect_status(files_defects_map):
    defect_list = open("defect.txt", "w")
    non_defect_list = open("non-defect.txt", "w")
    is_defect = 0
    not_defect = 0
    for file_defect_status in files_defects_map:
        print(file_defect_status[0], ": ", file_defect_status[1])
        if(file_defect_status[1]):
            defect_list.write(file_defect_status[0] + "\n")
            is_defect += 1
        else:
            non_defect_list.write(file_defect_status[0] + "\n")
            not_defect +=1
    print("Total defected files: ", is_defect)
    print("Total safe files: ", not_defect)

    defect_list.close()
    non_defect_list.close()

def print_attributes(files_defects_map):
    """
    Get all the data of attributes needed for Naive Bayes Classifier
    """

    data_set = open("data_set.txt", "w")
    file_attributes_list = []
    for file in files_defects_map:
        file_all_releases = File.objects.filter(file_path=file[PATH])
        total_added = 0
        total_deleted = 0
        total_changeset = 0
        total_involved = 0
        for file_per_release in file_all_releases:
            total_added += file_per_release.added
            total_deleted += file_per_release.deleted
            total_changeset += file_per_release.total_changeset
            total_involved += file_per_release.involved
        average_added = round(total_added/total_involved, 2)
        average_deleted = round(total_deleted/total_involved, 2)
        average_changset = round(total_changeset/total_involved, 2)
        file_attributes = [file[PATH], str(average_added), str(average_deleted), str(average_changset), str(file[1])]
        file_attributes_list.append(file_attributes)
        data_set.write(" ".join(file_attributes) + "\n")
    data_set.close()
