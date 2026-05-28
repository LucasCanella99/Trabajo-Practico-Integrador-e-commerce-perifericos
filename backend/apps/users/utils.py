

from django.http import JsonResponse

def lockout_response(request, credentials, *args, **kwargs):
    return JsonResponse(
        {
            "error": "Cuenta bloqueada temporalmente.",
            "detail": "Demasiados intentos fallidos. Intentá de nuevo en 15 minutos."
        },
        status=403
    )