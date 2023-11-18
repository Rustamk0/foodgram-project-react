import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self):
        with open("data/ingredients.csv", encoding='utf8') as f:
            csv_reader = csv.reader(f)
            data = []
            next(csv_reader)
            for row in csv_reader:
                name, measurement_unit = row
                ingredient = Ingredient(
                    name=name,
                    measurement_unit=measurement_unit,
                )
                data.append(ingredient)
            Ingredient.objects.bulk_create(data)
