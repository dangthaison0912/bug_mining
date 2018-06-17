from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from .models import Bug, File, Author, Release
from .bug_id_scraping import get_bugids, get_gerrit_links
from .js_scraping import get_inner_html, get_committed_files, get_authors, get_date
from .code_metrics_scraping import get_code_metrics, get_release, check_vulnerability, get_occurrences
from .classifier import classifier_defect, classifier_defect_fold
from .forms import ReleaseForm
from django.http import HttpResponseRedirect

PATH = 0
ADDED = 1
DELETED = 2
CHANGESET = 3
BUGS = 4

def index(request):
    """
    Handle index page request
    """
    file_list = File.objects.order_by('-added')[:5]
    template = loader.get_template('mining_main/index.html')
    context = {
        'file_list' : file_list
    }
    return render(request, 'mining_main/index.html', context)

def bug_detail(request, bug_id):
    """
    Handle bug page request
    """
    bug = get_object_or_404(Bug, pk=bug_id)
    return render(request, 'mining_main/bug_detail.html', {'bug': bug})

def file_detail(request, file_id):
    """
    Handle file page request
    """
    file = get_object_or_404(File, pk=file_id)
    return render(request, 'mining_main/file_detail.html', {'file': file})

def author_detail(request, author_id):
    """
    Handle author page request
    """
    author = get_object_or_404(Author, pk=author_id)
    return render(request, 'mining_main/author_detail.html', {'author': author})


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

def update_bug_lists(request):
    """
    Scrape all data of all bugs from the Bug Blog
    Limit: 6000 bugs
    """
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
    file_list = File.objects.order_by('-involved')[:10]
    template = loader.get_template('mining_main/index.html')
    context = {
        'file_list' : file_list
    }
    return render(request, 'mining_main/index.html', context)

def delete_all_bugs(request):
    """
    Delete all data from the database
    """
    Release.objests.all().delete()
    Author.objects.all().delete()
    return index(request)

def get_info_from_blog(bug):
    """
    Scrape data of the given bug from the Bug blog
    """
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
                    f = update_file_from_blog(file_info, bug, len(files))
                    a = update_author_database(author_name,f)

def update_file_from_blog(file_info, bug, changeset):
    """
    Update data of the bug from the blog to the database
    """
    path = file_info[PATH]
    added = file_info[ADDED]
    deleted = file_info[DELETED]
    try:
        f = File.objects.get(file_path=path)

    except File.DoesNotExist:
        f = File(file_path=path)
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
    """
    Scrape file metrics data from the given release changelog url
    Metrics collected: ADDED, DELETED, CHANGSET
    """
    if request.method == 'POST':
        form = ReleaseForm(request.POST)
        if form.is_valid():
            release_number = request.POST.get("release_number")
            url = "https://chromium.googlesource.com/chromium/src/+log/" + release_number + "?pretty=fuller&n=10000"
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
            return HttpResponseRedirect('/mining_main/')
        else:
            form = ReleaseForm()
            return HttpResponseRedirect('/mining_main/')

def update_files_from_git(file_info, release):
    """
    Update collected data from a release changelog to the database
    """
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
    """
    Connect to the change log of the latest release for the list of defect files
    Find the files in the database that are defective
    """
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ReleaseForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            release_number = request.POST.get("release_number")
            # release_number = "65.0.3325.181..66.0.3359.117"
            files_list = File.objects.all()
            file_path_list = set()
            for file in files_list:
                file_path_list.add(file.file_path)

            # url = "https://chromium.googlesource.com/chromium/src/+log/66.0.3359.181..67.0.3396.62?pretty=fuller&n=10000"
            url = "https://chromium.googlesource.com/chromium/src/+log/" + release_number + "?pretty=fuller&n=10000"
            next_release_defects = check_vulnerability(url)
            files_defects_map = map_files_and_bugs(file_path_list, next_release_defects)
        else:
            form = ReleaseForm()
            return HttpResponseRedirect('/mining_main/')

    # url_occ = "https://chromium.googlesource.com/chromium/src/+log/65.0.3325.181..66.0.3359.117?pretty=fuller&n=500"
    # files_occs = get_occurrences(file_path_list, url_occ)
    # # data_set = collect_data_set(files_defects_map)
    # for file_occ in files_occs:
    #     file = File.objects.get(file_path=file_occ[0], release__release_number=release_number)
    #     file.involved = file_occ[1]
    #     file.save()

    template = loader.get_template('mining_main/result.html')
    context = {
        'files_defects_map' : files_defects_map
    }
    return render(request, 'mining_main/result.html', context)

def get_name(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/mining_main/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, 'mining_main/name.html', {'form': form})

def map_files_and_bugs(file_path_list, next_release_defects):
    """
    From the list of defective file of the latest release, mark all files in
    the database if they are defective
    """
    bugs_in_files = []
    counter = 0
    defect_counter = 0
    for file in file_path_list:
        is_defect = 0
        if file in next_release_defects:
            is_defect = 1
            defect_counter += 1
        bugs_in_files.append(is_defect)
        counter += 1
        print("Checked ", counter, "/", len(file_path_list))
    print("Defect: ", defect_counter, "/", len(file_path_list))
    files_defects_map = zip(file_path_list, bugs_in_files)
    return files_defects_map



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


def collect_data_set(files_defects_map):
    """
    Get all the data of attributes needed for Naive Bayes Classifier from
    the database using the file-defect mapping
    [FILE_PATH, IS_DEFECT]
    """
    data_set = []
    data_set_file = open("data_set.txt", "w")
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
        file_attributes = [file[PATH], str(total_added), str(total_deleted),
                            str(average_added), str(average_deleted),
                            str(average_changset), str(total_involved), str(file[1])]
        data_set.append(file_attributes)
        data_set_file.write(" ".join(file_attributes) + "\n")
    data_set_file.close()
    return data_set

def run_classifier(request):
    """
    Get list of defective files from the lastest release
    Run classifier with the data from the database
    """
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ReleaseForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            release_number = request.POST.get("release_number")
            metrics = request.POST.get("metrics")

            files_list = File.objects.all()
            file_path_list = set()
            for file in files_list:
        # if file.release.release_number != "65.0.3325.181..66.0.3359.117":
                file_path_list.add(file.file_path)

            url = "https://chromium.googlesource.com/chromium/src/+log/" + release_number + "?pretty=fuller&n=10000"
            next_release_defects = check_vulnerability(url)
            # print(" ".join(metrics))
            list_of_metrics = list(map(int, metrics.split(",")))
            print(list_of_metrics[0])
            files_defects_map = map_files_and_bugs(file_path_list, next_release_defects)
            data_set = collect_data_set(files_defects_map)
            results = classifier_defect_fold(data_set, list_of_metrics)

            metric_mapping = {
                    0 : "ADDED",
                    1 : "DELETED",
                    2 : "AVG_ADDED",
                    3 : "AVG_DELETED",
                    4 : "CHANGESET"
            }


            context = {
                'results' : results
            }
            return render(request, 'mining_main/classifier.html', context)
        else:
            form = ReleaseForm()
            return HttpResponseRedirect('/mining_main/')
