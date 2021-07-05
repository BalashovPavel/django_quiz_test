from django.urls import path
from test_app.views import QuizHome, QuizListTests, TestTheme, TestQuestion, test_result

urlpatterns = [
    path('', QuizHome.as_view(), name='home'),
    path('list_tests/', QuizListTests.as_view(), name='list_tests'),
    path('list_tests/<str:slug>/', TestTheme.as_view(), name='test_theme'),
    path('list_tests/<str:slug>/<int:num_question>/', TestQuestion.as_view(), name='test_questions'),
    path('list_tests/<str:slug>/result/', test_result, name='test_result'),
]
