# apps/users/api/serializers.py
from rest_framework import serializers
from apps.users.models import User, SecurityQuestion

class SecurityQuestionSerializer(serializers.Serializer):
    question = serializers.ChoiceField(choices=[q[0] for q in SecurityQuestion._meta.get_field('question').choices])
    answer   = serializers.CharField(max_length=255)

    def validate_answer(self, value):
        if not value.strip():
            raise serializers.ValidationError("La respuesta no puede estar vacía.")
        return value

class UserRegisterSerializer(serializers.ModelSerializer):
    security_questions = SecurityQuestionSerializer(many=True, write_only=True)

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'name', 'last_name', 'password', 'security_questions']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_security_questions(self, questions):
        if len(questions) != 3:
            raise serializers.ValidationError("Debés responder exactamente 3 preguntas de seguridad.")
        q_keys = [q['question'] for q in questions]
        if len(set(q_keys)) != 3:
            raise serializers.ValidationError("No podés repetir preguntas de seguridad.")
        return questions

    def create(self, validated_data):
        questions_data = validated_data.pop('security_questions')
        user = User.objects.create_user(**validated_data)

        for q_data in questions_data:
            SecurityQuestion.objects.create(
                user=user,
                question=q_data['question'],
                answer=SecurityQuestion.normalize(q_data['answer']),
            )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'name', 'last_name', 'image', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user