from django.contrib import admin
from django.urls import path
from taskapp import views


urlpatterns = [
    path('',views.index,name='index'),
    path('all/',views.display_tasks,name='all'),
    path('add/',views.add_records,name='add'),
    path('tasks/remove/<int:task_id>/',views.remove_records,name='remove'),
    # path('filter/',views.filter_records,name='filter'),
    path('tasks/update/<int:task_id>/',views.update_records,name='update'),
    path('search/', views.search_view, name='search'),

]


