from typing import List, Type

from django.contrib.sessions.models import Session
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView, ListView, DetailView, FormView

from quiz.dto import QuizDTO, QuestionDTO, ChoiceDTO, AnswerDTO, AnswersDTO
from quiz.services import QuizResultService
from test_app.forms import QuestionForm
from test_app.models import Quiz, Question, Choice


class QuizHome(TemplateView):
    template_name = "test_app/index.html"

    def dispatch(self, request, *args, **kwargs):
        self.request.session.flush()
        return super(QuizHome, self).dispatch(request, *args, **kwargs)


def create_quiz_dto(quiz_uuid: str) -> QuizDTO:
    quiz = get_object_or_404(Quiz, quiz_uuid=quiz_uuid)
    return QuizDTO(
        str(quiz.quiz_uuid),
        quiz.quiz_title,
        create_question_dto(quiz.quiz_uuid)
    )


def create_question_dto(quiz_uuid: str) -> list[QuestionDTO]:
    questions = Question.objects.filter(quiz=quiz_uuid).order_by('question_slug')
    questions_list = []
    for q in questions:
        q_dto: QuestionDTO = QuestionDTO(
            str(q.question_uuid),
            q.question_text,
            create_choice_dto(q.question_uuid)
        )
        questions_list.append(q_dto)
    return questions_list


def create_choice_dto(question_uuid: str) -> list[ChoiceDTO]:
    choices = Choice.objects.filter(question=question_uuid).order_by('choice_variant')
    choices_list = []
    for c in choices:
        c_dto: ChoiceDTO = ChoiceDTO(
            str(c.choice_uuid),
            c.choice_text,
            c.is_correct
        )
        choices_list.append(c_dto)
    return choices_list


class QuizListTests(ListView):
    model = Quiz
    template_name = "test_app/list-tests.html"
    context_object_name = "list"

    def dispatch(self, request, *args, **kwargs):
        self.request.session.flush()
        return super(QuizListTests, self).dispatch(request, *args, **kwargs)


class TestTheme(DetailView):
    model = Quiz
    template_name = "test_app/test-theme.html"
    context_object_name = "theme"
    slug_field = "quiz_uuid"

    def dispatch(self, request, *args, **kwargs):
        self.request.session.flush()
        return super(TestTheme, self).dispatch(request, *args, **kwargs)


class TestQuestion(FormView):
    template_name = 'test_app/test-questions.html'
    form_class = QuestionForm

    def dispatch(self, request, *args, **kwargs):
        self.quiz_uuid: str = self.kwargs['slug']
        self.quiz_dto: QuizDTO = create_quiz_dto(self.quiz_uuid)
        self.num_question: int = self.kwargs['num_question']
        request.session.modified = True
        if self.quiz_dto.uuid not in self.request.session:
            self.request.session[self.quiz_dto.uuid] = dict(answers={})
            self.request.session[self.quiz_dto.uuid].pop('test_result', None)
        return super(TestQuestion, self).dispatch(request, *args, **kwargs)

    def get_form(self, *args, **kwargs):
        form_class: Type[QuestionForm] = self.form_class
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        form_kwargs = super(TestQuestion, self).get_form_kwargs()
        self.question_dto: QuestionDTO = self.quiz_dto.questions[self.num_question - 1]
        checked: List[str] = self.request.session[self.quiz_dto.uuid][
            'answers'
        ].get(self.question_dto.uuid, [])
        form_kwargs.update({
            'question': self.question_dto,
            'checked': checked
        })
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super(TestQuestion, self).get_context_data(**kwargs)
        context['quiz']: QuizDTO = self.quiz_dto
        context['question']: QuestionDTO = self.question_dto
        context['num_question']: int = self.num_question
        context['max_num']: int = len(self.quiz_dto.questions)
        context['prev_question']: int = self.num_question - 1
        return context

    def form_valid(self, form):
        self.request.session[self.quiz_dto.uuid]['answers'][
            self.question_dto.uuid
        ] = dict(form.data).get('choices', [])
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        if self.num_question == len(self.quiz_dto.questions):
            self.save_test()
            return reverse('test_result', kwargs={
                'slug': self.quiz_uuid
            })
        return reverse('test_questions', kwargs={
            'slug': self.quiz_uuid,
            'num_question': self.num_question + 1
        })

    def create_answers_dto(self) -> AnswersDTO:
        question_uuids: List[str] = self.request.session[self.quiz_dto.uuid]['answers'].keys()
        answers: List[AnswerDTO] = []
        for question_uuid in question_uuids:
            answer_dto: AnswerDTO = AnswerDTO(
                question_uuid,
                self.request.session[self.quiz_dto.uuid]['answers'][question_uuid]
            )
            answers.append(answer_dto)
        answers_dto: AnswersDTO = AnswersDTO(self.quiz_dto.uuid, answers)
        return answers_dto

    def save_test(self):
        answers_dto: AnswersDTO = self.create_answers_dto()
        quiz_result_service = QuizResultService(self.quiz_dto, answers_dto)
        result: float = quiz_result_service.get_result()
        self.request.session[self.quiz_dto.uuid]['test_result'] = result


def test_result(request, slug: str):
    quiz = get_object_or_404(Quiz, quiz_uuid=slug)
    questions = Question.objects.filter(quiz=slug).order_by('question_slug')
    result = request.session[slug]['test_result']
    checked = []
    for question in questions:
        checked_uuid_list = (request.session[slug]['answers'][str(question.question_uuid)])
        choice_variant = []
        for ch in checked_uuid_list:
            choice_variant.append(get_object_or_404(Choice, choice_uuid=ch).choice_variant)
        checked.append(choice_variant)
    return render(request, 'test_app/test-result.html', {
        'quiz': quiz,
        'result': result,
        'checked': checked
    })
