import csv

from django.core.management import BaseCommand
from django.db import IntegrityError

from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.import_ingredients()
        print('Загрузка ингредиентов завершена.')

    def import_ingredients(self, file='ingredients.csv'):
        print(f'Загрузка данных из {file}')
        path = f'./recipes/management/commands/data/{file}'
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    status, created = Ingredient.objects.update_or_create(
                        name=row[0],
                        measurement_unit=row[1]
                    )
                except IntegrityError:
                    print(f"Ингредиент {row[0]} уже существует.")
