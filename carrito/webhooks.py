import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from carrito.models import Cart
from pedidos.models import Pedido, PedidoItem
import logging


logger = logging.getLogger(__name__)
User = get_user_model()

@csrf_exempt
@require_POST
def stripe_webhook(request):
    print("🔥 WEBHOOK EJECUTADO")
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    # Use ONLY settings.STRIPE_WEBHOOK_SECRET - NO fallbacks
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    
    if not endpoint_secret:
        logger.error("STRIPE_WEBHOOK_SECRET not configured")
        return HttpResponse(status=400)
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        logger.error("Webhook signature error - invalid payload")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        logger.error("Webhook signature verification failed")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return HttpResponse(status=400)

    logger.info(f"✅ Webhook recibido: {event['type']}")

    # Handle checkout.session.completed ONLY
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.id
        
        # Idempotencia: Skip si ya procesado
        if Pedido.objects.filter(stripe_session_id=session_id).exists():
            logger.info(f"✅ Webhook idempotente para {session_id} - ya procesado")
            return HttpResponse(status=200)
        
        # Validate metadata
        metadata = getattr(session, 'metadata', {})
        user_id_str = metadata.get('user_id')
        
        if not user_id_str:
            logger.warning(f"No user_id in metadata: {session_id}")
            return HttpResponse(status=200)
        
        try:
            user_id = int(user_id_str)
        except ValueError:
            logger.error(f"Invalid user_id format: {user_id_str}")
            return HttpResponse(status=200)
        
        try:
            # Get user and cart
            user = User.objects.get(id=user_id)
            cart = Cart.objects.filter(user=user).first()
            
            if not cart or not cart.items.exists():
                logger.warning(f"No cart or empty cart for user {user_id}")
                return HttpResponse(status=200)
            
            # Calculate total
            total = sum(item.subtotal() for item in cart.items.all())
            
            # Create Pedido
            pedido = Pedido.objects.create(
                user=user,
                total=total,
                estado='pagado',
                direccion='Pendiente',
                telefono='Pendiente',
                stripe_session_id=session_id,
            )
            
            # Create PedidoItems
            for item in cart.items.all():
                PedidoItem.objects.create(
                    pedido=pedido,
                    product=item.product,
                    cantidad=item.quantity,
                    precio_unitario=item.product.price,
                )
            
            # Clear cart
            cart.items.all().delete()
            
            logger.info(f"✅ Pedido #{pedido.id} creado para user {user_id}, total: ${total}")
            
        except User.DoesNotExist:
            logger.error(f"User {user_id} not found")
        except Exception as e:
            logger.error(f"Error creating pedido: {str(e)}")
    
    return HttpResponse(status=200)

