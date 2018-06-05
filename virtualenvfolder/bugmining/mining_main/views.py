from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from .models import Bug

def index(request):
    bug_list = Bug.objects.order_by('bug_id')[:5]
    template = loader.get_template('mining_main/index.html')
    context = {
        'bug_list': bug_list
    }
    return render(request, 'mining_main/index.html', context)

def detail(request, bug_id):
    bug = get_object_or_404(Bug, pk=bug_id)
    return render(request, 'mining_main/detail.html', {'bug': bug})

def results(request, bug_id):
    response = "You're looking at the results of bug %s."
    return HttpResponse(response % bug_id)

def vote(request, bug_id):
    return HttpResponse("You're voting on bug %s." % bug_id)
