from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import jwt

from app1.models import AccGoddownStock


@api_view(['GET'])
def get_goddown_stock(request):
    try:
        auth_header = request.META.get('HTTP_AUTHORIZATION')

        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({
                'success': False,
                'error': 'Missing or invalid authorization header'
            }, status=401)

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            client_id = payload.get('client_id')

            if not client_id:
                return Response({
                    'success': False,
                    'error': 'Invalid token: missing client_id'
                }, status=401)

        except jwt.ExpiredSignatureError:
            return Response({
                'success': False,
                'error': 'Token expired'
            }, status=401)

        except jwt.InvalidTokenError:
            return Response({
                'success': False,
                'error': 'Invalid token'
            }, status=401)

        data = AccGoddownStock.objects.filter(
            client_id=client_id
        ).values(
            'id',
            'goddownid',
            'product',
            'quantity',
            'barcode'
        ).order_by('product')

        return Response({
            'success': True,
            'client_id': client_id,
            'data': list(data)
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)