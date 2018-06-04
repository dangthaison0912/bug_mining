from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Bug
def index(request):
    bug_list = Bug.objects.order_by('fixed_date')[:5]
    template = loader.get_template('mining_main/index.html')
    context = {
        'bug_list': bug_list
    }
    return HttpResponse(template.render(context, request))

def detail(request, bug_id):
    return HttpResponse("You're looking at bug %s." % bug_id)

def results(request, bug_id):
    response = "You're looking at the results of bug %s."
    return HttpResponse(response % bug_id)

def vote(request, bug_id):
    return HttpResponse("You're voting on bug %s." % bug_id)
