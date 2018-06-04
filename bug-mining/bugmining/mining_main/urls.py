from django.urls import path

from . import views

urlpatterns = [
    #ex: /miningmain
    path('', views.index, name='index'),
    #ex: /miningmain/5/
    path('<int:bug_id>/', views.detail, name='detail'),
    # ex: /polls/5/results/
    path('<int:bug_id>/results/', views.results, name='results'),
    # ex: /polls/5/vote/
    path('<int:bug_id>/vote/', views.vote, name='vote'),
]
