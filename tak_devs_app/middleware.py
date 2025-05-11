# middleware.py
from django.http import JsonResponse
from django.contrib.auth import get_user_model

User = get_user_model()

class ApiKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip API key check for documentation routes
        if request.path.startswith('/swagger') or request.path.startswith('/redoc') or request.path.startswith('/admin'):
            return self.get_response(request)
            
        # Skip API key check for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            return self.get_response(request)
            
        # Skip for health check
        if request.path == '/health/':
            return self.get_response(request)
        
        # Check for API key
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            return JsonResponse({'detail': 'User API key Authentication credentials were not provided.'}, status=401)

        user = User.objects.filter(api_key=api_key).first()

        if not user:
            return JsonResponse({'detail': 'Invalid API key.'}, status=401)

        request.user = user

        return self.get_response(request)