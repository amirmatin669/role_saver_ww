from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .RANK_STATEMENT import get_cur
import datetime
from . import BotStats, check_channel_join
from .db_cmd import check_player_ban

conn, cur = get_cur()
ranks = {}
time = datetime.datetime.now()


def select(Id):
    global time, ranks
    try:
        selected = ranks[Id]['emoji']
        parent_id = ranks[Id]['parent']
    except:
        cur.execute(f"SELECT emoji, parent_id, id FROM v2.ranks")
        result = cur.fetchall()
        for x in result:
            if x[2] < 0:
                None
            else:
                ranks[x[2]] = {'emoji': x[0],
                               'parent': x[1]}
        time = datetime.datetime.now() + datetime.timedelta(hours=12)
        selected = ranks[Id]['emoji']
        parent_id = ranks[Id]['parent']
    return selected, parent_id


def get_emojii(user_id):
    cur.execute(
        f"SELECT rank_id FROM v2.members_ranks WHERE user_id={user_id} AND disabled_at IS NULL ORDER BY rank_id")
    all_emojies = cur.fetchall()
    emojies = []
    for x in all_emojies:
        if type(x) is tuple:
            for z in x:
                emojies.append(z)
        else:
            emojies.append(x)

    cur.execute(f"SELECT * FROM v2.selected_emojies_by_user WHERE user_id={user_id}")
    result = cur.fetchall()
    if not result:
        emoji_id1 = 0
        emoji_id2 = 0
        emoji_id3 = 0
        for x in all_emojies:
            emo, pare = select(x[0])
            if pare == -1:
                if x[0] > emoji_id1:
                    emoji_id1 = x[0]
                else:
                    None
            elif pare == -2:
                if x[0] > emoji_id2:
                    emoji_id2 = x[0]
                else:
                    None
            elif pare == -3:
                if x[0] > emoji_id3:
                    emoji_id3 = x[0]
                else:
                    None
        cur.execute(
            f"INSERT INTO v2.selected_emojies_by_user (user_id, group_emoji, main_emoji, donor_emoji) VALUES ({user_id}, {emoji_id1}, {emoji_id2}, {emoji_id3})")
        conn.commit()
        cur.execute(f"SELECT * FROM v2.selected_emojies_by_user WHERE user_id={user_id}")
        result = cur.fetchall()
    return result, emojies


@check_channel_join
@check_player_ban
def panel_emoji(update, context):
    result, emojies = get_emojii(update.effective_user.id)
    texts = update.chat_lang.Mypanel
    if result[0][1] == 0:
        emoji1 = '-'
    else:
        rawemo = result[0][1]
        emoji1, p = select(rawemo)
    if result[0][2] == 0:
        emoji2 = '-'
    else:
        rawemo = result[0][2]
        emoji2, p = select(rawemo)
    if result[0][3] == 0:
        emoji3 = '-'
    else:
        rawemo = result[0][3]
        emoji3, p = select(rawemo)
    keyboards = [[InlineKeyboardButton(str(emoji1), callback_data='e-panel pannel1'),
                  InlineKeyboardButton(str(emoji2), callback_data='e-panel pannel2'),
                  InlineKeyboardButton(str(emoji3), callback_data="e-panel pannel3")],
                 [InlineKeyboardButton(texts.quit, callback_data='e-panel exitp')]]
    if update.callback_query:
        update.callback_query.edit_message_text(texts.welcome_select, reply_markup=InlineKeyboardMarkup(keyboards))
    else:
        def send_app(chat_id):
            context.bot.send_message(chat_id, texts.welcome_select, reply_markup=InlineKeyboardMarkup(keyboards))
            BotStats.panel_emoji += 1

        if update.message.chat.type == 'private':
            texts = update.user_lang.Mypanel
            send_app(update.message.chat.id)
        else:
            try:
                send_app(update.message.from_user.id)
                update.message.reply_text(texts.sent_pv)
            except:
                keyboard = [[InlineKeyboardButton('Start me', 't.me/role_ww_bot')]]
                context.bot.send_message(update.message.chat.id, texts.start_pv,
                                         reply_markup=InlineKeyboardMarkup(keyboard),
                                         reply_to_message_id=update.message.message_id)


def panel_emoji_c(update, context):
    query = update.callback_query
    data = query.data
    data = data.replace('e-panel ', '')
    texts = update.user_lang.Mypanel
    if data == 'exitp':
        query.edit_message_text(texts.panel_close)
    else:
        result, emojies = get_emojii(update.effective_user.id)
        parent1 = {}
        parent2 = {}
        parent3 = {}
        for x in emojies:
            selected, parent_id = select(x)
            if parent_id == -1:
                parent1[selected] = x
            elif parent_id == -2:
                parent2[selected] = x
            elif parent_id == -3:
                parent3[selected] = x

        def sm(sec):
            parents = None
            section = None
            Id = None
            if sec == 'pannel1':
                section = texts.group
                parents = parent1
                Id = -1
            elif sec == 'pannel2':
                section = texts.pub
                parents = parent2
                Id = -2
            elif sec == 'pannel3':
                section = texts.don
                parents = parent3
                Id = -3
            keyboard = []
            rowperemoji = []
            for x, y in parents.items():
                if len(rowperemoji) == 4:
                    keyboard.append(rowperemoji.copy())
                    rowperemoji.clear()
                if result[0][Id * -1] == y:
                    x += '✅'
                rowperemoji.append(InlineKeyboardButton(x, callback_data='e-panel ' + str(y)))
            if len(rowperemoji) != 0:
                keyboard.append(rowperemoji.copy())
                rowperemoji.clear()
            keyboard.append([InlineKeyboardButton(texts.back, callback_data='e-panel returnp')])
            query.edit_message_text(texts.panel_section.format(section), reply_markup=InlineKeyboardMarkup(keyboard))

        if 'pannel' in data:
            sm(data)
        elif data == 'returnp':
            panel_emoji(update, context)
        elif data not in ['returnp', 'pannel1', 'pannel2', 'pannel3']:
            data = int(data)
            emoji, parent_id = select(data)
            if parent_id == -2:
                cur.execute(
                    f'UPDATE v2.selected_emojies_by_user SET main_emoji={data} WHERE user_id={update.effective_user.id}')
            elif parent_id == -3:
                cur.execute(
                    f'UPDATE v2.selected_emojies_by_user SET donor_emoji={data} WHERE user_id={update.effective_user.id}')
            elif parent_id == -1:
                cur.execute(
                    f"UPDATE v2.selected_emojies_by_user SET group_emoji={data} WHERE user_id={update.effective_user.id}")
            conn.commit()
            result, emojies = get_emojii(update.effective_user.id)
            parent1 = {}
            parent2 = {}
            parent3 = {}
            for x in emojies:
                selected, parentId = select(x)
                if parentId == -1:
                    parent1[selected] = x
                elif parentId == -2:
                    parent2[selected] = x
                elif parentId == -3:
                    parent3[selected] = x
            sm(f"pannel{parent_id * -1}")
