from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import jwt

from app1.models import AccMaster   # existing model


@api_view(['GET'])
def get_area_list(request):
    """Return unique area names based on logged user's client_id"""

    # 1) Read Bearer token
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({'success': False, 'error': 'Missing or invalid token'}, status=401)

    token = auth_header.split(' ')[1]

    # 2) Decode token
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        client_id = payload.get('client_id')
    except jwt.ExpiredSignatureError:
        return Response({'success': False, 'error': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'success': False, 'error': 'Invalid token'}, status=401)

    # 3) Missing client_id
    if not client_id:
        return Response({'success': False, 'error': 'client_id missing in token'}, status=401)

    # 4) Get unique area names
    areas = (
        AccMaster.objects
        .filter(client_id=client_id)
        .exclude(area__isnull=True)
        .exclude(area__exact='')
        .values_list('area', flat=True)
        .distinct()
    )

    return Response({
        'success': True,
        'client_id': client_id,
        'areas': list(areas)
    })
