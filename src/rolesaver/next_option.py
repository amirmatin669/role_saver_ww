from telegram.ext.dispatcher import run_async
from .db_cmd import set_next as db_set_next, get_next, get_admins_id
from . import updater
from .multilanger import return_lang

bot = updater.bot


@run_async
def set_next(update, context):
    reply_msg = update.message.reply_to_message
    chat_id = update.message.chat_id
    texts = update.chat_lang.Setnext
    t = bot.get_chat_member(chat_id, update.message.from_user.id)
    if t.status in ('creator', 'administrator') or update.message.from_user.id in get_admins_id():
        if reply_msg:
            if not reply_msg.text:
                next_media = reply_msg.effective_attachment
                next_media_id = next_media.file_id if not isinstance(next_media, list) else next_media[
                    0].file_id
                media_types = {
                    0: reply_msg.text,
                    1: reply_msg.sticker,
                    2: reply_msg.photo,
                    3: reply_msg.video,
                    4: reply_msg.animation,
                    5: reply_msg.audio,
                    6: reply_msg.voice,
                    7: reply_msg.video_note,
                    8: reply_msg.document
                }
                for media_type in media_types:
                    if media_types[media_type]:
                        next_type = media_type
                        break
                else:
                    return
            else:
                next_media_id = None
                next_type = 0
            if reply_msg.text:
                next_text = reply_msg.text_html
            elif reply_msg.caption:
                next_text = reply_msg.caption_html
            else:
                next_text = None
            db_set_next(update.message.chat.id, next_text, next_media_id, next_type)
            update.message.reply_text(texts.next_saved)
        else:
            update.message.reply_text(texts.rep)
    else:
        update.message.reply_text(texts.admin)


def send_next(chat_id):
    chat_data = get_next(chat_id)
    texts = return_lang(chat_id).Setnext
    if chat_data:
        next_text, next_media_id, next_type = chat_data
        media_types = {
            0: bot.send_message,
            1: bot.send_sticker,
            2: bot.send_photo,
            3: bot.send_video,
            4: bot.send_animation,
            5: bot.send_audio,
            6: bot.send_voice,
        }
        action = media_types.get(next_type)
        msg = action(chat_id, text=next_text, caption=next_text,
                     sticker=next_media_id, audio=next_media_id,
                     photo=next_media_id, video=next_media_id, animation=next_media_id,
                     voice=next_media_id, parse_mode='html')
        try:
            bot.pin_chat_message(chat_id, msg.message_id)
        except Exception as e:
            pass
    else:
        bot.send_message(chat_id, texts.setst,
                         parse_mode='html')
    return True
