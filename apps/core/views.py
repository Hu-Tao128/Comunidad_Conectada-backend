from django.http import JsonResponse


def healthcheck(request):
    """Healthcheck endpoint para Railway."""
    return JsonResponse({"status": "healthy"})
