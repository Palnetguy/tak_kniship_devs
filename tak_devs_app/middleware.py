# middleware.py
from django.http import JsonResponse
from django.contrib.auth import get_user_model

User = get_user_model()

class ApiKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            return JsonResponse({'detail': 'User API key Authentication credentials were not provided.'}, status=401)

        user = User.objects.filter(api_key=api_key).first()

        if not user:
            return JsonResponse({'detail': 'Invalid API key.'}, status=401)

        request.user = user

        return self.get_response(request)
