# apps/users/signals.py

from django_rest_passwordreset.signals import reset_password_token_created
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

@receiver(reset_password_token_created)
def enviar_mail_recuperacion(sender, instance, reset_password_token, **kwargs):
    
    usuario = reset_password_token.user
    token   = reset_password_token.key

    frontend_url = getattr(settings, 'PASSWORD_RESET_FRONTEND_URL', 'http://localhost:5173/reset-confirm/')
    reset_url = f"{frontend_url}?token={token}"

    send_mail(
        subject="Recuperá tu contraseña",
        message=(
            f"Hola {usuario.name},\n\n"                        
            f"Hacé clic en el siguiente link para recuperar tu contraseña:\n\n"
            f"{reset_url}\n\n"
            f"Si no lo solicitaste, ignorá este mail."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[usuario.email],
        fail_silently=False,
    )