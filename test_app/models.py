import uuid

from django.core import serializers
from django.db import models

# Create your models here.
from test_app.const import VARIANT_CHOICE


class Quiz(models.Model):
    quiz_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz_title = models.CharField(max_length=50, verbose_name='Тема тестирования')

    def __str__(self):
        return self.quiz_title

    class Meta:
        verbose_name = 'Тема тестирования'
        verbose_name_plural = 'Темы тестирования'


class Question(models.Model):
    question_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question_text = models.CharField(max_length=255, verbose_name='Текст вопроса')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='question', verbose_name='Тема вопроса')
    question_slug = models.SlugField(null=False, unique=True, verbose_name='Метка вопроса')

    def __str__(self):
        return self.question_text

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class Choice(models.Model):
    choice_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    choice_text = models.CharField(max_length=255)
    is_correct = models.BooleanField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choice')
    choice_variant = models.CharField(max_length=20, choices=VARIANT_CHOICE, verbose_name='Буква варианта ответа')

    def __str__(self):
        return self.choice_text

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'

