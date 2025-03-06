# student_urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.student_home, name='home-student'),
    path('api/homework/', views.HomeworkView.as_view(), name='homework-view'),
    path('api/send/picture/', views.PicturesSendAPIView.as_view(), name='send-picture'),
    path('api/delete/picture/', views.PicturesDeleteAPIView.as_view(), name='delete-picture'),
]
