from rest_framework import serializers
from accounts.models import User
from quizzes.models import Quiz, Question, Choice, Attempt, Response


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = ['id']


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'order', 'choices']


class QuizListSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    question_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'instructor_name', 'question_count',
                  'time_limit_minutes', 'is_published', 'created_at']


class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'instructor_name', 'questions',
                  'time_limit_minutes', 'is_published', 'created_at']


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ['question', 'selected_choice', 'is_correct']
        read_only_fields = ['is_correct']


class AttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    percentage = serializers.FloatField(read_only=True)
    responses = ResponseSerializer(many=True, read_only=True)

    class Meta:
        model = Attempt
        fields = ['id', 'quiz', 'quiz_title', 'score', 'total_questions',
                  'percentage', 'started_at', 'completed_at', 'responses']
        read_only_fields = ['id', 'score', 'total_questions', 'started_at', 'completed_at']


class SubmitAttemptSerializer(serializers.Serializer):
    quiz_id = serializers.IntegerField()
    answers = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField())
    )

    def validate_quiz_id(self, value):
        if not Quiz.objects.filter(id=value, is_published=True).exists():
            raise serializers.ValidationError("Quiz not found or not published.")
        return value


class DashboardSerializer(serializers.Serializer):
    total_attempts = serializers.IntegerField()
    average_percentage = serializers.FloatField()
    recent_attempts = AttemptSerializer(many=True)
