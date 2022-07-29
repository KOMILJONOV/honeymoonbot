from django.core.management import BaseCommand



class Command(BaseCommand):
    def handle(self, *args, **options) -> str:
        from tg_bot import Bot

        Bot()
        