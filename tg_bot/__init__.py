import requests
from setuptools import Command
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext
)

from telegram import (
    ReplyKeyboardRemove,
    KeyboardButton,
    Update
)

from CONST import TOKEN
from bot.models import Post, Region, User
from tg_bot.constants import (
    NAME,
    NUMBER,
    REGION
)
from utils import Utils, ReplyKeyboardMarkup



url = "https://honey-moon.bitrix24.ru/rest/1/xbja0nw3kkmubt1r/crm.lead.add.json"


class Bot(Updater, Utils):
    def __init__(self):
        super().__init__(token=TOKEN)
        
        not_start = ~Filters.regex(r'^(/start|/help)$')
        self.dispatcher.add_handler(
            ConversationHandler(
                [
                    CommandHandler('start', self.start),
                ],
                {
                    NAME: [
                        MessageHandler(
                            Filters.text & not_start,
                            self.name
                        )
                    ],
                    NUMBER: [
                        MessageHandler(
                            Filters.contact & not_start,
                            self.number
                        )
                    ],
                    REGION: [
                        MessageHandler(
                            Filters.text & not_start,
                            self.region
                        )
                    ]
                },
                [
                    CommandHandler('start', self.start),
                ]
            )
        )

        self.start_polling()
        self.idle()
    

    def start(self, update: Update, context: CallbackContext):
        user, dbUser = self.getUser(update)
        context.user_data['register'] = {
            "id": user.id,
        }


        if not dbUser:
            user.send_message(
                "Assalomu alaykum\nIltimos ismingiz va familyangizni yuboring."
            )
            return NAME
        else:
            user.send_message(
                "Kechirasiz siz ro'yxatdan o'tib bo'lgansiz.\nOperatorlarimiz tez orada siz bilan bog'lanishadi.\nBiz bilan bog'lanishingiz uchun Tel: +998555007878"
            )
            return NUMBER

    
    def name(self, update: Update, context: CallbackContext):
        user, dbUser = self.getUser(update)
        context.user_data['register']['name'] = update.message.text
        user.send_message(
            "Iltimos raqamingizni quyidagi tugma orqali yuboring!",
            reply_markup=ReplyKeyboardMarkup(
                [
                    [
                        KeyboardButton(
                            text="Raqamni yuborish",
                            request_contact=True

                        )
                    ]
                ]
            )
        )
        return NUMBER
                                                                                                 
                                                                                                 
    def number(self, update: Update, context: CallbackContext):
        user, dbUser = self.getUser(update)
        context.user_data['register']['number'] = update.message.contact.phone_number
                                                                                                 
        user.send_message(
            "Iltimos endi viloyatingizni tanlang!",
            reply_markup=ReplyKeyboardMarkup(
                Region.keyboard()
            )
        )
        return REGION
                                                                                                 
                                                                                                 
    def region(self, update: Update, context: CallbackContext):
        user, dbUser = self.getUser(update)
        region = Region.objects.filter(name=update.message.text).first()
                                                                                                 
        if region:
            context.user_data['register']['region'] = region
            
            new_user:User = User.objects.create(
                **context.user_data['register']
            )
                                                                                                 
                                                                                                 
                                                                                                 
            data = {
                "fields[TITLE]": f"{new_user.name} - {new_user.number} - {new_user.region.name}",
                "fields[NAME]": new_user.name,
                "fields[PHONE][0][VALUE]": new_user.number,
                "fields[ADDRESS]": new_user.region.name
            }
            print(data)
                                                                                                 
                                                                                                 
            res = requests.post(url, data=data)
            print(res.json())
                                                                                                 
            user.send_message("Tabriklaymiz siz botimizdan muvafaqqiyatli ro'yxatdan o'tdingiz.",reply_markup=ReplyKeyboardRemove())
            post: Post = Post.objects.first()
            
            if post:
                post.send_to_user(
                    user
                )
                
        else:
            user.send_message(
                "Kechirasiz viloyat topilmadi!"
            )
            return REGION