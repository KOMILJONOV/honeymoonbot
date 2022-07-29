from django.db import models
from django.forms import ValidationError
from telegram import Update, User as TelegramUser
# Create your models here.

from django.db.models.fields.files import FileDescriptor


class Utils:
    def getUser(self, update:Update) ->"tuple[TelegramUser, User]":
        user = update.message.from_user if update.message else update.callback_query.from_user
        tgUser = User.objects.filter(id=user.id).first()
        return user, tgUser
    
    
    @classmethod
    def distribute(self, items, number) -> list:
        res = []
        start = 0
        end = number
        for item in items:
            if items[start:end] == []:
                return res
            res.append(items[start:end])
            start += number
            end += number
        return res

class Region(models.Model, Utils):
    name: str = models.CharField(max_length=100)
    def __str__(self):
        return self.name

    @classmethod
    def keyboard(self):
        regions:"list[Region]" = Region.objects.all()
        return self.distribute([
            region.name for region in regions
        ], 2)


class User(models.Model):
    id:int = models.BigIntegerField(primary_key=True)
    name:str = models.CharField(max_length=255)
    number: str = models.CharField(max_length=255)
    region:Region = models.ForeignKey('Region', on_delete=models.CASCADE)




def file_size(value): # add this to some file where you can import it from
    # limit = 2 * 1024 * 1024
    # if value.size > limit:
    #     raise ValidationError('File too large. Size should not exceed 2 MiB.')
    pass


class Post(models.Model):
    media:FileDescriptor = models.FileField(upload_to="media/", validators=[file_size])
    media_type: int = models.IntegerField(
        choices=[
            (0, "text"),
            (1, "image"),
            (2, "video"),
            (3, "document"),
        ]
    )
    description:str = models.TextField()
    

    def send_to_user(self, user:TelegramUser):
        if self.media_type == 1:
            user.send_photo(open(self.media.path, 'rb'), caption=self.description, parse_mode="HTML")
        elif self.media_type == 2:
            user.send_video(open(self.media.path, 'rb'), caption=self.description, parse_mode="HTML")
        elif self.media_type == 3:
            user.send_document(open(self.media.path, 'rb'), caption=self.description, parse_mode="HTML")
        else:
            user.send_message(self.description, parse_mode="HTML")