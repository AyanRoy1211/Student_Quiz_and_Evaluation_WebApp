from django import forms
from .models import Quiz, Question, Choice


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'time_limit_minutes', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition',
                'placeholder': 'Enter quiz title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition',
                'placeholder': 'Enter quiz description',
                'rows': 3,
            }),
            'time_limit_minutes': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition',
                'min': 1,
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500',
            }),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'order']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition',
                'placeholder': 'Enter question text',
                'rows': 2,
            }),
            'order': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition',
                'min': 1,
            }),
        }


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition',
                'placeholder': 'Enter choice text',
            }),
            'is_correct': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-green-600 rounded border-gray-300 focus:ring-green-500',
            }),
        }


ChoiceFormSet = forms.inlineformset_factory(
    Question,
    Choice,
    form=ChoiceForm,
    extra=4,
    max_num=6,
    can_delete=True,
)
