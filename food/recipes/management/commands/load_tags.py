import csv

from django.core.management import BaseCommand
from django.db import IntegrityError

from recipes.models import Tag


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.import_tags()
        print('Загрузка тегов завершена.')

    def import_tags(self, file='tags.csv'):
        print(f'Загрузка данных из {file}')
        path = f'./recipes/management/commands/data/{file}'
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    status, created = Tag.objects.update_or_create(
                        name=row[0],
                        color=row[1],
                        slug=row[2]
                    )
                except IntegrityError:
                    print(f"Тег {row[0]} уже существует.")
