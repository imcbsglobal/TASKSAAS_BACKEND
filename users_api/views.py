from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import jwt

from app1.models import AccUser   # existing model


@api_view(['GET'])
def list_users(request):
    """Return only id, role, client_id for logged user's client_id"""

    # 1. Read token
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({'success': False, 'error': 'Missing or invalid token'}, status=401)

    token = auth_header.split(' ')[1]

    # 2. Decode token
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        client_id = payload.get('client_id')
    except jwt.ExpiredSignatureError:
        return Response({'success': False, 'error': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'success': False, 'error': 'Invalid token'}, status=401)

    if not client_id:
        return Response({'success': False, 'error': 'client_id not found in token'}, status=401)

    # 3. Filter users by same client_id
    users = AccUser.objects.filter(client_id=client_id).values(
        'id', 'role', 'client_id'
    )

    return Response({
        'success': True,
        'client_id': client_id,
        'users': list(users)
    })
