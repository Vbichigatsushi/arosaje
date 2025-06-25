import jwt
import datetime
from django.conf import settings

from django.shortcuts import redirect
from .jwt_utils import decode_jwt
from pageprincipale.models import Utilisateur

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

def generate_jwt(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def jwt_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        token = request.COOKIES.get('jwt')
        if not token:
            return redirect('login')

        decoded = decode_jwt(token)
        if not decoded:
            return redirect('login')

        try:
            user = Utilisateur.objects.get(id=decoded['user_id'])
            request.user = user  
            return view_func(request, *args, **kwargs)
        except Utilisateur.DoesNotExist:
            return redirect('login')
    return _wrapped_view