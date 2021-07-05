from django.contrib import admin

# Register your models here.
from test_app.models import Quiz, Question, Choice


class QuizAdmin(admin.ModelAdmin):
    list_display = ['quiz_title']
    search_fields = ['quiz_title']


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'question_slug', 'quiz']
    list_filter = ['quiz']
    search_fields = ['quiz', 'question_text']


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['choice_text', 'is_correct', 'choice_variant', 'question']
    list_filter = ['is_correct', 'question']
    search_fields = ['choice_text', 'question']


admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
