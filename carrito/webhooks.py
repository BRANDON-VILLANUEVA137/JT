import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from carrito.models import Cart
from pedidos.models import Pedido, PedidoItem
from inventario.services import registrar_venta
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@csrf_exempt
@require_POST
def stripe_webhook(request):
    print("🔥 WEBHOOK EJECUTADO")
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    
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
        logger.error("Webhook error: {}".format(str(e)))
        return HttpResponse(status=400)

    logger.info("✅ Webhook recibido: {}".format(event["type"]))

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session.id
        
        # Idempotency check
        if Pedido.objects.filter(stripe_session_id=session_id).exists():
            logger.info("✅ Webhook idempotent for {}".format(session_id))
            return HttpResponse(status=200)
        
        metadata = getattr(session, "metadata", {})
        user_id_str = metadata.get("user_id")
        
        if not user_id_str:
            logger.warning("No user_id in metadata: {}".format(session_id))
            return HttpResponse(status=200)
        
        try:
            user_id = int(user_id_str)
        except ValueError:
            logger.error("Invalid user_id: {}".format(user_id_str))
            return HttpResponse(status=200)
        
        try:
            user = User.objects.get(id=user_id)
            cart = Cart.objects.filter(user=user).first()
            
            if not cart or not cart.items.exists():
                logger.warning("No cart for user {}".format(user_id))
                return HttpResponse(status=200)
            
            # Verify stock (warn but continue)
            for item in cart.items.all():
                if item.quantity > item.product.stock:
                    logger.error("⚠️ Stock insuficiente for {}: {} < {} - overselling".format(item.product.name, item.product.stock, item.quantity))
            
            total = sum(item.subtotal() for item in cart.items.all())
            
            telefono = metadata.get("telefono", "No proporcionado")
            direccion = metadata.get("direccion", "No proporcionada")
            
            pedido = Pedido.objects.create(
                user=user,
                total=total,
                estado="preparacion",
                direccion=direccion,
                telefono=telefono,
                stripe_session_id=session_id,
            )
            
            # Create items and update stock via inventory system
            for item in cart.items.all():
                PedidoItem.objects.create(
                    pedido=pedido,
                    product=item.product,
                    cantidad=item.quantity,
                    precio_unitario=item.product.price,
                )
                
                # Use inventory service to register the sale
                registrar_venta(
                    product=item.product,
                    cantidad=item.quantity,
                    pedido_id=pedido.id,
                )
                logger.info("✅ Stock updated for {}: -{} (via inventario)".format(item.product.name, item.quantity))
            
            # Clear cart
            cart.items.all().delete()
            
            logger.info("✅ Pedido #{} created, stock updated, cart cleared for user {}".format(pedido.id, user_id))
        except User.DoesNotExist:
            logger.error("User {} not found".format(user_id))
        except Exception as e:
            logger.error("Error creating pedido: {}".format(str(e)))
    
    return HttpResponse(status=200)
