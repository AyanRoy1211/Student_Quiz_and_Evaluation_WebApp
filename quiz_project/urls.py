from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


def home_redirect(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    elif request.user.role == 'instructor':
        return redirect('instructor_dashboard')
    else:
        return redirect('student_dashboard')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('quizzes/', include('quizzes.urls')),
    path('api/', include('api.urls')),
    path('', home_redirect, name='home'),
]
