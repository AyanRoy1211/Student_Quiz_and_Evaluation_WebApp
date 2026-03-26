from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response as DRFResponse
from django.utils import timezone

from accounts.models import User
from quizzes.models import Quiz, Question, Choice, Attempt, Response
from .serializers import (
    UserSerializer, QuizListSerializer, QuizDetailSerializer,
    AttemptSerializer, SubmitAttemptSerializer, DashboardSerializer
)
from .permissions import IsInstructor, IsStudent


class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizListSerializer

    def get_queryset(self):
        if self.request.user.role == 'instructor':
            return Quiz.objects.filter(instructor=self.request.user)
        return Quiz.objects.filter(is_published=True)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return QuizDetailSerializer
        return QuizListSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsInstructor()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)


class AttemptViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AttemptSerializer

    def get_queryset(self):
        return Attempt.objects.filter(student=self.request.user).select_related('quiz')


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStudent])
def submit_attempt(request):
    serializer = SubmitAttemptSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    quiz = Quiz.objects.get(id=serializer.validated_data['quiz_id'])
    questions = quiz.questions.prefetch_related('choices').all()

    attempt = Attempt.objects.create(
        student=request.user,
        quiz=quiz,
        total_questions=questions.count(),
    )

    score = 0
    answers = {a['question_id']: a['choice_id'] for a in serializer.validated_data['answers']}

    for question in questions:
        choice_id = answers.get(question.id)
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

    return DRFResponse(AttemptSerializer(attempt).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_api(request):
    attempts = Attempt.objects.filter(student=request.user).select_related('quiz')
    total = attempts.count()
    avg = 0
    if total > 0:
        avg = round(sum(a.percentage for a in attempts) / total, 1)

    data = {
        'total_attempts': total,
        'average_percentage': avg,
        'recent_attempts': AttemptSerializer(attempts[:10], many=True).data,
    }
    return DRFResponse(data)
