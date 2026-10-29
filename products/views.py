from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import date, datetime, timedelta
from .models import Product, DailyRecord, ProductCatalog
from .forms import ProductForm


# ========== ГЛАВНАЯ ==========
@login_required
def index(request):
    products = Product.objects.filter(user=request.user)
    
    total_protein = sum(p.actual_protein for p in products)
    total_fat = sum(p.actual_fat for p in products)
    total_carbs = sum(p.actual_carbs for p in products)
    total_calories = sum(p.actual_calories for p in products)
    
    context = {
        'products': products,
        'total_protein': round(total_protein, 2),
        'total_fat': round(total_fat, 2),
        'total_carbs': round(total_carbs, 2),
        'total_calories': round(total_calories, 2),
        'product_count': products.count(),
    }
    return render(request, 'products/index.html', context)


# ========== ДОБАВЛЕНИЕ ==========
@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            messages.success(request, f'Продукт "{product.name}" добавлен!')
            return redirect('index')
    else:
        form = ProductForm()
    
    catalog = ProductCatalog.objects.all().order_by('category', 'name')
    
    return render(request, 'products/add_product.html', {
        'form': form,
        'catalog': catalog,
    })


# ========== РЕДАКТИРОВАНИЕ ==========
@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Продукт "{product.name}" обновлён!')
            return redirect('index')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/edit_product.html', {
        'form': form,
        'product': product,
    })


# ========== УДАЛЕНИЕ ==========
@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    name = product.name
    product.delete()
    messages.info(request, f'Продукт "{name}" удалён')
    return redirect('index')


# ========== ИСТОРИЯ ==========
@login_required
def history(request):
    products = Product.objects.filter(user=request.user).order_by('-created_at')
    
    history_data = {}
    for product in products:
        date_str = product.created_at.strftime('%Y-%m-%d')
        if date_str not in history_data:
            history_data[date_str] = []
        history_data[date_str].append(product)
    
    return render(request, 'products/history.html', {'history_data': history_data})


# ========== СОХРАНЕНИЕ ДНЯ ==========
@login_required
def save_daily_record(request):
    if request.method == 'POST':
        today = date.today()
        products_today = Product.objects.filter(
            user=request.user,
            created_at__date=today
        )
        
        if not products_today.exists():
            messages.warning(request, 'Нет данных за сегодня')
            return redirect('index')
        
        total_protein = sum(p.actual_protein for p in products_today)
        total_fat = sum(p.actual_fat for p in products_today)
        total_carbs = sum(p.actual_carbs for p in products_today)
        total_calories = sum(p.actual_calories for p in products_today)
        
        DailyRecord.objects.update_or_create(
            user=request.user,
            date=today,
            defaults={
                'total_protein': total_protein,
                'total_fat': total_fat,
                'total_carbs': total_carbs,
                'total_calories': total_calories,
            }
        )
        messages.success(request, 'Дневная запись сохранена!')
    
    return redirect('index')


# ========== ОЧИСТКА ==========
@login_required
def clear_all(request):
    if request.method == 'POST':
        Product.objects.filter(user=request.user).delete()
        messages.info(request, 'Все ваши данные очищены!')
    return redirect('index')


# ========== СТАТИСТИКА ==========
@login_required
def get_stats(request):
    products = Product.objects.filter(user=request.user)
    
    total_products = products.count()
    total_calories = sum(p.actual_calories for p in products)
    avg_calories = total_calories / total_products if total_products > 0 else 0
    
    week_ago = timezone.now() - timedelta(days=7)
    week_products = products.filter(created_at__gte=week_ago).count()
    
    top_products = products.order_by('-calories')[:5]
    
    total_protein = sum(p.actual_protein for p in products)
    total_fat = sum(p.actual_fat for p in products)
    total_carbs = sum(p.actual_carbs for p in products)
    
    context = {
        'products': products,
        'total_products': total_products,
        'total_calories': round(total_calories, 2),
        'avg_calories': round(avg_calories, 2),
        'week_products': week_products,
        'top_products': top_products,
        'total_protein': round(total_protein, 2),
        'total_fat': round(total_fat, 2),
        'total_carbs': round(total_carbs, 2),
    }
    return render(request, 'products/stats.html', context)


# ========== СПРАВОЧНИК ПРОДУКТОВ ==========
@login_required
def catalog_view(request):
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    
    catalog = ProductCatalog.objects.all()
    if category:
        catalog = catalog.filter(category=category)
    if search:
        catalog = catalog.filter(name__icontains=search)
    
    categories = ProductCatalog.objects.values_list('category', flat=True).distinct()
    categories = [c for c in categories if c]
    
    return render(request, 'products/catalog.html', {
        'catalog': catalog,
        'categories': categories,
        'selected_category': category,
        'search': search,
    })


# ========== СПИСОК ПРОДУКТОВ (ОТЧЁТ) ==========
@login_required
def report_products(request):
    products = Product.objects.filter(user=request.user)
    names = products.values_list('name', flat=True).distinct()
    
    report = []
    for name in names:
        items = products.filter(name=name)
        report.append({
            'name': name,
            'count': items.count(),
            'total_weight': sum(p.weight for p in items),
            'total_calories': sum(p.actual_calories for p in items),
            'total_protein': sum(p.actual_protein for p in items),
            'total_fat': sum(p.actual_fat for p in items),
            'total_carbs': sum(p.actual_carbs for p in items),
            'last_date': items.first().created_at,
        })
    
    report.sort(key=lambda x: x['total_calories'], reverse=True)
    
    return render(request, 'products/report_products.html', {'report': report})


# ========== ОТЧЁТ ПО КОНКРЕТНОМУ ПРОДУКТУ ==========
@login_required
def report_product(request, product_name):
    products = Product.objects.filter(
        user=request.user, name__iexact=product_name
    ).order_by('-created_at')
    
    if not products.exists():
        messages.warning(request, 'Продукт не найден')
        return redirect('report_products')
    
    stats = {
        'name': product_name,
        'count': products.count(),
        'total_weight': sum(p.weight for p in products),
        'avg_weight': sum(p.weight for p in products) / products.count(),
        'total_protein': sum(p.actual_protein for p in products),
        'total_fat': sum(p.actual_fat for p in products),
        'total_carbs': sum(p.actual_carbs for p in products),
        'total_calories': sum(p.actual_calories for p in products),
        'avg_calories': sum(p.actual_calories for p in products) / products.count(),
        'first_date': products.last().created_at,
        'last_date': products.first().created_at,
    }
    
    by_date = {}
    for p in products:
        d = p.created_at.strftime('%Y-%m-%d')
        if d not in by_date:
            by_date[d] = {'weight': 0, 'calories': 0, 'count': 0}
        by_date[d]['weight'] += p.weight
        by_date[d]['calories'] += p.actual_calories
        by_date[d]['count'] += 1
    
    return render(request, 'products/report_product.html', {
        'stats': stats,
        'products': products,
        'by_date': dict(sorted(by_date.items(), reverse=True)),
    })


# ========== ОТЧЁТ ЗА ПЕРИОД ==========
@login_required
def report_period(request):
    period = request.GET.get('period', 'week')
    date_from_str = request.GET.get('date_from', '')
    date_to_str = request.GET.get('date_to', '')
    
    today = date.today()
    
    if period == 'week':
        date_from = today - timedelta(days=7)
        date_to = today
    elif period == 'month':
        date_from = today - timedelta(days=30)
        date_to = today
    elif period == 'year':
        date_from = today - timedelta(days=365)
        date_to = today
    elif period == 'custom' and date_from_str and date_to_str:
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        except ValueError:
            date_from = today - timedelta(days=7)
            date_to = today
    else:
        date_from = today - timedelta(days=7)
        date_to = today
    
    products = Product.objects.filter(
        user=request.user,
        created_at__date__gte=date_from,
        created_at__date__lte=date_to,
    ).order_by('-created_at')
    
    totals = {
        'protein': sum(p.actual_protein for p in products),
        'fat': sum(p.actual_fat for p in products),
        'carbs': sum(p.actual_carbs for p in products),
        'calories': sum(p.actual_calories for p in products),
        'count': products.count(),
    }
    
    daily = {}
    for p in products:
        d = p.created_at.strftime('%Y-%m-%d')
        if d not in daily:
            daily[d] = {'protein': 0, 'fat': 0, 'carbs': 0, 'calories': 0, 'count': 0}
        daily[d]['protein'] += p.actual_protein
        daily[d]['fat'] += p.actual_fat
        daily[d]['carbs'] += p.actual_carbs
        daily[d]['calories'] += p.actual_calories
        daily[d]['count'] += 1
    
    return render(request, 'products/report_period.html', {
        'period': period,
        'date_from': date_from,
        'date_to': date_to,
        'date_from_str': date_from_str,
        'date_to_str': date_to_str,
        'products': products,
        'totals': totals,
        'daily': dict(sorted(daily.items(), reverse=True)),
        'days_count': (date_to - date_from).days + 1,
    })