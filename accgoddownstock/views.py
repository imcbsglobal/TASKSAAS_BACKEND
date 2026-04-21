from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import jwt

from app1.models import AccGoddownStock, AccProduct, AccGoddown


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

        data_queryset = AccGoddownStock.objects.filter(
            client_id=client_id
        ).values(
            'id',
            'goddownid',
            'product',
            'quantity',
            'barcode'
        ).order_by('product')

        data = list(data_queryset)

        # Optimization: Fetch product and godown names in bulk
        product_codes = [item['product'] for item in data if item['product']]
        godown_ids = [item['goddownid'] for item in data if item['goddownid']]

        # Create dictionaries for mapping
        product_map = {
            p['code']: p['name']
            for p in AccProduct.objects.filter(
                code__in=product_codes, client_id=client_id
            ).values('code', 'name')
        }

        godown_map = {
            g['goddownid']: g['name']
            for g in AccGoddown.objects.filter(
                goddownid__in=godown_ids, client_id=client_id
            ).values('goddownid', 'name')
        }

        # Add names to the response 
        for item in data:
            item['product_name'] = product_map.get(item['product'], None)
            item['goddown_name'] = godown_map.get(item['goddownid'], None)

        return Response({
            'success': True,
            'client_id': client_id,
            'data': data
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)