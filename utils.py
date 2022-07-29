from telegram import (
    KeyboardButton,
    Update,
    User as tgUser,
    ReplyKeyboardMarkup as tgReplyKeyboardMarkup,
)


from bot.models import User

class Utils:
    def getUser(self, update:Update) -> "tuple[tgUser, User]":
        user = update.message.from_user if update.message else update.callback_query.from_user
        tgUser = User.objects.filter(id=user.id).first()
        return user, tgUser
    
    

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





class ReplyKeyboardMarkup(tgReplyKeyboardMarkup):
    def __init__(self,
        keyboard: "list[list[str, KeyboardButton]]",
        one_time_keyboard: bool = False,
        selective: bool = False,
        input_field_placeholder: str = None,
        **_kwargs):
        super().__init__(
            
            keyboard,
            True,
            one_time_keyboard,
            selective,
            input_field_placeholder
        )
    