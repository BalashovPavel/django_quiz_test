from .dto import ChoiceDTO, QuestionDTO, QuizDTO, AnswerDTO, AnswersDTO
from typing import List, Set


class QuizResultService():
    def __init__(self, quiz_dto: QuizDTO, answers_dto: AnswersDTO):
        self.quiz_dto = quiz_dto
        self.answers_dto = answers_dto

    def get_result(self) -> float:
        result = 0
        test_dict = dict()
        questions = self.quiz_dto.questions
        for question in questions:
            true_answers = []
            for choice in question.choices:
                if choice.is_correct:
                    true_answers.append(choice.uuid)
            test_dict[question.uuid] = true_answers
        for answer in self.answers_dto.answers:
            if true_answers := test_dict.get(answer.question_uuid):
                if true_answers == list(answer.choices):
                    result += 1
        return round(result / len(test_dict), 2)
