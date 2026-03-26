from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'quizzes', views.QuizViewSet, basename='api-quiz')
router.register(r'attempts', views.AttemptViewSet, basename='api-attempt')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('submit/', views.submit_attempt, name='api_submit_attempt'),
    path('dashboard/', views.dashboard_api, name='api_dashboard'),
]
