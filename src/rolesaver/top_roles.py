from .db_cmd import get_top_roles, get_top_roles_detailed, get_user_roles, check_player_ban
from . import updater, BotStats, check_channel_join
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import mention_markdown
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from random import choice

bot = updater.bot

roles_by_emoji = {'👱': {'role_title': 'روستایی ساده', 'role_id': 1}, '🐺': {'role_title': 'گرگینه', 'role_id': 2},
                  '🍻': {'role_title': 'مست', 'role_id': 3}, '👳': {'role_title': 'پیشگو', 'role_id': 4},
                  '😾': {'role_title': 'نفرین شده', 'role_id': 5}, '💋': {'role_title': 'فاحشه', 'role_id': 6},
                  '👁': {'role_title': 'ناظر', 'role_id': 7}, '🔫': {'role_title': 'تفنگدار', 'role_id': 8},
                  '🖕': {'role_title': 'خائن', 'role_id': 9}, '👼': {'role_title': 'فرشته نگهبان', 'role_id': 10},
                  '🕵️': {'role_title': 'کاراگاه', 'role_id': 11}, '🙇': {'role_title': 'پیشگوی رزرو', 'role_id': 12},
                  '👤': {'role_title': 'فرقه گرا', 'role_id': 13}, '💂': {'role_title': 'شکارچی', 'role_id': 14},
                  '👶': {'role_title': 'بچه وحشی', 'role_id': 15}, '🃏': {'role_title': 'احمق', 'role_id': 16},
                  '👷': {'role_title': 'فراماسون', 'role_id': 17}, '🎭': {'role_title': 'همزاد', 'role_id': 18},
                  '💘': {'role_title': 'الهه عشق', 'role_id': 19}, '🎯': {'role_title': 'کلانتر', 'role_id': 20},
                  '🔪': {'role_title': 'قاتل زنجیره ای', 'role_id': 21}, '👺': {'role_title': 'منافق', 'role_id': 22},
                  '🎖': {'role_title': 'کدخدا', 'role_id': 23}, '👑': {'role_title': 'شاهزاده', 'role_id': 24},
                  '🔮': {'role_title': 'جادوگر', 'role_id': 25}, '🤕': {'role_title': 'پسر گیج', 'role_id': 26},
                  '⚒': {'role_title': 'آهنگر', 'role_id': 27}, '⚡️': {'role_title': 'گرگ آلفا', 'role_id': 28},
                  '🐶': {'role_title': 'توله گرگ', 'role_id': 29}, '💤': {'role_title': 'خواب گذار', 'role_id': 30},
                  '🌀': {'role_title': 'پیشگوی نگاتیوی', 'role_id': 31},
                  '👱🌚': {'role_title': 'گرگ نما', 'role_id': 32}, '🐺🌝': {'role_title': 'گرگ ایکس', 'role_id': 33},
                  '☮️': {'role_title': 'صلح گرا', 'role_id': 34}, '📚': {'role_title': 'ریش سفید', 'role_id': 35},
                  '😈': {'role_title': 'دزد', 'role_id': 36}, '🤯': {'role_title': 'دردسرساز', 'role_id': 37},
                  '👨‍🔬': {'role_title': 'شیمیدان', 'role_id': 38},
                  '🐺☃️': {'role_title': 'گرگ برفی', 'role_id': 39}, '☠️': {'role_title': 'گورکن', 'role_id': 40},
                  '🔥': {'role_title': 'آتش زن', 'role_id': 41}, '🦅': {'role_title': 'رمال', 'role_id': 42}}

emoji_by_roles = {role['role_id']: role['role_title'] + emoji for emoji, role in roles_by_emoji.items()}

alefba = 'آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی'
emoji_by_roles = {k: v for k, v in sorted(emoji_by_roles.items(), key=lambda x: alefba.index(x[1][0]))}


@check_channel_join
@check_player_ban
@run_async
def most_roles(update, context):
    chat = update.message.chat
    user = update.message.from_user
    if context.args:
        if context.args[0].isdigit():
            days = int(context.args[0])
            if 1 <= days <= 31:
                pass
            else:
                days = 7
        else:
            days = 7
    else:
        days = 7
    if chat.id != user.id:
        texts = update.chat_lang.Mostroles
        if chat.id in [-1001444185267, -1001461432821]:
            all_groups = True
            chat_title = texts.all_groups
        else:
            all_groups = False
            chat_title = chat.title

        most_roles_list = get_top_roles(chat.id, days, all_groups)
        text = texts.most_header.format(days, chat_title)
        if not most_roles_list:
            text = texts.no_role.format(days)
        counter = 0
        for user, role, tedad in most_roles_list:
            try:
                if all_groups:
                    user = mention_markdown(user, bot.get_chat(user).first_name)
                else:
                    user = bot.get_chat_member(chat.id, user).user.mention_markdown()
                counter += 1
                role = emoji_by_roles[role]
                text += f'\n{counter} - {user} | {role} | {tedad}'
            except:
                continue
        BotStats.most_roles += 1
    else:
        texts = update.user_lang.Mostroles
        most_roles_list = get_user_roles(user.id, days)
        text = texts.pv_most_header.format(days)
        if not most_roles_list:
            text = texts.no_role_pv.format(days)
        for role, tedad in most_roles_list:
            role = emoji_by_roles[role]
            text += f'\n{role} | {tedad}'
        BotStats.most_roles_pv += 1
    update.message.reply_text(text, quote=False, parse_mode='markdown')


@check_channel_join
@check_player_ban
@run_async
def most_roles_detailed(update, context):
    btns = []
    tmp = []
    if update.message:
        chat_id = update.message.chat.id
    else:
        chat_id = int(update.callback_query.data.split()[2])
    for role_id, role in emoji_by_roles.items():
        if len(tmp) % 3 == 0:
            btns.append(tmp)
            tmp = []
        tmp.append(InlineKeyboardButton(role, callback_data=f'most_roles {role_id} {chat_id}'))
    if tmp:
        btns.append(tmp)
    texts_pv = update.user_lang.Mostroles
    texts_chat = update.chat_lang.Mostroles
    if update.message:
        try:
            context.bot.send_message(update.message.from_user.id, texts_pv.which,
                                     reply_markup=InlineKeyboardMarkup(btns))
            update.message.reply_text(texts_chat.panel_pv)
            BotStats.most_roles_detailed += 1
        except:
            update.message.reply_text(texts_chat.start_first)
    else:
        update.callback_query.message.edit_text(
            (texts_pv.which if isinstance(texts_pv.which, str) else choice(texts_pv.which)),
            reply_markup=InlineKeyboardMarkup(btns))


@run_async
def most_roles_buttons(update, context):
    data = update.callback_query.data
    chat_id = int(data.split()[2])
    texts = update.user_lang.Mostroles
    if chat_id in [-100144418527, -1001461432821]:
        all_groups = True
        chat_title = texts.all_groups
    else:
        all_groups = False
        chat_title = context.bot.get_chat(chat_id).title
    role_id = int(data.replace('most_roles ', '').split()[0])
    if not role_id:
        most_roles_detailed(update, context)
        return
    role_name = emoji_by_roles[role_id]
    most_roles_list = get_top_roles_detailed(chat_id, 7, role_id, all_groups)
    text = texts.most_header_det.format(role_name, chat_title)
    if not most_roles:
        text = texts.no_role_det.format(role_name)
    counter = 0
    for user, tedad in most_roles_list:
        try:
            if all_groups:
                user = mention_markdown(user, bot.get_chat(user).first_name)
            else:
                user = bot.get_chat_member(chat_id, user).user.mention_markdown()
            counter += 1
            text += f'\n{counter} - {user} | {tedad}'
        except:
            continue
    buttons = [[InlineKeyboardButton(texts.back_list, callback_data=f'most_roles 0 {chat_id}')]]
    update.callback_query.message.edit_text(text, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(buttons))
