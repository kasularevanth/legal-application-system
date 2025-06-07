

# ============ core/middleware.py ============
import jwt
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.http import JsonResponse
from apps.authentication.models import User
import logging

logger = logging.getLogger(__name__)

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip JWT authentication for certain paths
        skip_paths = [
            '/admin/',
            '/api/auth/login/',
            '/api/auth/register/',
            '/api/forms/knowledge-base/',  # Public knowledge base
        ]
        
        if any(request.path.startswith(path) for path in skip_paths):
            return self.get_response(request)

        # Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            try:
                payload = jwt.decode(
                    token,
                    settings.JWT_SECRET_KEY,
                    algorithms=[settings.JWT_ALGORITHM]
                )
                
                user = User.objects.get(id=payload['user_id'])
                request.user = user
                
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist) as e:
                if request.path.startswith('/api/') and not any(request.path.startswith(path) for path in skip_paths):
                    return JsonResponse(
                        {'error': 'Invalid or expired token'},
                        status=401
                    )
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()

        return self.get_response(request)