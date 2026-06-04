from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from simple_history.models import HistoricalRecords

class UserManager(BaseUserManager):
    def _create_user(self, username, email, name, last_name, password, is_staff, is_superuser, **extra_fields):
        user = self.model(username=username, email=email, name=name, last_name=last_name, is_staff=is_staff, is_superuser=is_superuser, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, username, email, name, last_name, password=None, **extra_fields):
        return self._create_user(username, email, name, last_name, password, False, False, **extra_fields)

    def create_superuser(self, username, email, name, last_name, password=None, **extra_fields):
        return self._create_user(username, email, name, last_name, password, True, True, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField('Correo Electrónico', max_length=255, unique=True)
    name = models.CharField('Nombres', max_length=255, blank=True, null=True)
    last_name = models.CharField('Apellidos', max_length=255, blank=True, null=True)
    image = models.ImageField('Imagen de perfil', upload_to='perfil/', max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    historical = HistoricalRecords()
    objects = UserManager()

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'name', 'last_name']

    def __str__(self):
        return f'{self.name} {self.last_name}'

# --- NUEVO: PREGUNTAS DE SEGURIDAD ---
SECURITY_QUESTIONS = [
    ('q1', '¿Cuál es el nombre de tu primera mascota?'),
    ('q2', '¿En qué ciudad naciste?'),
    ('q3', '¿Cuál es el nombre de tu madre?'),
    ('q4', '¿Cuál es tu color favorito?'),
]

class SecurityQuestion(models.Model):
    QUESTION_CHOICES = [
        ('mascota', '¿Nombre de tu primera mascota?'),
        ('ciudad',  '¿Ciudad donde naciste?'),
        ('madre',   '¿Nombre de tu madre?'),
    ]
    user     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='security_questions')
    question = models.CharField(max_length=50, choices=QUESTION_CHOICES)
    answer   = models.CharField(max_length=255)

    class Meta:
        unique_together = [('user', 'question')]  # ← Recuperar esta restricción

    @staticmethod
    def normalize(raw_answer):
        return raw_answer.strip().lower()

    def check_answer(self, raw_answer):
        return self.normalize(raw_answer) == self.answer
