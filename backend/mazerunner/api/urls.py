from django.urls import path
from django.conf.urls import url
from .views import StudentAPIView , QuestionAPIView ,CreateQuestionAPIView , gameSummaryAPIView  , LoginAPIView , LeaderBoardAPIView, overallSummaryView, QuestionSubmitAPIView, signup
from django.contrib import admin
admin.site.site_header = "Mazerunner Administration"
admin.site.site_title = 'Mazerunner Admin'

urlpatterns = [
    path('api/login/',LoginAPIView.as_view(), name = 'login'),
    path('api/students/leaderboard', LeaderBoardAPIView.as_view() , name = 'leaderboard'),
    path('api/students', StudentAPIView.as_view() , name = 'students'),
    path('api/questions', QuestionAPIView.as_view() , name = 'questions'),
    path('api/questions/submit', QuestionSubmitAPIView.as_view() , name = 'questions_submit'),
    path('api/questions/create', CreateQuestionAPIView.as_view() , name = 'create-questions'),
    path('api/gameSummary', gameSummaryAPIView.as_view() , name = 'gameSummary'),

    path('dashboard/', overallSummaryView.as_view(), name='dashboard'),
    path('signup/', signup.as_view(), name='signup')
]
