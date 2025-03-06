# coach_urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('auth/', views.login_view, name='auth'),
    path('logout/', views.logout_view, name='logout-coach'),
    path('', views.apolon_yar_home, name='home'),
    path('student-homework/<uuid:id>/week/<int:week_number>/', views.studentHomeworkRender, name='student-homework'),
    path('api/submit/score/', views.SubmitScoreView.as_view(), name='submit_score'),  
    path('api/coaches/<uuid:id>/edit/', views.ApolonYarEditAPIView.as_view(), name='edit_coach'),
    path('api/apolon_yar/create/', views.ApolonYarCreateAPIView.as_view(), name='apolon-yar-create'),
    path('api/student/create/', views.StudentCreateAPIView.as_view(), name='student-create'),
]
