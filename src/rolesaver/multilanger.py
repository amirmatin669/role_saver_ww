from telegram import Update, Bot
from .db_cmd import get_chat_lang
from .texts import texts_fa, texts_en, texts_fb
from random import choice


def chat_lang(self) -> texts_fa:
    return return_lang(self.effective_chat.id)


def user_lang(self) -> texts_fa:
    return return_lang(self.effective_user.id)


def return_lang(chat_id) -> texts_fa:
    lang = get_chat_lang(chat_id)
    if lang == 'fa':
        return texts_fa
    elif lang == 'fb':
        return texts_fb
    elif lang == 'en':
        return texts_en
    else:
        return texts_fa


def custom_sendmsg(self,
                   chat_id,
                   text,
                   parse_mode=None,
                   disable_web_page_preview=None,
                   disable_notification=False,
                   reply_to_message_id=None,
                   reply_markup=None,
                   timeout=None,
                   **kwargs):
    if isinstance(text, (list, tuple)):
        text = choice(text)
    return sndmsg(self,
                  chat_id,
                  text,
                  parse_mode=parse_mode,
                  disable_web_page_preview=disable_web_page_preview,
                  disable_notification=disable_notification,
                  reply_to_message_id=reply_to_message_id,
                  reply_markup=reply_markup,
                  timeout=timeout,
                  **kwargs)


sndmsg = Bot.send_message
Bot.send_message = custom_sendmsg

Update.chat_lang = property(chat_lang)
Update.user_lang = property(user_lang)
