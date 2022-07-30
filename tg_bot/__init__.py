import requests
from setuptools import Command
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)
import xlsxwriter

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
    Update
)

from CONST import TOKEN
from bot.models import Post, Region, User
from tg_bot.constants import (
    CHECK_POST,
    NAME,
    NUMBER,
    POST_MEDIA,
    POST_RECEIVERS,
    POST_TEXT,
    REGION
)
from utils import Utils, ReplyKeyboardMarkup

start_bosganlarga = "Start bosganlarga"
royxatdan_otganlarga = "Ro'yxatdan o'tganlarga"
hammaga = "Hammaga"
textni_ozini_yuborish = "Textni ozini yuborish"


url = "https://honey-moon.bitrix24.ru/rest/1/xbja0nw3kkmubt1r/crm.lead.add.json"


class Bot(Updater, Utils):
    def __init__(self):
        super().__init__(token=TOKEN)

        not_start = ~Filters.regex(r'^(/start|/post)$')
        self.dispatcher.add_handler(

            ConversationHandler(
                [
                    CommandHandler('start', self.start),
                    CommandHandler('post', self.post),
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
                    ],
                    POST_RECEIVERS: [
                        MessageHandler(
                            Filters.regex(
                                fr"^({hammaga}|{start_bosganlarga}|{royxatdan_otganlarga})$"
                            ) & not_start,
                            self.post_receivers
                        )
                    ],
                    POST_MEDIA: [
                        # MessageHandler(
                        #     Filters.regex(
                        #         fr"^{textni_ozini_yuborish}$"
                        #     ) & not_start,
                        #     self.only_text
                        # ),
                        CallbackQueryHandler(
                            self.only_text,
                            pattern=fr"^only_text$"
                        ),
                        MessageHandler(
                            Filters.photo & not_start,
                            self.post_media_photo
                        ),
                        MessageHandler(
                            Filters.document & not_start,
                            self.post_media_document
                        ),
                        MessageHandler(
                            Filters.video & not_start,
                            self.post_media_video
                        )
                    ],
                    POST_TEXT: [
                        MessageHandler(
                            Filters.text & not_start,
                            self.post_text
                        )
                    ],
                    CHECK_POST: [
                        CallbackQueryHandler(
                            self.check_post,
                            pattern=fr"^(post_accept|post_decline)$"
                        )
                    ]
                },
                [
                    CommandHandler('start', self.start),
                    CommandHandler('post', self.post),
                ]
            )
        )

        self.dispatcher.add_handler(
            CommandHandler('data', self.data)
        )

        self.start_polling()
        self.idle()

    def start(self, update: Update, context: CallbackContext):
        user, dbUser = self.getUser(update)
        context.user_data['register'] = {
            "id": user.id,
        }

        if not dbUser:
            User.objects.create(
                **context.user_data['register']
            )
            user.send_message(
                "Assalomu alaykum\nIltimos ismingiz va familyangizni yuboring."
            )
            return NAME
        elif not dbUser.name or not dbUser.number or not dbUser.region:
            user.send_message(
                "Assalomu alaykum\nIltimos ismingiz va familyangizni yuboring."
            )
            return NAME
        else:
            user.send_message(
                "Kechirasiz siz ro'yxatdan o'tib bo'lgansiz.\nOperatorlarimiz tez orada siz bilan bog'lanishadi.\nBiz bilan bog'lanishingiz uchun Tel: +998555007878"
            )
            return -1

    def name(self, update: Update, context: CallbackContext):
        user, dbUser = self.getUser(update)

        # context.user_data['register']['name'] = update.message.text
        dbUser.name = update.message.text
        dbUser.save()

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
        # context.user_data['register']['number'] = update.message.contact.phone_number
        dbUser.number = update.message.contact.phone_number
        dbUser.save()

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
            # context.user_data['register']['region'] = region
            dbUser.region = region
            dbUser.is_registered = True
            dbUser.save()

            data = {
                "fields[TITLE]": f"{dbUser.name} - {dbUser.number} - {dbUser.region.name}",
                "fields[NAME]": dbUser.name,
                "fields[PHONE][0][VALUE]": dbUser.number,
                "fields[ADDRESS]": dbUser.region.name
            }

            res = requests.post(url, data=data)

            user.send_message(
                "Tabriklaymiz siz botimizdan muvafaqqiyatli ro'yxatdan o'tdingiz.", reply_markup=ReplyKeyboardRemove())
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

    def makeexcelData(self):
        workbook = xlsxwriter.Workbook('data.xlsx')
        worksheet = workbook.add_worksheet()
        worksheet.write('A1', 'ID')
        worksheet.write('B1', 'NAME')
        worksheet.write('C1', 'NUMBER')
        worksheet.write('D1', 'region')
        users: list[User] = User.objects.all()
        for user in range(users.count()):
            worksheet.write(f"A{user + 2}", users[user].id)
            worksheet.write(f"B{user + 2}", users[user].name)
            worksheet.write(f"C{user + 2}", users[user].number)
            worksheet.write(f"D{user + 2}", users[user].region.name)
        workbook.close()

        return open(workbook.filename, 'rb')

    def data(self, update: Update, context: CallbackContext):
        user, dbUser = self.getUser(update)
        xlsx = self.makeexcelData()

        if dbUser.is_admin:
            user.send_document(xlsx)

    def post(self, update: Update, context: CallbackContext):
        user, dbUser = self.getUser(update)
        if dbUser.is_admin:
            context.user_data['post'] = {}
            user.send_message(
                "Iltimos post kimlarga yuborilishini tanlang!",
                reply_markup=ReplyKeyboardMarkup(
                    [
                        [
                            hammaga
                        ],
                        [
                            start_bosganlarga,
                            royxatdan_otganlarga
                        ]
                    ]
                )
            )
            return POST_RECEIVERS

    def post_receivers(self, update: Update, context: CallbackContext):
        user, dbUser = self.getUser(update)

        context.user_data['post']['receivers'] = 0 if update.message.text == hammaga else (
            1 if update.message.text == start_bosganlarga else 2)
        user.send_message(
            "Iltimos post uchun mediani yuboring yoki postni o'zini forward qiling!",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            textni_ozini_yuborish,
                            callback_data="only_text"
                        )
                    ]
                ]
            )
        )

        return POST_MEDIA

    def post_media_photo(self, update: Update, context: CallbackContext):
        user, dbUser = self.getUser(update)
        context.user_data['post']['media'] = update.message.photo[-1].file_id
        context.user_data['post']['media_type'] = 1

        if update.message.caption:
            context.user_data['post']['caption'] = update.message.caption
            context.user_data['post']['caption_entities'] = update.message.caption_entities
            user.send_message(
                "Iltimos postni tasdiqlang"
            )
            user.send_photo(
                update.message.photo[-1].file_id,
                caption=update.message.caption,
                caption_entities=update.message.caption_entities,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Tasdiqlash",
                                callback_data="post_accept"
                            ),
                            InlineKeyboardButton(
                                "Bekor qilish",
                                callback_data="post_decline"
                            )
                        ]
                    ]
                )
            )
            return CHECK_POST
        else:
            user.send_message(
                "Iltimos post uchun textni yuboring!"
            )
            return POST_TEXT

    def post_media_video(self, update: Update, context: CallbackContext):
        user, dbUser = self.getUser(update)
        context.user_data['post']['media'] = update.message.video.file_id
        context.user_data['post']['media_type'] = 2

        if update.message.caption:
            context.user_data['post']['caption'] = update.message.caption
            context.user_data['post']['caption_entities'] = update.message.caption_entities
            user.send_message(
                "Iltimos postni tasdiqlang"
            )
            user.send_video(
                update.message.video.file_id,
                caption=update.message.caption,
                caption_entities=update.message.caption_entities,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Tasdiqlash",
                                callback_data="post_accept"
                            ),
                            InlineKeyboardButton(
                                "Bekor qilish",
                                callback_data="post_decline"
                            )
                        ]
                    ]
                )
            )
            return CHECK_POST

        else:
            user.send_message(
                "Iltimos post uchun textni yuboring!"
            )
            return POST_TEXT

    def post_media_document(self, update: Update, context: CallbackContext):
        user, dbUser = self.getUser(update)

        context.user_data['post']['media'] = update.message.document.file_id
        context.user_data['post']['media_type'] = 3

        if update.message.caption:
            context.user_data['post']['caption'] = update.message.caption
            context.user_data['post']['caption_entities'] = update.message.caption_entities
            user.send_message(
                "Iltimos postni tasdiqlang"
            )
            user.send_document(
                update.message.document.file_id,
                caption=update.message.caption,
                caption_entities=update.message.caption_entities,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Tasdiqlash",
                                callback_data="post_accept"
                            ),
                            InlineKeyboardButton(
                                "Bekor qilish",
                                callback_data="post_decline"
                            )
                        ]
                    ]
                )
            )
            return CHECK_POST

        else:
            user.send_message(
                "Iltimos post uchun textni yuboring!"
            )
            return POST_TEXT

    def only_text(self, update: Update, context: CallbackContext):
        user, dbUser = self.getUser(update)
        context.user_data['post']['media_type'] = 0

        user.send_message(
            "Iltimos post uchun text yuboring!",
        )
        return POST_TEXT

    def post_text(self, update: Update, context: CallbackContext):
        user, dbUser = self.getUser(update)
        context.user_data['post']['caption'] = update.message.text
        context.user_data['post']['caption_entities'] = update.message.entities
        post = context.user_data['post']
        user.send_message(
            "Iltimos postni tasdiqlang"
        )
        if post['media_type'] == 1:
            self.bot.send_photo(
                user.id,
                post['media'],
                caption=post['caption'],
                caption_entities=post['caption_entities'],
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Tasdiqlash",
                                callback_data="post_accept"
                            ),
                            InlineKeyboardButton(
                                "Bekor qilish",
                                callback_data="post_decline"
                            )
                        ]
                    ]
                )
            )
        elif post['media_type'] == 2:
            self.bot.send_video(
                user.id,
                post['media'],
                caption=post['caption'],
                caption_entities=post['caption_entities'],
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Tasdiqlash",
                                callback_data="post_accept"
                            ),
                            InlineKeyboardButton(
                                "Bekor qilish",
                                callback_data="post_decline"
                            )
                        ]
                    ]
                )
            )
        elif post['media_type'] == 3:
            self.bot.send_document(
                user.id,
                post['media'],
                caption=post['caption'],
                caption_entities=post['caption_entities'],
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Tasdiqlash",
                                callback_data="post_accept"
                            ),
                            InlineKeyboardButton(
                                "Bekor qilish",
                                callback_data="post_decline"
                            )
                        ]
                    ]
                )
            )
        else:
            self.bot.send_message(
                user.id,
                text=post['caption'],
                entities=post['caption_entities'],
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Tasdiqlash",
                                callback_data="post_accept"
                            ),
                            InlineKeyboardButton(
                                "Bekor qilish",
                                callback_data="post_decline"
                            )
                        ]
                    ]
                )
            )

        # user.send_message(
        #     update.message.text,
        #     entities=update.message.entities,
        #     reply_markup=InlineKeyboardMarkup(
        #         [
        #             [
        #                 InlineKeyboardButton(
        #                     "Tasdiqlash",
        #                     callback_data="post_accept"
        #                 ),
        #                 InlineKeyboardButton(
        #                     "Bekor qilish",
        #                     callback_data="post_decline"
        #                 )
        #             ]
        #         ]
        #     )
        # )
        return CHECK_POST

    def check_post(self, update: Update, context: CallbackContext):
        user, dbUser = self.getUser(update)
        if update.callback_query.data == "post_accept":
            user.send_message(
                "Post tasdiqlandi!"
            )
            self.post_send(context.user_data['post'])
            return ConversationHandler.END
        else:
            return self.post(update, context)

    def post_send(self, post):
        users: list[User] = User.objects.all() if post['receivers'] == 0 else (
            User.objects.filter(is_registered=False) if post['receivers'] == 1 else User.objects.filter(
                is_registered=True)
        )
        users = users.filter(is_admin=False)
        if post['media_type'] == 1:
            for user in users:
                self.bot.send_photo(
                    user.id,
                    post['media'],
                    caption=post['caption'],
                    caption_entities=post['caption_entities']
                )
        elif post['media_type'] == 2:
            for user in users:
                self.bot.send_video(
                    user.id,
                    post['media'],
                    caption=post['caption'],
                    caption_entities=post['caption_entities']
                )
        elif post['media_type'] == 3:
            for user in users:
                self.bot.send_document(
                    user.id,
                    post['media'],
                    caption=post['caption'],
                    caption_entities=post['caption_entities']
                )
        else:
            for user in users:
                self.bot.send_message(
                    user.id,
                    text=post['caption'],
                    entities=post['caption_entities']
                )
