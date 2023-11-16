import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        with open("data/ingredients.csv", encoding="utf8") as f:
            reader_object = csv.reader(f, delimiter=",")
            for row in reader_object:
                obj = Ingredient(
                    name=row[0],
                    measurement_unit=row[1],
                )
                obj.save()
