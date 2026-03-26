from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from .models import User
from quizzes.models import Quiz, Attempt


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Your account has been created.')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def profile_view(request):
    context = {}
    if request.user.is_student:
        attempts = Attempt.objects.filter(student=request.user).select_related('quiz').order_by('-started_at')
        context['attempts'] = attempts
        context['total_quizzes_taken'] = attempts.values('quiz').distinct().count()
        if attempts.exists():
            context['avg_score'] = round(sum(a.percentage for a in attempts) / attempts.count(), 1)
        else:
            context['avg_score'] = 0
    elif request.user.is_instructor:
        quizzes = Quiz.objects.filter(instructor=request.user)
        context['quizzes'] = quizzes
        context['total_quizzes'] = quizzes.count()
    return render(request, 'accounts/profile.html', context)


@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('home')
    context = {
        'total_users': User.objects.count(),
        'total_students': User.objects.filter(role='student').count(),
        'total_instructors': User.objects.filter(role='instructor').count(),
        'total_quizzes': Quiz.objects.count(),
        'total_attempts': Attempt.objects.count(),
        'recent_users': User.objects.order_by('-date_joined')[:5],
        'recent_attempts': Attempt.objects.select_related('student', 'quiz').order_by('-started_at')[:10],
    }
    return render(request, 'accounts/admin_dashboard.html', context)
