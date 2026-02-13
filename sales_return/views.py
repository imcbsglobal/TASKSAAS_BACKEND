import json
import jwt
import uuid
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .models import SalesReturn


# ---------------- TOKEN ----------------
def get_client_from_token(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION')

    if not auth_header or not auth_header.startswith("Bearer "):
        return None, "Invalid authorization header"

    token = auth_header.split(" ", 1)[1]

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"


# ---------------- CREATE SALES RETURN ----------------
@csrf_exempt
@require_http_methods(["POST"])
def create_sales_return(request):
    payload, error = get_client_from_token(request)
    if error:
        return JsonResponse({"success": False, "error": error}, status=401)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    items = data.get("items", [])
    if not items:
        return JsonResponse({"success": False, "error": "items required"}, status=400)

    order_id = f"SR-{uuid.uuid4().hex[:10].upper()}"
    created_items = []

    from decimal import Decimal

    for item in items:
        # 🔹 ONLY FIX: quantity normalization
        qty = item.get("quantity")

        if isinstance(qty, str):
            qty = qty.strip()
            if qty.startswith("."):
                qty = "0" + qty
            if qty.endswith("."):
                qty = qty + "0"

        try:
            quantity = Decimal(qty)
        except Exception:
            return JsonResponse({
                "success": False,
                "error": f"Invalid quantity value: {item.get('quantity')}"
            }, status=400)

        sr = SalesReturn.objects.create(
            order_id=order_id,

            customer_name=data.get("customer_name"),
            customer_code=data.get("customer_code"),
            area=data.get("area"),

            product_name=item.get("product_name"),
            item_code=item.get("item_code"),
            barcode=item.get("barcode"),

            price=item.get("price"),
            quantity=quantity,          # ✅ fixed here
            amount=item.get("amount"),

            # ✅ ITEM-LEVEL REMARK
            product_remark=item.get("remark"),

            client_id=payload.get("client_id"),
            username=data.get("username"),
            device_id=data.get("device_id")
        )

        created_items.append({
            "product_name": sr.product_name,
            "item_code": sr.item_code,
            "quantity": sr.quantity,
            "amount": float(sr.amount),
            "remark": sr.product_remark
        })

    return JsonResponse({
        "success": True,
        "order_id": order_id,
        "items": created_items
    })



# ---------------- LIST (UPLOADED ONLY) ----------------
@require_http_methods(["GET"])
def sales_return_list(request):
    payload, error = get_client_from_token(request)
    if error:
        return JsonResponse({"success": False, "error": error}, status=401)

    returns = SalesReturn.objects.filter(
        client_id=payload.get("client_id"),
        status="uploaded to server"
    ).order_by('-id')

    grouped = {}

    for r in returns:
        grouped.setdefault(r.order_id, {
            "order_id": r.order_id,
            "customer_name": r.customer_name,
            "customer_code": r.customer_code,
            "area": r.area,
            "username": r.username,
            "status": r.status,
            "created_date": r.created_date.strftime('%Y-%m-%d'),
            "created_time": r.created_time.strftime('%H:%M:%S'),
            "items": []
        })["items"].append({
            "product_name": r.product_name,
            "item_code": r.item_code,
            "barcode": r.barcode,
            "price": float(r.price),
            "quantity": r.quantity,
            "amount": float(r.amount),
            "remark": r.product_remark   # ✅ SHOW ITEM REMARK
        })

    return JsonResponse({
        "success": True,
        "total": len(grouped),
        "returns": list(grouped.values())
    })


# ---------------- STATUS CHANGE ----------------
@csrf_exempt
@require_http_methods(["POST"])
def sales_return_status_change(request):
    payload, error = get_client_from_token(request)
    if error:
        return JsonResponse({"success": False, "error": error}, status=401)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    order_id = data.get("order_id")
    status_value = data.get("status")

    ALLOWED_STATUSES = ["uploaded to server", "completed"]

    if not order_id or not status_value:
        return JsonResponse({
            "success": False,
            "error": "order_id and status are required"
        }, status=400)

    if status_value not in ALLOWED_STATUSES:
        return JsonResponse({
            "success": False,
            "error": f"Invalid status. Allowed: {ALLOWED_STATUSES}"
        }, status=400)

    qs = SalesReturn.objects.filter(
        order_id=order_id,
        client_id=payload.get("client_id")
    )

    if not qs.exists():
        return JsonResponse({
            "success": False,
            "error": "Invalid order_id"
        }, status=404)

    now = timezone.localtime()

    qs.update(
        status=status_value
    )

    return JsonResponse({
        "success": True,
        "message": "Status updated successfully",
        "order_id": order_id,
        "status": status_value
    })
