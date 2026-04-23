from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.db import transaction, DatabaseError,connection
from django.db.models import OuterRef, Subquery
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse

import jwt
import logging

from .models import ShopLocation, PunchIn, UserAreas
from .serializers import ShopLocationSerializer
from app1.models import Misel, AccMaster, AccUser

logger = logging.getLogger(__name__)


# ============================================================================
# UTILITY FUNCTIONS - JWT & AUTHENTICATION
# ============================================================================

def decode_jwt_token(request):
    """Decode JWT token from Authorization header"""
    auth_header = request.META.get("HTTP_AUTHORIZATION")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(' ')[1]

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except Exception:
        return None


def get_client_id_from_token(request):
    """Get client_id from JWT token"""
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload.get('client_id')
    except Exception:
        return None


# ============================================================================
# SHOP LOCATION FEATURES
# ============================================================================


@api_view(['POST'])
def shop_location(request):
    """Create or update shop location"""
    try:
        payload = decode_jwt_token(request)
        if not payload:
            return Response({'error': 'Invalid or missing token'}, status=401)

        client_id = payload.get("client_id")
        username = payload.get("username")

        if not client_id:
            return Response({'error': 'Invalid or missing token'}, status=401)

        firm_name = request.data.get('firm_name')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        if not firm_name or not latitude or not longitude:
            return Response({'error': 'firm_name, latitude, longitude required'}, status=400)

        # Validate coordinates
        try:
            lat = Decimal(str(latitude))
            lng = Decimal(str(longitude))
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                return Response({'error': 'Invalid coordinate values'}, status=400)
        except (InvalidOperation, ValueError):
            return Response({'error': 'Invalid coordinate format'}, status=400)

        try:
            firm = AccMaster.objects.get(name=firm_name, client_id=client_id)
        except AccMaster.DoesNotExist:
            return Response({'error': 'Invalid firm for this client'}, status=404)

        with transaction.atomic():
            shop, created = ShopLocation.objects.get_or_create(
                firm=firm,
                client_id=client_id,
                defaults={
                    'latitude': latitude,
                    'longitude': longitude,
                    "created_by": username 
                },
            )

            if not created:
                shop.latitude = latitude
                shop.longitude = longitude
                if username:
                    shop.created_by = username
                shop.save()

        serializer = ShopLocationSerializer(shop)
        return Response({'success': True, 'data': serializer.data}, status=201 if created else 200)

    except DatabaseError as e:
        logger.error(f"Database error in shop_location: {str(e)}")
        return Response({'error': 'Database operation failed'}, status=500)
    except Exception as e:
        logger.exception("Unexpected error in shop_location")
        return Response({'error': 'An unexpected error occurred'}, status=500)

  
@api_view(['GET'])
def get_firms(request):
    """Get all firms with their latest shop location coordinates"""
    try:
        payload = decode_jwt_token(request)
        if not payload:
            return Response({'error': 'Invalid or missing token'}, status=401)

        username = payload.get('username')
        client_id = payload.get('client_id')
        role = payload.get('role')

        if not client_id:
            return Response({'error': 'Invalid or missing token'}, status=401)

        # Prepare subquery for latest shop location
        latest_shop = ShopLocation.objects.filter(
            firm=OuterRef('pk'),
            client_id=client_id
        ).order_by('-created_at')

        # ---- ADMIN LOGIC ----
        if role == "Admin":
            firms = (
                AccMaster.objects.filter(client_id=client_id)
                .annotate(
                    latitude=Subquery(latest_shop.values('latitude')[:1]),
                    longitude=Subquery(latest_shop.values('longitude')[:1]),
                )
            )

        # ---- NON-ADMIN LOGIC ----
        else:
            # Get areas assigned to this user
            user_areas = UserAreas.objects.filter(
                client_id=client_id,
                user=username
            ).values_list('area_code', flat=True)

            from django.db.models import Q
            area_filter = Q()

            # Build LIKE filters: name__icontains or area__icontains
            for area in user_areas:
                area_filter |= Q(name__icontains=area) | Q(area__icontains=area)

            # Apply dynamic filters
            firms = (
                AccMaster.objects.filter(client_id=client_id)
                .filter(area_filter)
                .annotate(
                    latitude=Subquery(latest_shop.values('latitude')[:1]),
                    longitude=Subquery(latest_shop.values('longitude')[:1]),
                )
            )

        # ---- RESPONSE ----
        if not firms.exists():
            return Response({'success': True, 'firms': [], 'message': 'No firms found'}, status=200)

        data = [
            {
                'id': firm.code,
                'firm_name': firm.name,
                'area': firm.area,
                'latitude': float(firm.latitude) if firm.latitude is not None else None,
                'longitude': float(firm.longitude) if firm.longitude is not None else None,
            }
            for firm in firms
        ]

        return Response({'success': True, 'firms': data}, status=200)

    except DatabaseError as e:
        logger.error(f"Database error in get_firms: {str(e)}")
        return Response({'error': 'Database error'}, status=500)
    except Exception as e:
        logger.exception("Unexpected error in get_firms")
        return Response({'error': 'An unexpected error occurred'}, status=500)


@api_view(['GET'])
def get_table_data(request):
    """Get shop location data for authenticated client using optimized raw SQL"""
    try:
        payload = decode_jwt_token(request)
        if not payload:
            return Response({'error': 'Invalid or missing token'}, status=401)

        client_id = payload.get('client_id')
        if not client_id:
            return Response({'error': 'Invalid token payload'}, status=401)
        userRole=payload.get('role')
        userName=payload.get('username')
        
        startDate = request.GET.get('start_date')
        endDate =request.GET.get('end_date')
        if startDate and endDate:
            date_filter = f"AND s.created_at >= '{startDate}' AND s.created_at < '{endDate}'::date + INTERVAL '1 day'"
        else:
            date_filter = ""


        # print("Start/End date :",startDate ,endDate)


        from django.db import connection

        # ✅ Dynamic table names (no hardcoding)
        shop_table = ShopLocation._meta.db_table       # "shop_location"
        firm_table = AccMaster._meta.db_table          # "acc_master"

        if(userRole=='Admin' or userRole =='admin'):
            

        # ✅ Correct join: shop_location.firm_code → acc_master.code
            sql_query = f"""
            SELECT 
            s.id,
            s.latitude,
            s.longitude,
            s.status,
            s.created_by,
            s.created_at,
            s.client_id,
            a.code as firm_code,
            COALESCE(a.name, 'Unknown Store') as firm_name,
            COALESCE(a.place, 'No address') as firm_place
            FROM {shop_table} s
            LEFT JOIN {firm_table} a ON s.firm_code = a.code AND s.client_id = a.client_id
            WHERE s.client_id = %s  {date_filter}
            ORDER BY s.created_at DESC
            """
        else :
                        sql_query = f"""
            SELECT 
            s.id,
            s.latitude,
            s.longitude,
            s.status,
            s.created_by,
            s.created_at,
            s.client_id,
            a.code as firm_code,
            COALESCE(a.name, 'Unknown Store') as firm_name,
            COALESCE(a.place, 'No address') as firm_place
            FROM {shop_table} s
            LEFT JOIN {firm_table} a ON s.firm_code = a.code AND s.client_id = a.client_id
            WHERE s.client_id = %s AND s.created_by = '{userName}'  {date_filter}
            ORDER BY s.created_at DESC
            """


        with connection.cursor() as cursor:
            cursor.execute(sql_query, [client_id])
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

        if not rows:
            return Response({
                'success': True,
                'data': [],
                'message': 'No shop locations found',
                'count': 0
            }, status=200)

        # ✅ Convert rows → dicts
        data = []
        for row in rows:
            row_dict = dict(zip(columns, row))

            # Safe coordinate conversion
            try:
                latitude = float(row_dict['latitude']) if row_dict['latitude'] is not None else None
                longitude = float(row_dict['longitude']) if row_dict['longitude'] is not None else None
            except (ValueError, TypeError):
                latitude, longitude = None, None

            # Safe timestamp formatting
            try:
                last_captured = row_dict['created_at'].isoformat() if row_dict['created_at'] else None
            except Exception:
                last_captured = str(row_dict['created_at']) if row_dict['created_at'] else None

            data.append({
                'id': row_dict['id'],
                'firm_code': row_dict['firm_code'],
                'storeName': row_dict['firm_name'],
                'storeLocation': row_dict['firm_place'],
                'latitude': latitude,
                'longitude': longitude,
                'status': row_dict['status'] or 'pending',
                'taskDoneBy': row_dict['created_by'] or 'Unknown',
                'lastCapturedTime': last_captured,
                'client_id': row_dict['client_id'],
            })

        return Response({
            'success': True,
            'data': data,
            'count': len(data),
            'message': 'Shop locations retrieved successfully'
        }, status=200)

    except DatabaseError as e:
        logger.error(f"Database error in get_table_data: {str(e)}")
        return Response({'error': 'Database error'}, status=500)
    except Exception as e:
        logger.exception("Unexpected error in get_table_data")
        return Response({'error': 'Internal server error'}, status=500)




@api_view(['POST'])
def update_location_status(request):
    """Update the status of a shop location"""
    try:
        payload = decode_jwt_token(request)
        if not payload:
            return Response({'error': 'Invalid or missing token'}, status=401)
        
        client_id = payload.get("client_id")
        username = payload.get("username")

        new_status = request.data.get('status')
        shop_id = request.data.get('shop_id')

        if not new_status:
            return Response({"error": 'Status is required'}, status=400)

        if not shop_id:
            return Response({"error": 'ShopId is required'}, status=400)
    
        with transaction.atomic():
            updated_count = ShopLocation.objects.filter(
                client_id=client_id,
                firm_id=shop_id
            ).update(status=new_status)

            if updated_count == 0:
                return Response({'error': 'Shop not found or unauthorized'}, status=404)

        return Response({'success': True, 'updated_count': updated_count}, status=200)

    except MultipleObjectsReturned:
        logger.error(f"Multiple ShopLocations found for client_id={client_id}, shop_id={shop_id}")
        return Response({'error': 'Multiple shops found with same ID, please contact support'}, status=500)
    except DatabaseError as e:
        logger.error(f"Database error in update_location_status: {str(e)}")
        return Response({'error': 'Database error'}, status=500)
    except Exception as e:
        logger.exception("Unexpected error while updating shop status")
        return Response({'error': 'Internal server error'}, status=500)


@api_view(['POST'])
def update_punchin_verification(request):
    """Update the status of a shop location"""
    try:
        payload = decode_jwt_token(request)
        if not payload:
            return Response({'error': 'Invalid or missing token'}, status=401)
        
        client_id = payload.get("client_id")
        username = payload.get("username")

        new_status = request.data.get('status')
        shop_id = request.data.get('shop_id')
        punchinId = request.data.get('id')
        createdBy = request.data.get('createdBy')


        if not shop_id:
            return Response({"error": 'ShopId is required'}, status=400)
       
        if not new_status:
            return Response({"error": 'Status is required'}, status=400)

        if not punchinId :
            return Response({"error":'Punchin Id required'},status=400)

        with transaction.atomic():
            updated_count = PunchIn.objects.filter(
                client_id=client_id,
                firm_id=shop_id,
                created_by=createdBy,
                id = punchinId
            ).update(status=new_status)

            if updated_count == 0:
                return Response({'error': 'Shop not found or unauthorized'}, status=404)

        return Response({'success': True, 'updated_count': updated_count}, status=200)

    except MultipleObjectsReturned:
        logger.error(f"Multiple ShopLocations found for client_id={client_id}, shop_id={shop_id}")
        return Response({'error': 'Multiple shops found with same ID, please contact support'}, status=500)
    except DatabaseError as e:
        logger.error(f"Database error in punchin status update: {str(e)}")
        return Response({'error': 'Database error'}, status=500)
    except Exception as e:
        logger.exception("Unexpected error while updating punchin status")
        return Response({'error': 'Internal server error'}, status=500)


# ============================================================================
# PUNCH-IN/OUT FEATURES
# ============================================================================

@api_view(['POST'])
def punchin(request):
    """
    Handle punch-in functionality with image upload and location tracking
    Accepts image file directly and uploads to Cloudflare R2
    """
    try:
        # ✅ Authenticate user
        payload = decode_jwt_token(request)
        if not payload:
            return Response({'error': 'Authentication required'}, status=401)
        
        client_id = payload.get('client_id')
        username = payload.get('username')
        user_id = payload.get('user_id')

        if not client_id or not username:
            return Response({'error': 'Invalid token payload'}, status=401)

        # 📥 Get request data
        firm_code = request.data.get('customerCode')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        notes = request.data.get('notes', '')
        address = request.data.get('address', '')
        image_file = request.FILES.get('image')

        # ✅ KEEP SAME (for compatibility)
        current_location = request.data.get('current_location')
        shop_location = request.data.get('shop_location')
        punchin_status = request.data.get('punchin_status')

        # ✅ Existing validations (unchanged)
        if not firm_code:
            return Response({'error': 'firm_code is required'}, status=400)
        
        if not latitude or not longitude:
            return Response({'error': 'Location coordinates are required'}, status=400)

        if not image_file:
            return Response({'error': 'Image file is required for punch-in'}, status=400)

        if not current_location:
            return Response({'error': 'current_location is required'}, status=400)

        if not shop_location:
            return Response({'error': 'shop_location is required'}, status=400)

        if not punchin_status:
            return Response({'error': 'punchin_status is required'}, status=400)

        # 🖼️ Image validation (unchanged)
        max_size = 5 * 1024 * 1024
        if image_file.size > max_size:
            return Response({'error': 'Image size must be less than 5MB'}, status=400)

        allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
        if image_file.content_type not in allowed_types:
            return Response({'error': 'Only JPG, JPEG, and PNG images are allowed'}, status=400)

        # 📍 Coordinate validation (unchanged)
        try:
            lat = float(latitude)
            lng = float(longitude)
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                return Response({'error': 'Invalid coordinate values'}, status=400)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid coordinate format'}, status=400)

        # 🏬 Firm validation (unchanged)
        try:
            firm = AccMaster.objects.get(code=firm_code, client_id=client_id)
        except AccMaster.DoesNotExist:
            return Response({'error': 'Invalid firm code for this client'}, status=404)

        # ============================
        # ✅ ONLY CHANGE: LOCATION CHECK
        # ============================
        import math

        def calculate_distance(lat1, lon1, lat2, lon2):
            R = 6371000
            lat1, lon1, lat2, lon2 = map(math.radians, map(float, [lat1, lon1, lat2, lon2]))
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            return R * c

        try:
            cur_lat, cur_lon = current_location.split(',')
            shop_lat, shop_lon = shop_location.split(',')

            distance = calculate_distance(cur_lat, cur_lon, shop_lat, shop_lon)

            if distance > 100:
                punchin_status = "Mismatch Location"
            else:
                punchin_status = "Correct Location"

        except Exception:
            # fallback (keep original value if something fails)
            punchin_status = punchin_status

        # 🕒 Existing punch-in check (unchanged)
        from django.utils import timezone
        today = timezone.now().date()

        existing_punchin = PunchIn.objects.filter(
            client_id=client_id,
            created_by=username,
            punchin_time__date=today,
            punchout_time__isnull=True
        ).first()

        # ✅ Create punch-in record
        with transaction.atomic():
            punchin_record = PunchIn.objects.create(
                firm=firm,
                client_id=client_id,
                latitude=lat,
                longitude=lng,
                current_location=current_location,
                shop_location=shop_location,

                # ✅ FINAL STATUS (ONLY THIS CHANGED)
                punchin_status=punchin_status,

                photo=image_file,
                address=address,
                notes=notes,
                created_by=username,
                status='pending'
            )

            logger.info(f"Punch-in created successfully for user {username}, ID: {punchin_record.id}")

        # ✅ Response (unchanged)
        photo_url = punchin_record.photo.url if punchin_record.photo else None
        
        response_data = {
            'success': True,
            'message': 'Punch-in recorded successfully',
            'data': {
                'punchin_id': punchin_record.id,
                'firm_name': firm.name,
                'firm_code': firm.code,
                'punchin_time': punchin_record.punchin_time.isoformat(),
                'latitude': float(punchin_record.latitude),
                'longitude': float(punchin_record.longitude),
                'current_location': punchin_record.current_location,
                'shop_location': punchin_record.shop_location,
                'punchin_status': punchin_record.punchin_status,
                'photo_url': photo_url,
                'address': punchin_record.address,
                'status': punchin_record.status,
                'created_by': punchin_record.created_by
            }
        }

        return Response(response_data, status=201)

    except DatabaseError as e:
        logger.error(f"Database error in punchin: {str(e)}")
        return Response({'error': 'Database operation failed'}, status=500)

    except Exception as e:
        logger.error(f"Error in punchin for user {username if 'username' in locals() else 'unknown'}: {str(e)}")
        return Response({'error': 'Punch-in failed'}, status=500)


@api_view(['POST'])
def punchout(request, id):
    """
    Handle punch-out functionality
    """
    try:
        payload = decode_jwt_token(request)
        if not payload:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        client_id = payload.get('client_id')
        username = payload.get('username')

        if not client_id or not username:
            return Response(
                {'error': 'Invalid token payload'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        punchin_id = id
        notes = request.data.get('notes', '')

        from django.utils import timezone

        logger.info(
            f"Punchout request | client_id={client_id} | "
            f"username={username} | requested_id={punchin_id}"
        )

        active_punchin = (
            PunchIn.objects
            .filter(
                id=punchin_id,
                client_id=client_id,
                created_by__iexact=username,
                punchout_time__isnull=True
            )
            .order_by('-punchin_time')
            .first()
        )

        latest_active = (
            PunchIn.objects
            .filter(
                client_id=client_id,
                created_by__iexact=username,
                punchout_time__isnull=True
            )
            .order_by('-punchin_time')
            .first()
        )

        if not active_punchin:
            return Response(
                {
                    'error': 'No active punch-in found with the provided ID',
                    'details': {
                        'requested_id': punchin_id,
                        'latest_active_id': latest_active.id if latest_active else None,
                        'client_id': client_id,
                        'username': username,
                        'note': (
                            'Requested record may already be punched out, '
                            'belong to another user, or the frontend is using '
                            'an old punchin_id.'
                        )
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            active_punchin.punchout_time = timezone.now()

            if notes:
                existing_notes = active_punchin.notes or ''
                active_punchin.notes = (
                    f"{existing_notes}\nPunch-out notes: {notes}"
                ).strip()

            active_punchin.save(update_fields=['punchout_time', 'notes'])

        # Get firm only for same client_id
        firm = AccMaster.objects.filter(
            code=active_punchin.firm_id,
            client_id=client_id
        ).first()

        logger.info(
            f"Firm lookup | firm_code={active_punchin.firm_id} | "
            f"client_id={client_id} | "
            f"firm_name={firm.name if firm else 'Unknown Store'}"
        )

        work_duration = active_punchin.punchout_time - active_punchin.punchin_time
        hours = round(work_duration.total_seconds() / 3600, 2)

        return Response(
            {
                'success': True,
                'message': 'Punch-out recorded successfully',
                'data': {
                    'punchin_id': active_punchin.id,
                    'firm_name': firm.name if firm else 'Unknown Store',
                    'firm_code': firm.code if firm else None,
                    'punchin_time': active_punchin.punchin_time.isoformat(),
                    'punchout_time': active_punchin.punchout_time.isoformat(),
                    'work_duration_hours': hours,
                    'status': active_punchin.status or 'pending'
                }
            },
            status=status.HTTP_200_OK
        )

    except DatabaseError as e:
        logger.exception(
            f"Database error in punchout | "
            f"client_id={client_id if 'client_id' in locals() else None}"
        )
        return Response(
            {
                'error': 'Database operation failed',
                'details': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    except Exception as e:
        logger.exception(
            f"Unexpected error in punchout | "
            f"user={username if 'username' in locals() else 'unknown'}"
        )
        return Response(
            {
                'error': 'Punch-out failed',
                'details': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_active_punchin(request):
    """
    Get current punch status for authenticated user
    """
    try:
        payload = decode_jwt_token(request)
        if not payload:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        client_id = payload.get('client_id')
        username = payload.get('username')

        if not client_id or not username:
            return Response(
                {'error': 'Invalid token payload'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        from django.utils import timezone
        today = timezone.now().date()

        logger.info(
            f"Punch status request | client_id={client_id} | username={username}"
        )

        # Find latest active punch-in for this client + user only
        active_punchin = (
            PunchIn.objects
            .filter(
                client_id=client_id,
                created_by__iexact=username,
                punchin_time__date=today,
                punchout_time__isnull=True
            )
            .order_by('-punchin_time')
            .first()
        )

        if active_punchin:
            work_duration = timezone.now() - active_punchin.punchin_time
            hours = round(work_duration.total_seconds() / 3600, 2)

            # Get correct firm only from this client_id
            firm = AccMaster.objects.filter(
                code=active_punchin.firm_id,
                client_id=client_id
            ).first()

            logger.info(
                f"Active punch found | punchin_id={active_punchin.id} | "
                f"firm_id={active_punchin.firm_id} | "
                f"firm_name={firm.name if firm else 'None'}"
            )

            # Safe photo url
            photo_url = None
            try:
                if active_punchin.photo:
                    photo_url = active_punchin.photo.url
            except Exception as photo_error:
                logger.warning(
                    f"Photo URL error for punchin {active_punchin.id}: {photo_error}"
                )

            return Response(
                {
                    'success': True,
                    'is_punched_in': True,
                    'data': {
                        'punchin_id': active_punchin.id,
                        'firm_name': firm.name if firm else 'Unknown Store',
                        'firm_code': firm.code if firm else None,
                        'punchin_time': active_punchin.punchin_time.isoformat(),
                        'current_work_hours': hours,
                        'seconds': int(work_duration.total_seconds()),
                        'photo_url': photo_url,
                        'address': active_punchin.address or '',
                        'status': active_punchin.status or 'pending',
                        'created_by': active_punchin.created_by
                    }
                },
                status=status.HTTP_200_OK
            )

        # If no active punch-in, check completed punch today
        completed_today = (
            PunchIn.objects
            .filter(
                client_id=client_id,
                created_by__iexact=username,
                punchin_time__date=today,
                punchout_time__isnull=False
            )
            .order_by('-punchout_time')
            .first()
        )

        response_data = {
            'success': True,
            'is_punched_in': False,
            'completed_today': completed_today is not None,
            'data': None
        }

        if completed_today:
            work_duration = completed_today.punchout_time - completed_today.punchin_time
            hours = round(work_duration.total_seconds() / 3600, 2)

            # Get correct firm only from same client_id
            firm = AccMaster.objects.filter(
                code=completed_today.firm_id,
                client_id=client_id
            ).first()

            response_data['data'] = {
                'punchin_id': completed_today.id,
                'firm_name': firm.name if firm else 'Unknown Store',
                'firm_code': firm.code if firm else None,
                'punchin_time': completed_today.punchin_time.isoformat(),
                'punchout_time': completed_today.punchout_time.isoformat(),
                'total_work_hours': hours,
                'status': completed_today.status or 'pending'
            }

        return Response(response_data, status=status.HTTP_200_OK)

    except DatabaseError as e:
        logger.exception(
            f"Database error in get_active_punchin | "
            f"client_id={client_id if 'client_id' in locals() else None}"
        )
        return Response(
            {
                'error': 'Database error',
                'details': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    except Exception as e:
        logger.exception(
            f"Unexpected error in get_active_punchin | "
            f"user={username if 'username' in locals() else 'unknown'}"
        )
        return Response(
            {
                'error': 'Failed to get punch status',
                'details': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def punchin_table(request):
    """Get punch-in table data for authenticated client with role-based filtering"""
    try:
        payload = decode_jwt_token(request)
        if not payload:
            return Response({'error': 'Invalid or missing token'}, status=401)

        client_id = payload.get('client_id')
        if not client_id:
            return Response({'error': 'Invalid token payload'}, status=401)
        
        user_role = payload.get('role')
        username = payload.get('username')
        startDate = request.GET.get('start_date')
        endDate = request.GET.get('end_date')

        if startDate and endDate:
            date_filter = f"AND p.created_at >= '{startDate}' AND p.created_at < '{endDate}'::date + INTERVAL '1 day'"
        else:
            date_filter = ""

        from django.db import connection

        punchin_table = PunchIn._meta.db_table
        firm_table = AccMaster._meta.db_table

        # ================= ADMIN QUERY =================
        if user_role and user_role.lower() == 'admin':
            sql_query = f"""
            SELECT 
                p.id,
                p.latitude,
                p.longitude,

                -- ✅ ADDED FIELDS
                p.current_location,
                p.shop_location,
                p.punchin_status,

                p.punchin_time,
                p.punchout_time,
                p.photo,
                p.address,
                p.notes,
                p.status,
                p.created_by,
                p.created_at,
                p.updated_at,
                p.client_id,
                a.code as firm_code,
                COALESCE(a.name, 'Unknown Store') as firm_name,
                COALESCE(a.place, 'No address') as firm_place
            FROM {punchin_table} p
            LEFT JOIN {firm_table} a 
                ON p.firm_code = a.code AND p.client_id = a.client_id
            WHERE p.client_id = %s {date_filter}
            ORDER BY p.punchin_time DESC
            """
            query_params = [client_id]

        # ================= USER QUERY =================
        else:
            sql_query = f"""
            SELECT 
                p.id,
                p.latitude,
                p.longitude,

                -- ✅ ADDED FIELDS
                p.current_location,
                p.shop_location,
                p.punchin_status,

                p.punchin_time,
                p.punchout_time,
                p.photo,
                p.address,
                p.notes,
                p.status,
                p.created_by,
                p.created_at,
                p.updated_at,
                p.client_id,
                a.code as firm_code,
                COALESCE(a.name, 'Unknown Store') as firm_name,
                COALESCE(a.place, 'No address') as firm_place
            FROM {punchin_table} p
            LEFT JOIN {firm_table} a 
                ON p.firm_code = a.code AND p.client_id = a.client_id
            WHERE p.client_id = %s AND p.created_by = %s {date_filter}
            ORDER BY p.punchin_time DESC
            """
            query_params = [client_id, username]

        with connection.cursor() as cursor:
            cursor.execute(sql_query, query_params)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

        if not rows:
            return Response({
                'success': True,
                'data': [],
                'message': 'No punch-in records found',
                'count': 0
            }, status=200)

        data = []
        for row in rows:
            row_dict = dict(zip(columns, row))

            try:
                latitude = float(row_dict['latitude']) if row_dict['latitude'] is not None else None
                longitude = float(row_dict['longitude']) if row_dict['longitude'] is not None else None
            except (ValueError, TypeError):
                latitude, longitude = None, None

            punchin_time = row_dict['punchin_time'].isoformat() if row_dict['punchin_time'] else None
            punchout_time = row_dict['punchout_time'].isoformat() if row_dict['punchout_time'] else None

            work_duration_hours = None
            if row_dict['punchin_time'] and row_dict['punchout_time']:
                duration = row_dict['punchout_time'] - row_dict['punchin_time']
                work_duration_hours = round(duration.total_seconds() / 3600, 2)

            photo_path = row_dict.get('photo')
            photo_url = (
                f"{settings.CLOUDFLARE_R2_PUBLIC_URL}/{photo_path}"
                if photo_path and not photo_path.startswith('http')
                else photo_path
            )

            record = {
                'id': row_dict['id'],
                'firm_code': row_dict['firm_code'],
                'firm_name': row_dict['firm_name'],
                'firm_location': row_dict['firm_place'],
                'latitude': latitude,
                'longitude': longitude,

                # ✅ ADDED FIELDS IN RESPONSE
                'current_location': row_dict.get('current_location'),
                'shop_location': row_dict.get('shop_location'),
                'punchin_status': row_dict.get('punchin_status'),

                'punchin_time': punchin_time,
                'punchout_time': punchout_time,
                'work_duration_hours': work_duration_hours,
                'photo_url': photo_url,
                'address': row_dict['address'] or '',
                'notes': row_dict['notes'] or '',
                'status': row_dict['status'] or 'pending',
                'created_by': row_dict['created_by'] or 'Unknown',
                'client_id': row_dict['client_id'],
                'is_active': row_dict['punchout_time'] is None,
                'created_at': row_dict['created_at'].isoformat() if row_dict['created_at'] else None,
                'updated_at': row_dict['updated_at'].isoformat() if row_dict['updated_at'] else None
            }

            data.append(record)

        return Response({
            'success': True,
            'data': data,
            'count': len(data),
            'message': f'Punch-in records retrieved successfully ({len(data)} records)',
            'user_role': user_role,
            'is_admin_view': user_role and user_role.lower() == 'admin'
        }, status=200)

    except DatabaseError as e:
        logger.error(f"Database error in punchin_table: {str(e)}")
        return Response({'error': 'Database error'}, status=500)
    except Exception as e:
        logger.error(f"Error in punchin_table: {str(e)}")
        return Response({'error': 'Failed to get punch-in records'}, status=500)



# ============================================================================
# AREA MANAGEMENT FEATURES
# ============================================================================

@api_view(['GET'])
def get_areas(request):
    try:
        payload = decode_jwt_token(request)
        if not payload:
            return Response({'error': 'Invalid or missing token'}, status=401)

        client_id = payload.get('client_id')
        if not client_id:
            return Response({'error': 'Invalid token payload'}, status=401)
        
        areas =AccMaster.objects.filter(client_id=client_id).values_list('area',flat=True).distinct()
        # areas =[a for a in areas if a]
        return Response({
            "status":"True",
            "areas":areas
        },status=200)

    except Exception as e:
        logger.error(f"Error in areas: {str(e)}")
        return Response({'error': 'Failed to get area records'}, status=500)


@api_view(['GET'])
def get_user_areas(request):
    """
    Get areas assigned to a specific user
    """
    try:
        # ✅ Authenticate user
        payload = decode_jwt_token(request)
        if not payload:
            return Response({'error': 'Authentication required'}, status=401)
        
        client_id = payload.get('client_id')
        logged_in_username = payload.get('username')
        
        if not client_id:
            return Response({'error': 'Invalid token payload'}, status=401)
        
        # ✅ Get user_id from query params or use logged-in user
        user_id = request.GET.get('user_id')

        if not user_id :
            return Response({'error':'User Id not found'},status=404)
        # print("UID",user_id)
        
        # ✅ Verify user exists
        try:
            user = AccUser.objects.get(id=user_id, client_id=client_id)
        except AccUser.DoesNotExist:
            return Response({
                'error': 'User not found',
                'user_id': user_id
            }, status=404)
        
        # ✅ Get user's assigned areas
        user_areas = UserAreas.objects.filter(user=user_id).values_list('area_code', flat=True)
        area_list = list(user_areas)
 
        return Response({
            'success': True,
            'user_id': user_id,
            'total_areas': len(area_list),
            'areas': area_list,
        }, status=200)
        
    except DatabaseError as e:
        logger.error(f"Database error in get_user_areas: {str(e)}")
        return Response({'error': 'Database error'}, status=500)
    except Exception as e:
        logger.error(f"Error in get_user_areas: {str(e)}")
        return Response({'error': 'Failed to get user areas'}, status=500)


@api_view(['POST'])
def update_area(request):
    """
    Update user areas - Add or remove area codes for a user
    Expects: { "user_id": "ARUN", "area_codes": ["AREA1", "AREA2", "AREA3"] }
    """
    try:
        # ✅ Authenticate admin/manager
        payload = decode_jwt_token(request)
        if not payload:
            return Response({'error': 'Authentication required'}, status=401)
        
        client_id = payload.get('client_id')
        admin_username = payload.get('username')
        admin_role = payload.get('role')
        
        if not client_id:
            return Response({'error': 'Invalid token payload'}, status=401)
        
        # Optional: Check if user has permission to update areas
        # if admin_role not in ['Admin', 'Manager']:
        #     return Response({'error': 'Insufficient permissions'}, status=403)
        
        # ✅ Get request data
        user_id = request.data.get('user_id')
        area_codes = request.data.get('area_codes', [])
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=400)
        
        if not isinstance(area_codes, list):
            return Response({'error': 'area_codes must be an array'}, status=400)
        
        # ✅ Verify user exists
        try:
            user = AccUser.objects.get(id=user_id, client_id=client_id)
        except AccUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        
        # ✅ Update user areas atomically
        with transaction.atomic():
            # Delete existing areas for this user
            deleted_count = UserAreas.objects.filter(user=user).delete()[0]
            
            # Add new areas
            new_areas = []
            for area_code in area_codes:
                if area_code:  # Skip empty strings
                    new_areas.append(
                        UserAreas(
                            user=user,
                            area_code=area_code.strip(),
                            client_id= client_id
                        )
                    )
            
            # Bulk create new areas
            if new_areas:
                UserAreas.objects.bulk_create(new_areas, ignore_conflicts=True)
            
            # Get updated areas
            updated_areas = list(
                UserAreas.objects.filter(user=user).values_list('area_code', flat=True)
            )
        
        logger.info(f"Areas updated for user {user_id} by {admin_username}. Removed: {deleted_count}, Added: {len(new_areas)}")
        
        return Response({
            'success': True,
            'message': 'User areas updated successfully',
            'data': {
                'user_id': user_id,
                'areas_removed': deleted_count,
                'areas_added': len(new_areas),
                'current_areas': updated_areas
            }
        }, status=200)
        
    except DatabaseError as e:
        logger.error(f"Database error in update_area: {str(e)}")
        return Response({'error': 'Database operation failed'}, status=500)
    except Exception as e:
        logger.error(f"Error in update_area: {str(e)}")
        return Response({'error': 'Failed to update user areas'}, status=500)


# ============================================================================
# IMAGE UPLOAD FEATURE
# ============================================================================

@api_view(['POST'])
def upload_image_to_r2(request):
    return


# ============================================================================
# HEALTH CHECK
# ============================================================================

@api_view(['GET'])
def health_check(request):
    """Simple health check endpoint"""
    return Response({
        'status': 'healthy',
        'message': 'API is running'
    }, status=200)