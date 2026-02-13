import json
import jwt
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.response import Response
from .models import Sales


# --------------------------------------------------
# TOKEN VALIDATION
# --------------------------------------------------
import jwt
from django.conf import settings


def get_client_from_token(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION')

    if not auth_header:
        return None, "Authorization header missing"

    if not auth_header.startswith("Bearer "):
        return None, "Invalid authorization format"

    token = auth_header.split(" ", 1)[1]

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        return payload, None

    except jwt.ExpiredSignatureError:
        return None, "Token expired"

    except jwt.InvalidTokenError:
        return None, "Invalid token"



# --------------------------------------------------
# CREATE SALES (POST)
# --------------------------------------------------
@csrf_exempt
@require_http_methods(["POST"])
def create_sales(request):
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

        # ✅ Generate ONE sales_id
        import uuid
        sales_id = f"SAL-{uuid.uuid4().hex[:10].upper()}"

        created_items = []

        for item in items:
            sale = Sales.objects.create(
                sales_id=sales_id,

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
                "product_name": sale.product_name,
                "item_code": sale.item_code,
                "quantity": sale.quantity,
                "amount": float(sale.amount)
            })

        return JsonResponse({
            "success": True,
            "message": "Sales created successfully",
            "sales_id": sales_id,
            "items": created_items
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)





# --------------------------------------------------
# LIST SALES (GET)
# --------------------------------------------------
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def sales_list(request):
    payload, error = get_client_from_token(request)
    if error:
        return JsonResponse({"success": False, "error": error}, status=401)

    client_id = payload.get("client_id")

    # ✅ SHOW ONLY "uploaded to server"
    sales = Sales.objects.filter(
        client_id=client_id,
        status="uploaded to server"
    ).order_by('-id')

    grouped_sales = {}

    for s in sales:
        if s.sales_id not in grouped_sales:
            grouped_sales[s.sales_id] = {
                "sales_id": s.sales_id,
                "customer_name": s.customer_name,
                "customer_code": s.customer_code,
                "area": s.area,
                "payment_type": s.payment_type,
                "username": s.username,
                "remark": s.remark,
                "created_date": s.created_date.strftime('%Y-%m-%d'),
                "created_time": s.created_time.strftime('%H:%M:%S'),
                "items": []
            }

        grouped_sales[s.sales_id]["items"].append({
            "product_name": s.product_name,
            "item_code": s.item_code,
            "barcode": s.barcode,
            "price": float(s.price),
            "quantity": s.quantity,
            "amount": float(s.amount)
        })

    return JsonResponse({
        "success": True,
        "total_sales": len(grouped_sales),
        "sales": list(grouped_sales.values())
    })


from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.http import JsonResponse
from .models import Sales
@csrf_exempt
@require_http_methods(["POST"])
def change_sales_status(request):
    payload, error = get_client_from_token(request)
    if error:
        return JsonResponse({"success": False, "error": error}, status=401)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    sales_id = data.get("sales_id")
    status_value = data.get("status")

    ALLOWED_STATUSES = ["uploaded to server", "completed"]

    if not sales_id or not status_value:
        return JsonResponse({
            "success": False,
            "error": "sales_id and status are required"
        }, status=400)

    if status_value not in ALLOWED_STATUSES:
        return JsonResponse({
            "success": False,
            "error": f"Invalid status. Allowed: {ALLOWED_STATUSES}"
        }, status=400)

    sales = Sales.objects.filter(
        sales_id=sales_id,
        client_id=payload.get("client_id")
    )

    if not sales.exists():
        return JsonResponse({
            "success": False,
            "error": "Sales not found"
        }, status=404)

    now = timezone.localtime()

    sales.update(
        status=status_value,
        status_changed_date=now.date(),
        status_changed_time=now.time(),
        status_changed_by=payload.get("username") or payload.get("user") or "system"
    )

    return JsonResponse({
        "success": True,
        "message": "Sales status updated successfully",
        "sales_id": sales_id,
        "total_items_updated": sales.count(),
        "status": status_value
    })



from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def sales_list_all(request):
    payload, error = get_client_from_token(request)
    if error:
        return JsonResponse({"success": False, "error": error}, status=401)

    client_id = payload.get("client_id")

    # ✅ NO status filter → show ALL
    sales = Sales.objects.filter(
        client_id=client_id
    ).order_by('-id')

    grouped_sales = {}

    for s in sales:
        if s.sales_id not in grouped_sales:
            grouped_sales[s.sales_id] = {
                "sales_id": s.sales_id,
                "customer_name": s.customer_name,
                "customer_code": s.customer_code,
                "area": s.area,
                "payment_type": s.payment_type,
                "username": s.username,
                "remark": s.remark,
                "status": s.status,  # ✅ include status
                "created_date": s.created_date.strftime('%Y-%m-%d'),
                "created_time": s.created_time.strftime('%H:%M:%S'),
                "items": []
            }

        grouped_sales[s.sales_id]["items"].append({
            "product_name": s.product_name,
            "item_code": s.item_code,
            "barcode": s.barcode,
            "price": float(s.price),
            "quantity": s.quantity,
            "amount": float(s.amount)
        })

    return JsonResponse({
        "success": True,
        "total_sales": len(grouped_sales),
        "sales": list(grouped_sales.values())
    })
