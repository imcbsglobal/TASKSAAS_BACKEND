import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import ItemOrders


@csrf_exempt
@require_http_methods(["POST"])
def create_item_order(request):
    try:
        data = json.loads(request.body)

        order = ItemOrders.objects.create(
            customer_name=data.get("customer_name"),
            area=data.get("area"),
            product_name=data.get("product_name"),
            payment_type=data.get("payment_type"),
            amount=data.get("amount"),
            quantity=data.get("quantity"),
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


@require_http_methods(["GET"])
def item_orders_list(request):
    orders = ItemOrders.objects.all()

    data = []
    for o in orders:
        data.append({
            "id": o.id,
            "customer_name": o.customer_name,
            "area": o.area,
            "product_name": o.product_name,
            "payment_type": o.payment_type,
            "amount": float(o.amount),
            "quantity": o.quantity,
            "date": o.created_date,
            "time": o.created_time,
        })

    return JsonResponse({
        "success": True,
        "total": len(data),
        "orders": data
    })
