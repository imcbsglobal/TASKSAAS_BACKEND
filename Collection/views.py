from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import jwt

from app1.models import Collection



import jwt
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from app1.models import Collection
import jwt
from django.conf import settings


def get_user_from_token(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, None

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload.get('client_id'), payload.get('username')
    except:
        return None, None


@api_view(['POST'])
def create_collection(request):

    client_id, username = get_user_from_token(request)
    if not client_id:
        return Response({'success': False, 'error': 'Invalid token'}, status=401)

    data = request.data

    required_fields = ['code', 'name', 'amount', 'type']
    for field in required_fields:
        if not data.get(field):
            return Response({'success': False, 'error': f'{field} is required'}, status=400)

    collection = Collection.objects.create(
        code=data.get('code'),
        name=data.get('name'),
        place=data.get('place'),
        phone=data.get('phone'),
        amount=data.get('amount'),
        type=data.get('type'),
        client_id=client_id,

        cheque_no=data.get('cheque_no'),   # ✅ optional
        ref_no=data.get('ref_no'),         # ✅ optional
        remark=data.get('remark'),         # ✅ optional

        created_by=username,
        status='uploaded to server'
    )

    return Response({
        'success': True,
        'message': 'Collection added',
        'id': collection.id
    }, status=201)




# ---------------- GET API ----------------
@api_view(['GET'])
def list_collections(request):
    client_id, username = get_user_from_token(request)
    if not client_id:
        return Response({'success': False, 'error': 'Invalid token'}, status=401)

    qs = Collection.objects.filter(client_id=client_id).values(
        'id',
        'code',
        'name',
        'place',
        'phone',
        'amount',
        'type',
        'cheque_no',
        'ref_no',
        'remark',
        'status',
        'created_by',
        'created_date',
        'created_time',
        'uploaded_username',
        'uploaded_date',
        'uploaded_time'
    )

    return Response({
        'success': True,
        'data': list(qs)
    })



@api_view(['POST'])
def complete_collection(request):

    client_id, username = get_user_from_token(request)
    if not client_id:
        return Response({'success': False, 'error': 'Invalid token'}, status=401)

    collection_id = request.data.get('id')
    status_value = request.data.get('status')

    if not collection_id or not status_value:
        return Response({'success': False, 'error': 'id and status required'}, status=400)

    try:
        collection = Collection.objects.get(id=collection_id, client_id=client_id)
    except Collection.DoesNotExist:
        return Response({'success': False, 'error': 'Collection not found'}, status=404)

    # ✅ When status changes → auto fill uploaded details
    if status_value == 'completed' and collection.status != 'completed':
        now = timezone.now()
        collection.uploaded_date = now.date()
        collection.uploaded_time = now.time()
        collection.uploaded_username = username

    collection.status = status_value
    collection.save()

    return Response({
        'success': True,
        'message': 'Status updated',
        'status': collection.status
    })
