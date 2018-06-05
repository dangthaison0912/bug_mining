from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    #ex: /miningmain
    path('', views.index, name='index'),

    #ex: /miningmain/5/
    #the 'name' value is called by the {%url} template tag
    path('<int:bug_id>/', views.detail, name='detail'),

    # ex: /miningmain/5/results/
    path('<int:bug_id>/results/', views.results, name='results'),
    
    # ex: /miningmain/5/vote/
    path('<int:bug_id>/vote/', views.vote, name='vote'),
]
