from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import jwt

from app1.models import Collection


def get_client_id_from_token(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION')

    if not auth_header or not auth_header.startswith('Bearer '):
        return None, Response(
            {'success': False, 'error': 'Missing or invalid authorization header'},
            status=401
        )

    token = auth_header.split(' ')[1]

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload.get('client_id'), None
    except jwt.ExpiredSignatureError:
        return None, Response({'success': False, 'error': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return None, Response({'success': False, 'error': 'Invalid token'}, status=401)


# ---------------- POST API ----------------
@api_view(['POST'])
def create_collection(request):
    client_id, error = get_client_id_from_token(request)
    if error:
        return error

    data = request.data

    required_fields = ['code', 'name', 'amount', 'type']
    for field in required_fields:
        if not data.get(field):
            return Response(
                {'success': False, 'error': f'{field} is required'},
                status=400
            )

    collection = Collection.objects.create(
        code=data.get('code'),
        name=data.get('name'),
        place=data.get('place'),
        phone=data.get('phone'),
        amount=data.get('amount'),
        type=data.get('type'),
        client_id=client_id
    )

    return Response({
        'success': True,
        'message': 'Collection created successfully',
        'id': collection.id
    }, status=201)


# ---------------- GET API ----------------
@api_view(['GET'])
def list_collections(request):
    client_id, error = get_client_id_from_token(request)
    if error:
        return error

    qs = Collection.objects.filter(client_id=client_id).values(
        'id', 'code', 'name', 'place', 'phone', 'amount', 'type'
    )

    return Response({
        'success': True,
        'data': list(qs)
    })
