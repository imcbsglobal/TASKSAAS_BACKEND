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
        return None, JsonResponse(
            {'success': False, 'error': 'Missing or invalid authorization header'},
            status=401
        )

    token = auth_header.split(' ')[1]

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload, None

    except jwt.ExpiredSignatureError:
        return None, JsonResponse(
            {'success': False, 'error': 'Token expired'},
            status=401
        )
    except jwt.InvalidTokenError as e:
        return None, JsonResponse(
            {'success': False, 'error': str(e)},
            status=401
        )



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

        if not data.get("device_id"):
            return JsonResponse({
                "success": False,
                "error": "device_id is required"
            }, status=400)

        items = data.get("items", [])
        if not items:
            return JsonResponse({
                "success": False,
                "error": "items list is required"
            }, status=400)

        # ✅ Generate ONE order_id
        import uuid
        order_id = f"ORD-{uuid.uuid4().hex[:10].upper()}"

        created_items = []

        for item in items:
            order = ItemOrders.objects.create(
                order_id=order_id,

                customer_name=data.get("customer_name"),
                customer_code=data.get("customer_code"),
                area=data.get("area"),

                product_name=item.get("product_name"),
                item_code=item.get("item_code"),
                barcode=item.get("barcode"),

                payment_type=data.get("payment_type"),
                price=item.get("price"),
                quantity=item.get("quantity"),
                amount=item.get("amount"),

                client_id=payload.get("client_id"),
                username=data.get("username"),
                remark=data.get("remark"),

                device_id=data.get("device_id")
            )

            created_items.append({
                "product_name": order.product_name,
                "item_code": order.item_code,
                "quantity": order.quantity,
                "amount": float(order.amount)
            })

        return JsonResponse({
            "success": True,
            "message": "Order created successfully",
            "order_id": order_id,
            "items": created_items
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

    client_id = payload.get("client_id")

    orders = ItemOrders.objects.filter(client_id=client_id).order_by('-id')

    grouped_orders = {}

    for o in orders:
        if o.order_id not in grouped_orders:
            grouped_orders[o.order_id] = {
                "order_id": o.order_id,
                "customer_name": o.customer_name,
                "customer_code": o.customer_code,
                "area": o.area,
                "payment_type": o.payment_type,
                "username": o.username,
                "remark": o.remark,
                "created_date": o.created_date.strftime('%Y-%m-%d'),
                "created_time": o.created_time.strftime('%H:%M:%S'),
                "items": []
            }

        grouped_orders[o.order_id]["items"].append({
            "product_name": o.product_name,
            "item_code": o.item_code,
            "barcode": o.barcode,
            "price": float(o.price),
            "quantity": o.quantity,
            "amount": float(o.amount)
        })

    return JsonResponse({
        "success": True,
        "total_orders": len(grouped_orders),
        "orders": list(grouped_orders.values())
    })


from django.utils import timezone
@csrf_exempt
@require_http_methods(["POST"])
def change_order_status(request):
    payload, error = get_client_from_token(request)
    if error:
        return error

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON"
        }, status=400)

    order_id = data.get("order_id")
    status_value = data.get("status")

    # ✅ ALLOWED STATUS LIST (SAME AS COLLECTION)
    ALLOWED_STATUSES = ['uploaded to server', 'completed']

    if not order_id or not status_value:
        return JsonResponse({
            "success": False,
            "error": "order_id and status are required"
        }, status=400)

    if status_value not in ALLOWED_STATUSES:
        return JsonResponse({
            "success": False,
            "error": f"Invalid status. Allowed values: {ALLOWED_STATUSES}"
        }, status=400)

    try:
        order = ItemOrders.objects.get(
            order_id=order_id,
            client_id=payload.get("client_id")
        )

        from django.utils import timezone
        now = timezone.localtime()

        order.status = status_value
        order.status_changed_date = now.date()
        order.status_changed_time = now.time()
        order.status_changed_by = payload.get("username")
        order.save()

        return JsonResponse({
            "success": True,
            "message": "Order status updated",
            "order_id": order.order_id,
            "status": order.status
        })

    except ItemOrders.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Order not found"
        }, status=404)
