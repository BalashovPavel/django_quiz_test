from typing import List
from django import forms
from quiz.dto import QuestionDTO


class QuestionForm(forms.Form):
    def __init__(self, question: QuestionDTO, checked, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.fields["choices"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=[[choice.uuid, choice.text] for choice in question.choices],
            initial=checked
        )

    def is_valid(self):
        return True
