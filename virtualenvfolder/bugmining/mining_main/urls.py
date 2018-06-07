from django.urls import path

from . import views

app_name = 'mining_main'
urlpatterns = [
    #ex: /miningmain
    path('', views.index, name='index'),

    #ex: /miningmain/5/
    #the 'name' value is called by the {%url} template tag
    path('<int:bug_id>/', views.bug_detail, name='bug_detail'),
    path('file/<int:file_id>/', views.file_detail, name='file_detail'),
    path('author/<int:author_id>/', views.author_detail, name='author_detail'),
    path('update', views.update_bug_lists, name='update'),
    path('delete', views.delete_all_bugs, name='delete')
]
