import json
import jwt
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.response import Response
from .models import ItemOrders


# --------------------------------------------------
# TOKEN VALIDATION
# --------------------------------------------------
def get_client_from_token(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION')

    if not auth_header or not auth_header.startswith('Bearer '):
        return None, Response(
            {'success': False, 'error': 'Missing or invalid authorization header'},
            status=401
        )

    token = auth_header.split(' ')[1]

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload, None

    except jwt.ExpiredSignatureError:
        return None, Response({'success': False, 'error': 'Token expired'}, status=401)
    except jwt.InvalidTokenError as e:
        return None, Response({'success': False, 'error': str(e)}, status=401)


# --------------------------------------------------
# CREATE ITEM ORDER (POST)
# --------------------------------------------------
@csrf_exempt
@require_http_methods(["POST"])
def create_item_order(request):
    payload, error = get_client_from_token(request)
    if error:
        return error

    try:
        data = json.loads(request.body)

        order = ItemOrders.objects.create(
            customer_name=data.get("customer_name"),
            customer_code=data.get("customer_code"),
            area=data.get("area"),

            product_name=data.get("product_name"),
            item_code=data.get("item_code"),
            barcode=data.get("barcode"),

            payment_type=data.get("payment_type"),
            price=data.get("price"),
            amount=data.get("amount"),
            quantity=data.get("quantity"),

            client_id=data.get("client_id"),
            username=data.get("username"),
            remark=data.get("remark"),
        )

        return JsonResponse({
            "success": True,
            "message": "Order created successfully",
            "order_id": order.id
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)


# --------------------------------------------------
# LIST ITEM ORDERS (GET)
# --------------------------------------------------
@require_http_methods(["GET"])
def item_orders_list(request):
    payload, error = get_client_from_token(request)
    if error:
        return error

    client_id = request.GET.get("client_id")

    orders = ItemOrders.objects.all()
    if client_id:
        orders = orders.filter(client_id=client_id)

    data = []
    for o in orders:
        data.append({
            "id": o.id,
            "client_id": o.client_id,

            "customer_name": o.customer_name,
            "customer_code": o.customer_code,
            "area": o.area,

            "product_name": o.product_name,
            "item_code": o.item_code,
            "barcode": o.barcode,

            "payment_type": o.payment_type,
            "price": float(o.price),
            "amount": float(o.amount),
            "quantity": o.quantity,

            "username": o.username,
            "remark": o.remark,
            "date": o.created_date.strftime('%Y-%m-%d'),
            "time": o.created_time.strftime('%H:%M:%S'),
        })

    return JsonResponse({
        "success": True,
        "total": len(data),
        "orders": data
    })
