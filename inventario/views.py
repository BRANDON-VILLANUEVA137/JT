from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum, F
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db import transaction
from datetime import timedelta

from .models import (
    Lote, MovimientoInventario, UnidadIndividual,
    ConteoFisico, ConteoFisicoItem, AlertaStock
)
from .forms import (
    LoteForm, MovimientoForm, EntradaCompraForm, SalidaMermaForm,
    UnidadIndividualForm, ConteoFisicoForm, ConteoFisicoItemForm, AlertaStockForm
)
from .services import (
    registrar_movimiento, registrar_entrada_compra, registrar_ajuste,
    aplicar_conteo_fisico, obtener_productos_bajo_stock,
    obtener_productos_por_vencer
)
from Catalogo.models import Product


def admin_required(view_func):
    """Decorator to check if user is admin."""
    def _wrapped_view(request, *args, **kwargs):
        if request.user.rol != 'admin':
            messages.error(request, 'No tienes permiso para acceder a esta página.')
            return redirect('usuarios:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# ============================
# DASHBOARD DE INVENTARIO
# ============================
@login_required
@admin_required
def dashboard(request):
    """Dashboard principal del módulo de inventario."""
    # Estadísticas generales
    total_productos = Product.objects.filter(activo=True).count()
    total_stock = Product.objects.filter(activo=True).aggregate(total=Sum('stock'))['total'] or 0
    total_unidades_vendidas = MovimientoInventario.objects.filter(
        tipo='salida_venta'
    ).aggregate(total=Sum('cantidad'))['total'] or 0
    
    # Alertas - productos bajo stock
    alertas_stock = obtener_productos_bajo_stock()
    
    # Productos por vencer (próximos 30 días)
    productos_por_vencer = obtener_productos_por_vencer(dias=30)
    
    # Lotes vencidos
    lotes_vencidos = Lote.objects.filter(
        activo=True,
        cantidad_actual__gt=0,
        fecha_vencimiento__isnull=False,
        fecha_vencimiento__lt=timezone.now().date()
    ).select_related('product')
    
    # Últimos movimientos
    ultimos_movimientos = MovimientoInventario.objects.all()[:20]
    
    # Últimos conteos físicos
    ultimos_conteos = ConteoFisico.objects.all()[:5]
    
    context = {
        'total_productos': total_productos,
        'total_stock': total_stock,
        'total_unidades_vendidas': total_unidades_vendidas,
        'alertas_stock': alertas_stock,
        'productos_por_vencer': productos_por_vencer,
        'lotes_vencidos': lotes_vencidos,
        'ultimos_movimientos': ultimos_movimientos,
        'ultimos_conteos': ultimos_conteos,
    }
    return render(request, 'inventario/dashboard.html', context)


# ============================
# MOVIMIENTOS
# ============================
@login_required
@admin_required
def movimiento_list(request):
    """Listado de movimientos de inventario."""
    movimientos = MovimientoInventario.objects.all().select_related('product', 'usuario', 'lote')
    
    # Filtros
    tipo = request.GET.get('tipo')
    product_id = request.GET.get('product')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    q = request.GET.get('q')
    
    if tipo:
        movimientos = movimientos.filter(tipo=tipo)
    if product_id:
        movimientos = movimientos.filter(product_id=product_id)
    if fecha_desde:
        movimientos = movimientos.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        movimientos = movimientos.filter(fecha__lte=fecha_hasta)
    if q:
        movimientos = movimientos.filter(
            Q(product__name__icontains=q) |
            Q(notas__icontains=q) |
            Q(referencia_id__icontains=q)
        )
    
    paginator = Paginator(movimientos, 50)
    page = paginator.get_page(request.GET.get('page'))
    
    context = {
        'movimientos': page,
        'productos': Product.objects.filter(activo=True).order_by('name'),
        'tipos_movimiento': [
            ('entrada_compra', 'Entrada - Compra'),
            ('entrada_devolucion', 'Entrada - Devolución'),
            ('entrada_ajuste', 'Entrada - Ajuste'),
            ('salida_venta', 'Salida - Venta'),
            ('salida_merma', 'Salida - Merma'),
            ('salida_ajuste', 'Salida - Ajuste'),
        ],
        'filtros': {
            'tipo': tipo,
            'product': product_id,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'q': q,
        }
    }
    return render(request, 'inventario/movimiento_list.html', context)


@login_required
@admin_required
def movimiento_create(request):
    """Registrar un nuevo movimiento manual de inventario."""
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            tipo = form.cleaned_data['tipo']
            cantidad = form.cleaned_data['cantidad']
            lote = form.cleaned_data.get('lote')
            notas = form.cleaned_data.get('notas', '')
            
            # Determinar signo de la cantidad
            if tipo.startswith('entrada'):
                cantidad_real = cantidad
            else:
                cantidad_real = -cantidad
            
            try:
                registro = registrar_movimiento(
                    product=product,
                    cantidad=cantidad_real,
                    tipo=tipo,
                    usuario=request.user,
                    lote=lote,
                    notas=notas
                )
                messages.success(request, f'Movimiento registrado: {product.name} ({cantidad} unidades)')
                return redirect('inventario:movimiento_list')
            except Exception as e:
                messages.error(request, f'Error al registrar movimiento: {str(e)}')
    else:
        form = MovimientoForm()
    
    context = {'form': form}
    return render(request, 'inventario/movimiento_form.html', context)


@login_required
@admin_required
def entrada_compra(request):
    """Registrar entrada por compra a proveedor."""
    if request.method == 'POST':
        form = EntradaCompraForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            cantidad = form.cleaned_data['cantidad']
            proveedor = form.cleaned_data['proveedor']
            costo_unitario = form.cleaned_data.get('costo_unitario')
            fecha_vencimiento = form.cleaned_data.get('fecha_vencimiento')
            codigo_lote = form.cleaned_data.get('codigo_lote')
            
            try:
                with transaction.atomic():
                    # Crear o usar lote
                    if not codigo_lote:
                        codigo_lote = f"COMP-{timezone.now().strftime('%Y%m%d%H%M%S')}"
                    
                    lote = Lote.objects.create(
                        codigo_lote=codigo_lote,
                        product=product,
                        cantidad_inicial=cantidad,
                        cantidad_actual=cantidad,
                        proveedor=proveedor,
                        costo_unitario=costo_unitario,
                        fecha_vencimiento=fecha_vencimiento,
                    )
                    
                    registrar_movimiento(
                        product=product,
                        cantidad=cantidad,
                        tipo='entrada_compra',
                        usuario=request.user,
                        lote=lote,
                        referencia_tipo='proveedor',
                        notas=f'Compra a {proveedor} - Lote {codigo_lote}'
                    )
                
                messages.success(request, f'Entrada de {cantidad} unidades de {product.name} registrada correctamente.')
                return redirect('inventario:movimiento_list')
            except Exception as e:
                messages.error(request, f'Error al registrar entrada: {str(e)}')
    else:
        form = EntradaCompraForm()
    
    context = {'form': form, 'titulo': 'Entrada por Compra'}
    return render(request, 'inventario/movimiento_form.html', context)


@login_required
@admin_required
def salida_merma(request):
    """Registrar salida por merma/pérdida."""
    if request.method == 'POST':
        form = SalidaMermaForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            cantidad = form.cleaned_data['cantidad']
            motivo = form.cleaned_data['motivo']
            
            try:
                registrar_movimiento(
                    product=product,
                    cantidad=-cantidad,
                    tipo='salida_merma',
                    usuario=request.user,
                    notas=motivo
                )
                messages.success(request, f'Merma registrada: {cantidad} unidades de {product.name}')
                return redirect('inventario:movimiento_list')
            except Exception as e:
                messages.error(request, f'Error al registrar merma: {str(e)}')
    else:
        form = SalidaMermaForm()
    
    context = {'form': form, 'titulo': 'Registrar Merma'}
    return render(request, 'inventario/movimiento_form.html', context)


# ============================
# LOTES
# ============================
@login_required
@admin_required
def lote_list(request):
    """Listado de lotes."""
    lotes = Lote.objects.all().select_related('product').order_by('-fecha_ingreso')
    
    # Filtros
    q = request.GET.get('q')
    estado = request.GET.get('estado')
    product_id = request.GET.get('product')
    
    if q:
        lotes = lotes.filter(
            Q(codigo_lote__icontains=q) |
            Q(product__name__icontains=q) |
            Q(proveedor__icontains=q)
        )
    if estado == 'activo':
        lotes = lotes.filter(activo=True, cantidad_actual__gt=0)
    elif estado == 'agotado':
        lotes = lotes.filter(cantidad_actual=0)
    elif estado == 'vencido':
        lotes = lotes.filter(
            fecha_vencimiento__isnull=False,
            fecha_vencimiento__lt=timezone.now().date()
        )
    if product_id:
        lotes = lotes.filter(product_id=product_id)
    
    paginator = Paginator(lotes, 25)
    page = paginator.get_page(request.GET.get('page'))
    
    context = {
        'lotes': page,
        'productos': Product.objects.filter(activo=True).order_by('name'),
    }
    return render(request, 'inventario/lote_list.html', context)


@login_required
@admin_required
def lote_create(request):
    """Crear un nuevo lote."""
    if request.method == 'POST':
        form = LoteForm(request.POST)
        if form.is_valid():
            lote = form.save(commit=False)
            lote.cantidad_actual = lote.cantidad_inicial
            lote.save()
            
            # Registrar movimiento de entrada
            registrar_movimiento(
                product=lote.product,
                cantidad=lote.cantidad_inicial,
                tipo='entrada_compra',
                usuario=request.user,
                lote=lote,
                referencia_tipo='proveedor',
                notas=f'Creación de lote {lote.codigo_lote} - {lote.proveedor or "Sin proveedor"}'
            )
            
            messages.success(request, f'Lote {lote.codigo_lote} creado con {lote.cantidad_inicial} unidades.')
            return redirect('inventario:lote_list')
    else:
        form = LoteForm()
    
    context = {'form': form, 'titulo': 'Nuevo Lote'}
    return render(request, 'inventario/lote_form.html', context)


@login_required
@admin_required
def lote_detail(request, pk):
    """Detalle de un lote."""
    lote = get_object_or_404(Lote.objects.select_related('product'), pk=pk)
    movimientos = MovimientoInventario.objects.filter(lote=lote).select_related('usuario')
    unidades = UnidadIndividual.objects.filter(lote=lote)
    
    context = {
        'lote': lote,
        'movimientos': movimientos,
        'unidades': unidades,
    }
    return render(request, 'inventario/lote_detail.html', context)


# ============================
# UNIDADES INDIVIDUALES
# ============================
@login_required
@admin_required
def unidad_list(request):
    """Listado de unidades individuales."""
    unidades = UnidadIndividual.objects.all().select_related('product', 'lote').order_by('codigo_interno')
    
    q = request.GET.get('q')
    estado = request.GET.get('estado')
    product_id = request.GET.get('product')
    
    if q:
        unidades = unidades.filter(
            Q(codigo_interno__icontains=q) |
            Q(product__name__icontains=q)
        )
    if estado:
        unidades = unidades.filter(estado=estado)
    if product_id:
        unidades = unidades.filter(product_id=product_id)
    
    paginator = Paginator(unidades, 50)
    page = paginator.get_page(request.GET.get('page'))
    
    context = {
        'unidades': page,
        'productos': Product.objects.filter(activo=True).order_by('name'),
        'estados': [
            ('disponible', 'Disponible'),
            ('vendido', 'Vendido'),
            ('merma', 'Merma'),
            ('en_reparacion', 'En reparación'),
        ],
    }
    return render(request, 'inventario/unidad_list.html', context)


@login_required
@admin_required
def unidad_create(request):
    """Crear una nueva unidad individual."""
    if request.method == 'POST':
        form = UnidadIndividualForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Unidad individual registrada correctamente.')
            return redirect('inventario:unidad_list')
    else:
        form = UnidadIndividualForm()
    
    context = {'form': form, 'titulo': 'Nueva Unidad Individual'}
    return render(request, 'inventario/unidad_form.html', context)


@login_required
@admin_required
def unidad_update(request, pk):
    """Actualizar una unidad individual."""
    unidad = get_object_or_404(UnidadIndividual, pk=pk)
    if request.method == 'POST':
        form = UnidadIndividualForm(request.POST, instance=unidad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Unidad individual actualizada.')
            return redirect('inventario:unidad_list')
    else:
        form = UnidadIndividualForm(instance=unidad)
    
    context = {'form': form, 'titulo': f'Editar {unidad.codigo_interno}'}
    return render(request, 'inventario/unidad_form.html', context)


# ============================
# CONTEO FÍSICO
# ============================
@login_required
@admin_required
def conteo_list(request):
    """Listado de conteos físicos."""
    conteos = ConteoFisico.objects.all().order_by('-fecha_conteo')
    
    estado = request.GET.get('estado')
    if estado:
        conteos = conteos.filter(estado=estado)
    
    context = {'conteos': conteos}
    return render(request, 'inventario/conteo_list.html', context)


@login_required
@admin_required
def conteo_create(request):
    """Crear un nuevo conteo físico."""
    if request.method == 'POST':
        form = ConteoFisicoForm(request.POST)
        if form.is_valid():
            conteo = form.save(commit=False)
            conteo.usuario = request.user
            conteo.save()
            messages.success(request, f'Conteo {conteo.codigo_conteo} creado. Ahora puedes agregar productos a contar.')
            return redirect('inventario:conteo_detail', pk=conteo.pk)
    else:
        form = ConteoFisicoForm()
    
    context = {'form': form, 'titulo': 'Nuevo Conteo Físico'}
    return render(request, 'inventario/conteo_form.html', context)


@login_required
@admin_required
def conteo_detail(request, pk):
    """Detalle de un conteo físico."""
    conteo = get_object_or_404(ConteoFisico, pk=pk)
    items = ConteoFisicoItem.objects.filter(conteo=conteo).select_related('product')
    
    if request.method == 'POST':
        # Agregar item al conteo
        item_form = ConteoFisicoItemForm(request.POST)
        if item_form.is_valid():
            item = item_form.save(commit=False)
            item.conteo = conteo
            item.stock_sistema = item.product.stock
            item.save()
            messages.success(request, f'{item.product.name} añadido al conteo.')
            return redirect('inventario:conteo_detail', pk=conteo.pk)
    else:
        item_form = ConteoFisicoItemForm()
    
    context = {
        'conteo': conteo,
        'items': items,
        'item_form': item_form,
    }
    return render(request, 'inventario/conteo_detail.html', context)


@login_required
@admin_required
def conteo_completar(request, pk):
    """Completar un conteo físico y aplicar ajustes."""
    conteo = get_object_or_404(ConteoFisico, pk=pk)
    
    if conteo.estado != 'pendiente' and conteo.estado != 'en_progreso':
        messages.warning(request, 'Este conteo ya está completado o cancelado.')
        return redirect('inventario:conteo_detail', pk=conteo.pk)
    
    items = ConteoFisicoItem.objects.filter(conteo=conteo)
    ajustes_realizados = 0
    
    with transaction.atomic():
        for item in items:
            if item.diferencia != 0:
                movimiento = aplicar_conteo_fisico(item, usuario=request.user)
                if movimiento:
                    ajustes_realizados += 1
        
        conteo.estado = 'completado'
        conteo.save()
    
    messages.success(
        request,
        f'Conteo {conteo.codigo_conteo} completado. {ajustes_realizados} ajustes realizados.'
    )
    return redirect('inventario:conteo_detail', pk=conteo.pk)


@login_required
@admin_required
def conteo_cancelar(request, pk):
    """Cancelar un conteo físico."""
    conteo = get_object_or_404(ConteoFisico, pk=pk)
    conteo.estado = 'cancelado'
    conteo.save()
    messages.warning(request, f'Conteo {conteo.codigo_conteo} cancelado.')
    return redirect('inventario:conteo_list')


@login_required
@admin_required
def conteo_eliminar_item(request, item_pk):
    """Eliminar un item de un conteo físico."""
    item = get_object_or_404(ConteoFisicoItem, pk=item_pk)
    conteo_pk = item.conteo.pk
    if item.conteo.estado in ['pendiente', 'en_progreso']:
        item.delete()
        messages.success(request, 'Item eliminado del conteo.')
    else:
        messages.error(request, 'No se puede eliminar items de un conteo completado.')
    return redirect('inventario:conteo_detail', pk=conteo_pk)


# ============================
# ALERTAS DE STOCK
# ============================
@login_required
@admin_required
def alerta_list(request):
    """Listado de alertas de stock."""
    alertas = AlertaStock.objects.all().select_related('product').order_by('product__name')
    
    activo = request.GET.get('activo')
    if activo == 'si':
        alertas = alertas.filter(activo=True)
    elif activo == 'no':
        alertas = alertas.filter(activo=False)
    
    context = {
        'alertas': alertas,
        'productos_sin_alerta': Product.objects.filter(activo=True).exclude(
            id__in=AlertaStock.objects.values('product_id')
        ).order_by('name'),
    }
    return render(request, 'inventario/alerta_list.html', context)


@login_required
@admin_required
def alerta_create(request):
    """Crear una alerta de stock."""
    if request.method == 'POST':
        form = AlertaStockForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Alerta de stock creada correctamente.')
            return redirect('inventario:alerta_list')
    else:
        form = AlertaStockForm()
    
    context = {'form': form, 'titulo': 'Nueva Alerta de Stock'}
    return render(request, 'inventario/alerta_form.html', context)


@login_required
@admin_required
def alerta_update(request, pk):
    """Actualizar una alerta de stock."""
    alerta = get_object_or_404(AlertaStock, pk=pk)
    if request.method == 'POST':
        form = AlertaStockForm(request.POST, instance=alerta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Alerta de stock actualizada.')
            return redirect('inventario:alerta_list')
    else:
        form = AlertaStockForm(instance=alerta)
    
    context = {'form': form, 'titulo': f'Editar Alerta - {alerta.product.name}'}
    return render(request, 'inventario/alerta_form.html', context)


@login_required
@admin_required
def alerta_delete(request, pk):
    """Eliminar una alerta de stock."""
    alerta = get_object_or_404(AlertaStock, pk=pk)
    if request.method == 'POST':
        alerta.delete()
        messages.success(request, 'Alerta de stock eliminada.')
        return redirect('inventario:alerta_list')
    context = {'alerta': alerta}
    return render(request, 'inventario/alerta_confirm_delete.html', context)


# ============================
# PRODUCTOS (vista de stock)
# ============================
@login_required
@admin_required
def producto_stock(request):
    """Vista de stock general de productos."""
    productos = Product.objects.filter(activo=True).order_by('name').annotate(
        total_lotes=Sum('lotes__cantidad_actual')
    )
    
    q = request.GET.get('q')
    categoria = request.GET.get('categoria')
    
    if q:
        productos = productos.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q)
        )
    if categoria:
        productos = productos.filter(category_id=categoria)
    
    # Marcar productos con alerta
    alertas_dict = {}
    for alerta in AlertaStock.objects.filter(activo=True):
        alertas_dict[alerta.product_id] = alerta.stock_minimo
    
    context = {
        'productos': productos,
        'alertas_dict': alertas_dict,
        'categories': Product.objects.values_list('category__name', 'category_id').distinct(),
    }
    return render(request, 'inventario/producto_stock.html', context)