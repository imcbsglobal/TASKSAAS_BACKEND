from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from app1.models import AccMaster
import jwt
from django.conf import settings


@api_view(['GET'])
def get_debtors_list(request):
    try:
        # -------------------------
        # AUTH CHECK
        # -------------------------
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response(
                {'success': False, 'error': 'Missing or invalid authorization header'},
                status=401
            )

        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        client_id = payload.get('client_id')

        if not client_id:
            return Response(
                {'success': False, 'error': 'Invalid token'},
                status=401
            )

        # -------------------------
        # FETCH DEBTORS (ADDED remarkcolumntitle)
        # -------------------------
        debtors = (
            AccMaster.objects
            .filter(client_id=client_id)
            .values(
                'code',
                'name',
                'place',
                'phone2',
                'debit',
                'credit',
                'area',
                'super_code',
                'remarkcolumntitle'   # ✅ NEW FIELD
            )
        )

        # -------------------------
        # BUILD RESPONSE
        # -------------------------
        result = []
        for d in debtors:
            debit = float(d['debit'] or 0)
            credit = float(d['credit'] or 0)
            balance = round(debit - credit, 2)

            result.append({
                'code': d['code'],
                'name': d['name'],
                'place': d['place'],
                'area': d['area'],
                'phone': d['phone2'],
                'super_code': d['super_code'],
                'remarkcolumntitle': d['remarkcolumntitle'],  # ✅ RETURNED
                'balance': balance,
                'client_id': client_id
            })

        return Response({
            'success': True,
            'data': result
        })

    except Exception as e:
        return Response(
            {'success': False, 'error': str(e)},
            status=500
        )
