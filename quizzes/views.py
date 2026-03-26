from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import models
from django.db.models import Avg, Count
from .models import Quiz, Question, Choice, Attempt, Response
from .forms import QuizForm, QuestionForm, ChoiceFormSet
from accounts.decorators import instructor_required, student_required


# ─── Instructor Views ───────────────────────────────────────

@login_required
@instructor_required
def instructor_dashboard(request):
    quizzes = Quiz.objects.filter(instructor=request.user).annotate(
        attempt_count=Count('attempts'),
        avg_score=Avg('attempts__score'),
    )
    context = {
        'quizzes': quizzes,
        'total_quizzes': quizzes.count(),
        'published_count': quizzes.filter(is_published=True).count(),
    }
    return render(request, 'quizzes/instructor_dashboard.html', context)


@login_required
@instructor_required
def quiz_create(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.instructor = request.user
            quiz.save()
            messages.success(request, 'Quiz created! Now add questions.')
            return redirect('quiz_add_question', quiz_id=quiz.id)
    else:
        form = QuizForm()
    return render(request, 'quizzes/quiz_form.html', {'form': form, 'title': 'Create Quiz'})


@login_required
@instructor_required
def quiz_edit(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, instructor=request.user)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz updated successfully!')
            return redirect('instructor_dashboard')
    else:
        form = QuizForm(instance=quiz)
    return render(request, 'quizzes/quiz_form.html', {'form': form, 'title': 'Edit Quiz', 'quiz': quiz})


@login_required
@instructor_required
def quiz_delete(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, instructor=request.user)
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Quiz deleted.')
        return redirect('instructor_dashboard')
    return render(request, 'quizzes/quiz_confirm_delete.html', {'quiz': quiz})


@login_required
@instructor_required
def quiz_add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, instructor=request.user)
    if request.method == 'POST':
        q_form = QuestionForm(request.POST)
        if q_form.is_valid():
            question = q_form.save(commit=False)
            question.quiz = quiz
            if not question.order:
                question.order = quiz.questions.count() + 1
            question.save()
            c_formset = ChoiceFormSet(request.POST, instance=question)
            if c_formset.is_valid():
                c_formset.save()
                messages.success(request, 'Question added!')
                return redirect('quiz_add_question', quiz_id=quiz.id)
            else:
                question.delete()
                messages.error(request, 'Please fix errors in the choices.')
        else:
            c_formset = ChoiceFormSet(request.POST)
    else:
        q_form = QuestionForm(initial={'order': quiz.questions.count() + 1})
        c_formset = ChoiceFormSet()

    questions = quiz.questions.prefetch_related('choices').all()
    return render(request, 'quizzes/question_form.html', {
        'quiz': quiz,
        'q_form': q_form,
        'c_formset': c_formset,
        'questions': questions,
    })


@login_required
@instructor_required
def question_delete(request, question_id):
    question = get_object_or_404(Question, id=question_id, quiz__instructor=request.user)
    quiz_id = question.quiz.id
    question.delete()
    messages.success(request, 'Question deleted.')
    return redirect('quiz_add_question', quiz_id=quiz_id)


@login_required
@instructor_required
def quiz_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, instructor=request.user)
    attempts = Attempt.objects.filter(quiz=quiz).select_related('student').order_by('-started_at')
    avg_score = attempts.aggregate(avg=Avg('score'))['avg'] or 0
    context = {
        'quiz': quiz,
        'attempts': attempts,
        'avg_score': round(avg_score, 1),
        'total_attempts': attempts.count(),
    }
    return render(request, 'quizzes/quiz_results.html', context)


# ─── Student Views ──────────────────────────────────────────

@login_required
@student_required
def student_dashboard(request):
    attempts = Attempt.objects.filter(student=request.user).select_related('quiz')
    total_attempts = attempts.count()
    avg_percentage = 0
    if total_attempts > 0:
        avg_percentage = round(sum(a.percentage for a in attempts) / total_attempts, 1)

    available_quizzes = Quiz.objects.filter(is_published=True).annotate(
        attempt_count=Count('attempts', filter=models.Q(attempts__student=request.user))
    )

    context = {
        'attempts': attempts[:10],
        'total_attempts': total_attempts,
        'avg_percentage': avg_percentage,
        'available_quizzes': available_quizzes,
    }
    return render(request, 'quizzes/student_dashboard.html', context)


@login_required
@student_required
def quiz_list(request):
    quizzes = Quiz.objects.filter(is_published=True).select_related('instructor').annotate(
        question_count_val=Count('questions')
    )
    return render(request, 'quizzes/quiz_list.html', {'quizzes': quizzes})


@login_required
@student_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, is_published=True)
    past_attempts = Attempt.objects.filter(student=request.user, quiz=quiz)
    context = {
        'quiz': quiz,
        'past_attempts': past_attempts,
    }
    return render(request, 'quizzes/quiz_detail.html', context)


@login_required
@student_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, is_published=True)
    questions = quiz.questions.prefetch_related('choices').all()

    if not questions.exists():
        messages.warning(request, 'This quiz has no questions yet.')
        return redirect('quiz_detail', quiz_id=quiz.id)

    if request.method == 'POST':
        attempt = Attempt.objects.create(
            student=request.user,
            quiz=quiz,
            total_questions=questions.count(),
        )
        score = 0
        for question in questions:
            choice_id = request.POST.get(f'question_{question.id}')
            selected_choice = None
            is_correct = False
            if choice_id:
                try:
                    selected_choice = Choice.objects.get(id=choice_id, question=question)
                    is_correct = selected_choice.is_correct
                except Choice.DoesNotExist:
                    pass
            if is_correct:
                score += 1
            Response.objects.create(
                attempt=attempt,
                question=question,
                selected_choice=selected_choice,
                is_correct=is_correct,
            )
        attempt.score = score
        attempt.completed_at = timezone.now()
        attempt.save()
        return redirect('quiz_result', attempt_id=attempt.id)

    return render(request, 'quizzes/take_quiz.html', {'quiz': quiz, 'questions': questions})


@login_required
@student_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(Attempt, id=attempt_id, student=request.user)
    responses = attempt.responses.select_related('question', 'selected_choice').all()
    questions_with_responses = []
    for resp in responses:
        correct_choice = resp.question.choices.filter(is_correct=True).first()
        questions_with_responses.append({
            'question': resp.question,
            'selected': resp.selected_choice,
            'correct': correct_choice,
            'is_correct': resp.is_correct,
        })
    context = {
        'attempt': attempt,
        'questions_with_responses': questions_with_responses,
    }
    return render(request, 'quizzes/quiz_result.html', context)
