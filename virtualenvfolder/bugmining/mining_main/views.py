from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from .models import Bug, File, Author
from .bug_id_scraping import get_bugids, get_gerrit_links
from .js_scraping import get_inner_html, get_committed_files, get_authors, get_date
PATH = 0
ADDED = 1
DELETED = 2

def index(request):
    file_list = File.objects.order_by('-involved')[:5]
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
    top5 = ids[:5]
    i = 0
    for id in top5:
        try:
            b = Bug.objects.get(bug_id=str(id))
        except Bug.DoesNotExist:
            b = Bug(bug_id=str(id))
            b.save()
            get_info_from_bug(b)
            i += 1
            print("finished ", i, " files")
    # bug_list = Bug.objects.order_by('bug_id')
    # template = loader.get_template('mining_main/index.html')
    # context = {
    #     'bug_list': bug_list
    # }
    file_list = File.objects.order_by('-involved')[:5]
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
    f.involved += 1
    f.total_changeset += changeset
    f.bugs.add(bug)
    f.save()
    return f

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
