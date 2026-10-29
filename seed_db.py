"""
Заполнение SQLite демо-данными.
Запуск:  python seed_db.py
"""
import os
import random
import django
from datetime import date, timedelta, datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bju_calculator.settings')
django.setup()

from django.contrib.auth.models import User
from products.models import Product, ProductCatalog, DailyRecord


# ==========================================================
# 1. ПОЛЬЗОВАТЕЛЬ
# ==========================================================
def create_user():
    user, created = User.objects.get_or_create(
        username='demo',
        defaults={'email': 'demo@example.com'}
    )
    if created:
        user.set_password('demo12345')
        user.save()
        print(f'✅ Создан пользователь: demo / demo12345')
    else:
        print(f'ℹ️  Пользователь demo уже есть')
    return user


# ==========================================================
# 2. СПРАВОЧНИК ПРОДУКТОВ
# ==========================================================
CATALOG = [
    # (название, белки, жиры, углеводы, категория)
    # Мясо
    ('Куриная грудка', 23.5, 1.5, 0.0, 'Мясо'),
    ('Куриное бедро', 18.0, 15.0, 0.0, 'Мясо'),
    ('Индейка', 22.0, 8.0, 0.0, 'Мясо'),
    ('Говядина', 18.0, 20.0, 0.0, 'Мясо'),
    ('Свинина', 20.0, 30.0, 0.0, 'Мясо'),
    ('Баранина', 17.0, 25.0, 0.0, 'Мясо'),
    # Рыба
    ('Лосось', 20.0, 13.0, 0.0, 'Рыба'),
    ('Тунец', 25.0, 1.0, 0.0, 'Рыба'),
    ('Горбуша', 20.0, 6.0, 0.0, 'Рыба'),
    ('Скумбрия', 18.0, 25.0, 0.0, 'Рыба'),
    ('Минтай', 16.0, 1.0, 0.0, 'Рыба'),
    ('Сельдь', 17.0, 19.0, 0.0, 'Рыба'),
    # Молочные
    ('Молоко 2.5%', 3.0, 2.5, 4.7, 'Молочные'),
    ('Кефир 1%', 3.0, 1.0, 4.0, 'Молочные'),
    ('Творог 5%', 16.0, 5.0, 2.0, 'Молочные'),
    ('Сыр твердый', 25.0, 30.0, 0.0, 'Молочные'),
    ('Сметана 20%', 2.8, 20.0, 3.2, 'Молочные'),
    ('Йогурт натуральный', 4.5, 1.5, 6.0, 'Молочные'),
    # Яйца
    ('Яйцо куриное', 12.7, 11.5, 0.7, 'Яйца'),
    ('Яйцо перепелиное', 13.0, 11.0, 0.6, 'Яйца'),
    # Крупы
    ('Гречка', 12.6, 3.3, 62.1, 'Крупы'),
    ('Рис', 7.0, 1.0, 75.0, 'Крупы'),
    ('Овсянка', 12.0, 6.0, 65.0, 'Крупы'),
    ('Макароны', 10.0, 1.0, 70.0, 'Крупы'),
    ('Перловка', 9.3, 1.1, 73.7, 'Крупы'),
    ('Пшено', 11.5, 3.3, 69.3, 'Крупы'),
    # Овощи
    ('Картофель', 2.0, 0.1, 17.0, 'Овощи'),
    ('Морковь', 1.3, 0.1, 9.6, 'Овощи'),
    ('Помидор', 0.9, 0.2, 3.9, 'Овощи'),
    ('Огурец', 0.8, 0.1, 3.6, 'Овощи'),
    ('Капуста белокочанная', 1.8, 0.1, 4.7, 'Овощи'),
    ('Брокколи', 3.0, 0.4, 7.0, 'Овощи'),
    ('Лук репчатый', 1.4, 0.2, 9.0, 'Овощи'),
    ('Шпинат', 2.9, 0.4, 3.6, 'Овощи'),
    # Фрукты
    ('Яблоко', 0.4, 0.4, 11.8, 'Фрукты'),
    ('Банан', 1.5, 0.2, 22.0, 'Фрукты'),
    ('Апельсин', 0.9, 0.2, 11.8, 'Фрукты'),
    ('Грейпфрут', 0.7, 0.1, 8.0, 'Фрукты'),
    ('Виноград', 0.6, 0.2, 16.0, 'Фрукты'),
    # Бобовые
    ('Фасоль', 21.0, 2.0, 62.0, 'Бобовые'),
    ('Горох', 20.0, 2.0, 60.0, 'Бобовые'),
    ('Чечевица', 24.0, 1.5, 60.0, 'Бобовые'),
    # Орехи
    ('Грецкий орех', 15.0, 65.0, 15.0, 'Орехи'),
    ('Миндаль', 21.0, 50.0, 20.0, 'Орехи'),
    ('Кешью', 18.0, 44.0, 30.0, 'Орехи'),
    # Масла
    ('Масло оливковое', 0.0, 99.8, 0.0, 'Масла'),
    ('Масло сливочное', 0.8, 82.5, 0.0, 'Масла'),
    # Хлеб
    ('Хлеб белый', 7.5, 2.0, 48.0, 'Хлеб'),
    ('Хлеб ржаной', 8.0, 1.0, 45.0, 'Хлеб'),
    # Сладости
    ('Шоколад темный', 6.0, 35.0, 50.0, 'Сладости'),
    ('Мёд', 0.8, 0.0, 80.0, 'Сладости'),
    ('Сахар', 0.0, 0.0, 99.7, 'Сладости'),
]


def fill_catalog():
    print('\n📚 Заполняем справочник продуктов...')
    created = 0
    for name, p, f, c, cat in CATALOG:
        obj, was_created = ProductCatalog.objects.get_or_create(
            name=name,
            defaults={
                'protein': p, 'fat': f, 'carbs': c, 'category': cat
            }
        )
        if was_created:
            created += 1
    print(f'✅ Добавлено новых: {created}')
    print(f'📊 Всего в справочнике: {ProductCatalog.objects.count()}')


# ==========================================================
# 3. ПРОДУКТЫ ПОЛЬЗОВАТЕЛЯ (за 30 дней)
# ==========================================================
def fill_products(user, days=30, per_day=(2, 5)):
    print(f'\n🍽️  Генерируем продукты за {days} дней...')

    # Удалить старые продукты пользователя (чтобы не было дублей)
    deleted = Product.objects.filter(user=user).delete()[0]
    print(f'🗑️  Удалено старых: {deleted}')

    catalog = list(ProductCatalog.objects.all())
    if not catalog:
        print('❌ Справочник пуст, сначала заполните его')
        return

    meals = ['breakfast', 'lunch', 'dinner', 'snack']
    today = date.today()
    total_created = 0

    for i in range(days):
        day = today - timedelta(days=i)
        count = random.randint(*per_day)

        for _ in range(count):
            item = random.choice(catalog)
            # Вес порции — от 50 до 250 г
            weight = random.choice([50, 80, 100, 120, 150, 200, 250])

            # Случайное время приёма пищи
            meal = random.choice(meals)
            hour = {
                'breakfast': 8, 'lunch': 13,
                'dinner': 19, 'snack': 16
            }[meal]

            # Создаём объект
            product = Product(
                user=user,
                name=item.name,
                protein=item.protein,
                fat=item.fat,
                carbs=item.carbs,
                weight=weight,
                meal_type=meal,
            )

            # created_at — auto_now_add, поэтому зададим после save
            product.save()

            # Принудительно ставим дату
            dt = timezone.make_aware(
                datetime(day.year, day.month, day.day,
                         hour, random.randint(0, 59))
            )
            Product.objects.filter(pk=product.pk).update(created_at=dt)
            total_created += 1

    print(f'✅ Создано продуктов: {total_created}')
    print(f'📊 Всего у пользователя {user.username}: '
          f'{Product.objects.filter(user=user).count()}')


# ==========================================================
# 4. ДНЕВНЫЕ ЗАПИСИ (последние 14 дней)
# ==========================================================
def fill_daily_records(user, days=14):
    print(f'\n📅 Заполняем дневные записи за {days} дней...')
    DailyRecord.objects.filter(user=user).delete()

    today = date.today()
    created = 0

    for i in range(days):
        day = today - timedelta(days=i)
        items = Product.objects.filter(
            user=user, created_at__date=day
        )
        if not items.exists():
            continue

        DailyRecord.objects.create(
            user=user,
            date=day,
            total_protein=sum(p.actual_protein for p in items),
            total_fat=sum(p.actual_fat for p in items),
            total_carbs=sum(p.actual_carbs for p in items),
            total_calories=sum(p.actual_calories for p in items),
        )
        created += 1

    print(f'✅ Дневных записей: {created}')


# ==========================================================
# 5. ИТОГИ
# ==========================================================
def print_summary(user):
    print('\n' + '=' * 50)
    print('📊 ИТОГИ БАЗЫ ДАННЫХ')
    print('=' * 50)
    print(f'👤 Пользователей:      {User.objects.count()}')
    print(f'📚 Справочник:         {ProductCatalog.objects.count()}')
    print(f'🍽️  Всего продуктов:   {Product.objects.count()}')
    print(f'🍽️  У {user.username}:  {Product.objects.filter(user=user).count()}')
    print(f'📅 Дневных записей:   {DailyRecord.objects.count()}')
    print('=' * 50)
    print(f'\n🔑 Логин:  demo')
    print(f'🔑 Пароль: demo12345')
    print(f'\n🌐 Откройте: http://127.0.0.1:8000/')
    print('=' * 50)


# ==========================================================
# ЗАПУСК
# ==========================================================
if __name__ == '__main__':
    print('🚀 Заполнение SQLite...')
    print(f'📁 БД: db.sqlite3\n')

    user = create_user()
    fill_catalog()
    fill_products(user, days=30, per_day=(2, 5))
    fill_daily_records(user, days=14)
    print_summary(user)

    print('\n✅ Готово!')