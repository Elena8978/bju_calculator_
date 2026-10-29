from django.db import models
from django.contrib.auth.models import User
from datetime import date



# class ProductCatalog(models.Model):
#     """
#     Справочник продуктов (общий для всех пользователей)
#     Заполняется один раз администратором
#     """
#     name = models.CharField('Название', max_length=200, unique=True)
#     protein = models.FloatField('Белки (г на 100г)', default=0.0)
#     fat = models.FloatField('Жиры (г на 100г)', default=0.0)
#     carbs = models.FloatField('Углеводы (г на 100г)', default=0.0)
#     calories = models.FloatField('Калории (на 100г)', default=0.0, editable=False)
#     category = models.CharField('Категория', max_length=100, blank=True)
    
#     class Meta:
#         verbose_name = 'Продукт (справочник)'
#         verbose_name_plural = 'Справочник продуктов'
#         ordering = ['name']
    
#     def __str__(self):
#         return self.name
    
#     def save(self, *args, **kwargs):
#         self.calories = (self.protein * 4) + (self.fat * 9) + (self.carbs * 4)
#         super().save(*args, **kwargs)


class Product(models.Model):
    """
    Продукт, введённый пользователем
    Привязан к конкретному пользователю
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='Пользователь',
        related_name='products',
        null=True,  # временно, для миграции
        blank=True
    )
    name = models.CharField('Название', max_length=200)
    protein = models.FloatField('Белки (г)', default=0.0)
    fat = models.FloatField('Жиры (г)', default=0.0)
    carbs = models.FloatField('Углеводы (г)', default=0.0)
    calories = models.FloatField('Калории (ккал)', default=0.0, editable=False)
    weight = models.FloatField('Вес порции (г)', default=100.0)
    meal_type = models.CharField(
        'Приём пищи',
        max_length=20,
        choices=[
            ('breakfast', 'Завтрак'),
            ('lunch', 'Обед'),
            ('dinner', 'Ужин'),
            ('snack', 'Перекус'),
        ],
        default='lunch'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.name} ({self.user.username if self.user else "—"})'
    
    def calculate_calories(self):
        return (self.protein * 4) + (self.fat * 9) + (self.carbs * 4)
    
    def save(self, *args, **kwargs):
        self.calories = self.calculate_calories()
        super().save(*args, **kwargs)
    
    @property
    def actual_calories(self):
        return self.calories * (self.weight / 100)
    
    @property
    def actual_protein(self):
        return self.protein * (self.weight / 100)
    
    @property
    def actual_fat(self):
        return self.fat * (self.weight / 100)
    
    @property
    def actual_carbs(self):
        return self.carbs * (self.weight / 100)


class DailyRecord(models.Model):
    """Дневные итоги"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='Пользователь',
        related_name='daily_records',
        null=True,
        blank=True
    )
    date = models.DateField('Дата', default=date.today)
    total_protein = models.FloatField('Белки (г)', default=0.0)
    total_fat = models.FloatField('Жиры (г)', default=0.0)
    total_carbs = models.FloatField('Углеводы (г)', default=0.0)
    total_calories = models.FloatField('Калории (ккал)', default=0.0)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Дневная запись'
        verbose_name_plural = 'Дневные записи'
        ordering = ['-date']
    
    def __str__(self):
        return f"Запись за {self.date} ({self.user.username if self.user else '—'})"

class ProductCatalog(models.Model):
    name = models.CharField('Название', max_length=200, unique=True)
    protein = models.FloatField('Белки (г на 100г)', default=0.0)
    fat = models.FloatField('Жиры (г на 100г)', default=0.0)
    carbs = models.FloatField('Углеводы (г на 100г)', default=0.0)
    calories = models.FloatField('Калории (на 100г)', default=0.0, editable=False)
    category = models.CharField('Категория', max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Продукт (справочник)'
        verbose_name_plural = 'Справочник продуктов'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.calories = (self.protein * 4) + (self.fat * 9) + (self.carbs * 4)
        super().save(*args, **kwargs)