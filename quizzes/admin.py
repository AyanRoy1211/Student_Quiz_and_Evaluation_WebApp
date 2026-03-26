from django.contrib import admin
from .models import Quiz, Question, Choice, Attempt, Response


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'is_published', 'question_count', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title',)
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'order')
    list_filter = ('quiz',)
    inlines = [ChoiceInline]


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'total_questions', 'started_at')
    list_filter = ('quiz', 'started_at')
