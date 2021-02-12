import html
import logging
import re
import time
from random import choice
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler, InlineQueryHandler
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import mention_html as mention
from jdatetime import datetime
from pytz import timezone
from . import inline_handler, multilanger
from . import updater, BotStats, lab, check_channel_join
from .cache import *
from .db_cmd import *
from .most_votes import most_votes
from .next_option import set_next
from .top_roles import most_roles, most_roles_buttons, most_roles_detailed
from .score_for_lupine import check_list, offscore, onscore, bests_list
from .emoji_panel import panel_emoji, panel_emoji_c
from .gift_emoji import emoji_gift_start

bot = updater.bot
dp = updater.dispatcher

iran = timezone('Asia/Tehran')
roles_v2 = {}


def update_roles_dict(text, chat_id):
    global roles_v2
    roles_v2[chat_id] = {''.join(i.split(':')[:-1]): {'state': i.split(':')[-1].split('-')[0],
                                                      'role': i.split(':')[-1].split('-')[1] if len(
                                                          i.split(':')[-1].split('-')) == 2 else False} for i in
                         text.split('\n')[1:-1] if i}


def now():
    sa_time = datetime.now(iran)
    return sa_time.strftime('%Y-%m-%d %H:%M:%S')


@run_async
def addusers(users, chat_id):
    # todo
    users = [bot.get_chat_member(chat_id=chat_id, user_id=user).user for user in users]
    data = []
    for user in users:
        data.append({
            'username': user.username,
            'user_id': user.id,
            'time': now()
        })
    update_user(data)


@check_channel_join
@run_async
def set_rule(update, context):
    user_id = update.message.from_user['id']
    chat_id = update.message.chat_id
    status = get_player_status(chat_id, user_id)
    allow_users = get_allow_players(update.message.chat_id)
    texts = update.chat_lang.Sn
    if status:
        pass
    elif not allow_users:
        update.message.reply_text(texts.start_a_game)
        return
    elif status and user_id in allow_users:
        update.message.reply_text(texts.admin_unblock)
    if not status:
        rules = get_group_rules(chat_id)
        if rules:
            if not rules['saverole']:
                update.message.reply_text(texts.inactive)
                return
        if not update.message.__dict__['reply_to_message']:
            all_players = get_all_players(update.message.chat_id)
            if all_players:
                if user_id in allow_users:
                    length = update.message.entities[0]['length']
                    text = update.message.text
                    role = text[int(length):len(text)]
                    if not role:
                        msg = texts.dont_blow
                        if user_id == 798494834:
                            msg = texts.amitis_no_role
                        update.message.reply_text(msg)
                    if role:
                        user = {
                            'id': user_id,
                            'role': role.replace('\n', ' '),
                            # 'username': update.message.from_user.username
                        }
                        add_rule(update.message.chat_id, user)
                        msg = ''
                        if user_id == 798494834:
                            msg = texts.amitis_saved
                        update.message.reply_text(msg) if msg else None
                        BotStats.roles_set += 1
                elif user_id not in allow_users and user_id in all_players:
                    msg = texts.check_youre_dead
                    if user_id == 798494834:
                        msg = texts.check_youre_dead_amitis
                    update.message.reply_text(msg)
                elif user_id not in allow_users:
                    msg = texts.not_in_game
                    if user_id == 798494834:
                        msg = texts.not_in_game_amitis
                    update.message.reply_text(msg)

            if not all_players:
                update.message.reply_text(texts.start_a_game)


@check_channel_join
@run_async
def set_shekarchi(update, context):
    user = update.message.from_user
    chat_id = update.message.chat_id
    user_id = update.message.from_user['id']
    status = get_player_status(chat_id, user_id)
    texts = update.chat_lang.Shekar
    if not status:
        rules = get_group_rules(chat_id)
        if rules:
            t = bot.get_chat_member(chat_id=chat_id, user_id=int(user.id))
        if t.status == 'creator' or t.status == 'administrator' or update.message.from_user.id in get_admins_id():
            if update.message.reply_to_message:
                rep_user = update.message.reply_to_message.from_user
                set_shekarchi_db(chat_id, rep_user.id)
                add_rule(chat_id, {'id': rep_user.id, 'role': 'ch'})
                t = bot.get_chat_member(chat_id=chat_id, user_id=int(rep_user.id)).user
                context.bot.send_message(chat_id,
                                         # f'[{t.name.replace("]","").replace("[","")}](tg://user?id={rep_user.id}) شکارچی بازی شد ',
                                         texts.ch_set.format(mention(rep_user.id, t.name)),
                                         parse_mode='HTML')
            elif not update.message.reply_to_message:
                update.message.reply_text(texts.rep_ch)
            BotStats.shekars_set += 1
        else:
            update.message.reply_text(texts.only_admins)


@check_channel_join
@run_async
def set_nazer(update, context):
    user = update.message.from_user
    chat_id = update.message.chat_id
    t = bot.get_chat_member(chat_id=chat_id, user_id=int(user.id))
    if t.status == 'creator' or t.status == 'administrator' or update.message.from_user.id in get_admins_id():
        if update.message.reply_to_message:
            rep_user = update.message.reply_to_message.from_user
            set_nazer_db(chat_id, rep_user.id)
        elif not update.message.reply_to_message:
            update.message.reply_text("روی ناظر این دستور رو باید بزنید")

    else:
        update.message.reply_text('تنها مدیران میتوانند از این دستور استفاده کنن')


@check_player_ban
@run_async
def set_vote(update, context):
    chat_id = update.message.chat_id
    user_id = update.message.from_user['id']
    texts = update.chat_lang.Sv
    user = update.message.from_user
    chat_id = update.message.chat_id
    shekarchi = get_shekarchi_db(chat_id)
    rules = get_group_rules(chat_id)
    if rules:
        if not rules['shekar']:
            update.message.reply_text(texts.inactive)
            return
    if shekarchi:
        if user.id == shekarchi:
            length = update.message.entities[0]['length']
            text = update.message.text
            try:
                allow_users = get_allow_players(chat_id)
                ents = update.message.entities[1:]
                if ents:
                    if update.message.entities[1].user:
                        user_id = update.message.entities[1].user.id
                        if user_id in allow_users:
                            vote = user_id
                        else:
                            update.message.reply_text(texts.not_alive)
                            return None
                    elif update.message.entities[1].type == 'mention':
                        start = update.message.entities[1].offset
                        length = update.message.entities[1].length
                        username = text[int(start) + 1:int(start) + int(length)]
                        try:
                            user_id = get_user_id_from_username(username)
                        except Exception as e:
                            user_id = None
                        if user_id:
                            if user_id in allow_users:
                                vote = user_id
                            else:
                                update.message.reply_text(texts.not_alive)
                                return None
                        else:
                            vote = ' '.join(update.message.text.split(' ')[1:])
                else:
                    vote = ' '.join(update.message.text.split(' ')[1:])
            except:
                update.message.reply_text(texts.like_this)
                return
            if vote:
                set_vote_db(chat_id, vote)
                update.message.reply_text(texts.vote_saved)
                BotStats.votes_saved += 1
            elif not vote:
                update.message.reply_text(texts.like_this)
        elif user.id != shekarchi:
            update.message.reply_text(texts.only_ch)
    elif not shekarchi:
        update.message.reply_text(texts.no_ch)


from telegram.utils.helpers import mention_markdown, escape_markdown


@check_player_ban
@run_async
def say_vote(update, context):
    chat_id = update.message.chat_id
    vote = get_vote_db(chat_id)
    user_id = update.message.from_user['id']
    texts = update.chat_lang.Vt
    rules = get_group_rules(chat_id)
    if rules:
        if not rules['shekar']:
            update.message.reply_text(texts.inactive)
            return
    shekar = get_shekarchi_db(chat_id)
    if shekar in get_allow_players(chat_id):
        allow_users = get_allow_players(chat_id)
        if vote:
            if vote.isdigit() and int(vote) in allow_users:
                t = bot.get_chat_member(chat_id=chat_id, user_id=int(vote)).user
                msg = choice(texts.say_vote).format(mention_markdown(int(vote), escape_markdown(t.name)))
                context.bot.send_message(chat_id, msg, parse_mode='Markdown')
                time.sleep(2)
                context.bot.send_message(chat_id, msg, parse_mode='Markdown')
                time.sleep(3)
                context.bot.send_message(chat_id, msg, parse_mode='Markdown')
                BotStats.votes_said += 1
            elif vote.isdigit() and int(vote) not in allow_users:
                if shekar:
                    update.message.reply_text(texts.vote_dead)
                    t = bot.get_chat_member(chat_id=chat_id, user_id=int(shekar)).user
                    context.bot.send_message(
                        chat_id,
                        texts.whos_vote.format(mention_markdown(int(vote), escape_markdown(t.first_name))),
                        parse_mode='Markdown'
                    )
                if not shekar:
                    update.message.reply_text(texts.no_ch)
            else:
                if shekar:
                    msg = choice(texts.say_vote).format(vote)
                    context.bot.send_message(chat_id, msg, parse_mode='Markdown')
                    time.sleep(2)
                    context.bot.send_message(chat_id, msg, parse_mode='Markdown')
                    time.sleep(3)
                    context.bot.send_message(chat_id, msg, parse_mode='Markdown')
                    BotStats.votes_said += 1
                if not shekar:
                    update.message.reply_text(texts.no_ch)
        else:
            update.message.reply_text(texts.no_vote)
    else:
        update.message.reply_text(texts.ch_dead)


game_finish = r'طول مدت بازی|مدت زمان بازی|مدت بازی|مدت بُکُن بُکُن'
game_list = r'بازیکن های زنده|فراموشکارای زنده|هنرمندای فعال|دانشجوهای مشغول به تحصیل|مسافرای زنده ی توی قطار|بازیکنان زنده|بازیکن های آنلاین|کونده های زنده |بازیکنان درحال بازی|برره ای های زنده|مسافر های زنده:|کشتی گیران سالم|هیولاهای زنده|بازمانده ها'
death = r'مرده|اخراج شده|کنار رفته|آفلاین|تبعید شده|بگا رفته|خارج شده|سقَط شده|فرار کرده|اخراج شده|نفله وشده'

from .methods import finish_game, update_game, start_game, make_user_role_list_v0, make_user_role_list_v1


@check_player_ban
@run_async
def update_list(update, context):
    global roles_v2
    user_id = update.message.from_user['id']
    chat_id = update.message.chat_id
    texts = update.chat_lang.Up

    if not update.message.reply_to_message or update.message.reply_to_message.from_user.id not in get_game_bots_id():
        update.message.reply_text(texts.rep_to_bot)
        return
    if update.message.reply_to_message.message_id in get_used_message(chat_id):
        update.message.reply_text(texts.used_list)
        return

    text = update.message.reply_to_message.text
    ents = update.message.reply_to_message['entities']
    if re.search(game_finish, text):
        msg = finish_game(update.message.chat_id, update.message.reply_to_message.message_id)
        context.bot.send_message(chat_id, msg)

    elif re.search(death, text):
        allow_users = []
        for ent in ents:
            if ent['type'] == 'text_mention':
                allow_users.append(ent['user'].id)
        players_data = {'players': allow_users}

        if chat_id == -1001414470547:
            update_msg = '-Lιѕт Uρɗαтєɗ Ɓу -Nιмα ☻'
        elif chat_id == -1001423339319:
            update_msg = 'Janan  لیست را اپدیت کرد'
        elif chat_id == -1001482994041:
            update_msg = 'ᯓ𝑴𝒐𝒉𝒎𝒅࿈ updated list'
        elif chat_id == -1001128468995:
            update_msg = 'ʟɪsᴛ ᴜᴘᴅᴀᴛᴇᴅ ʙʏ Ãℳℐℛ_Kh'
        elif chat_id == -1001259701545:
            update_msg = 'ʟɪsᴛ ᴜᴘᴅᴀᴛᴇᴅ ʙʏ _Aмeeɴ⃤'
        elif chat_id == -1001410480062:
            update_msg = '''𝐋𝐢𝐬𝐭 𝐔𝐩𝐝𝐚𝐭𝐞𝐝 𝐁𝐲:\n★ • Mєhrαn .• | ¤ 🇮🇱 ¤ | •.'''
        elif chat_id == -1001476763360:
            update_msg = 'ʟɪsᴛ ᴜᴘᴅᴀᴛᴇᴅ ʙʏ ✵αg ғᴛ #Ⲋɧίɳ'
        else:
            update_msg = texts.list_updated
        context.bot.send_message(chat_id, update_msg)
        update_game(chat_id, allow_users, update.message.reply_to_message.message_id, text)

    elif re.search(game_list, text):
        allow_users = []
        users = []
        for ent in ents:
            if ent['type'] == 'text_mention':
                allow_users.append(ent['user'].__dict__['id'])
                users.append(ent.user)
        players_data = {
            'players': allow_users
        }
        start_game(chat_id, allow_users, update.message.reply_to_message.message_id, text)
    else:
        pass
    BotStats.lists_updated += 1


@run_async
def ban(update, context):
    t = bot.get_chat_member(chat_id=update.message.chat_id, user_id=int(update.message.from_user['id']))
    texts = update.chat_lang.Block
    if update.message.from_user.id == update.message.reply_to_message.from_user.id:
        update.message.reply_text(texts.cant)
        return
    if t.status == 'creator' or t.status == 'administrator' or update.message.from_user.id in get_admins_id():
        status = get_player_status(update.message.chat_id, update.message.reply_to_message.from_user['id'])
        if status:
            update.message.reply_text(texts.ban_before)
        if not status:
            ban_user(update.message.chat_id, update.message.reply_to_message.from_user, update.message.from_user)
            update.message.reply_text(texts.banned)
    else:
        update.message.reply_text(texts.go_admin)


@run_async
def unban(update, context):
    status = get_player_status(update.message.chat_id, update.message.reply_to_message.from_user['id'])
    t = bot.get_chat_member(chat_id=update.message.chat_id, user_id=int(update.message.from_user['id']))
    texts = update.chat_lang.Unblock
    if t.status == 'creator' or t.status == 'administrator' or update.message.from_user.id in get_admins_id():
        if status:
            unban_user(update.message.chat_id, update.message.reply_to_message.from_user,
                       update.message.from_user)
            update.message.reply_text(texts.unblocked)

        if not status:
            update.message.reply_text(texts.good_guy)
    else:
        update.message.reply_text(texts.only_admin)


@run_async
def delete_role(update, context):
    user_id = update.message.from_user['id']
    chat_id = update.message.chat_id
    t = bot.get_chat_member(chat_id=update.message.chat_id, user_id=int(update.message.from_user['id']))
    if t.status == 'creator' or t.status == 'administrator' or update.message.from_user.id in get_admins_id():
        shekarchi = get_shekarchi_db(chat_id)
        if shekarchi == update.message.reply_to_message.from_user.id:
            set_shekarchi_db(chat_id, None)
        delete_rule(chat_id, update.message.reply_to_message.from_user)
        texts = update.chat_lang.Dl
        update.message.reply_text(texts.ok)


@check_channel_join
@check_player_ban
@run_async
def my_state(update, context):
    user_id = update.message.from_user['id']
    user = update.message.from_user
    chat_id = update.message.chat_id
    info = get_player_info(chat_id, user_id)
    if chat_id == user_id:
        texts = update.user_lang.Mystate
        gp = 'Private'
    else:
        texts = update.chat_lang.Mystate
        gp = mention(update.message.chat_id, update.message.chat['title'])
    # if info:
    if info:
        message = texts.template.format(
            name=mention(update.message.from_user['id'], update.message.from_user['first_name']),
            type=UserStatus(user).status,
            set=info['role_count'],
            gp_set=info['group_role'],
            gp_set_count=info['group_count'],
            gp=gp,
            ranks='|'.join(get_cached_user(user).get_all_emoji_ranks())
        )
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
        BotStats.my_state += 1
    if not info:
        update.message.reply_text(texts.no_use)


@check_channel_join
@check_player_ban
@run_async
def botstats(update, context):
    user_id = update.message.from_user['id']
    chat_id = update.message.chat_id
    info = get_self_data()

    message = '''
<b>Lupine Guys main stats:</b>

<b>∣Confirmed Groups:</b> ‏<code>{groups}</code> 
<b>∣Confirmed Games:</b> ‏<code>{games}</code>
<b>∣Confirmed Plays:</b> ‏<code>{plays}</code>
<b>∣Deleted Mentions:</b> ‏<code>{mentions}</code>
<b>∣Saved Roles:</b> ‏<code>{roles}</code>
<b>∣Users:</b> ‏<code>{users}</code>

█░░ █░░█ █▀▀█ ▀█▀ █▀▀█ █▀▀
█░░ █░░█ █░░█ ░█░ █░░█ █▀▀
▀▀▀ ▀▀▀▀ █▀▀▀ ▀▀▀ ▀░░▀ ▀▀▀
            '''.format(groups='{:,}'.format(int(info['groups'])),
                       roles='{:,}'.format(int(info['roles'])),
                       users='{:,}'.format(int(info['users'])),
                       mentions='{:,}'.format(int(info['deleted_msg'])),
                       plays='{:,}'.format(int(info['confirmed_plays'])),
                       games='{:,}'.format(int(info['confirmed_games'])))
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=message,
        parse_mode='HTML',
        disable_web_page_preview=True
    )


@run_async
def group_state(update, context):
    user_id = update.message.from_user['id']
    chat_id = update.message.chat_id
    status = get_player_status(chat_id, user_id)
    texts = update.chat_lang.Gpstate
    if status:
        pass
    if not status:
        info = get_group_info(chat_id)
        if info:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=texts.template.format(update.message.chat['title'].replace("]", "").replace("[", ""),
                                           update.message.chat['id'], info['all_games_count'], info['role_count'],
                                           info['player_count']),
                parse_mode='Markdown'
            )
        if not info:
            update.message.reply_text(texts.not_used)
        BotStats.gpstate += 1


@check_channel_join
@check_player_ban
@run_async
def save_your_role(update, context):
    user_id = update.message.from_user['id']
    chat_id = update.message.chat_id
    status = get_player_status(chat_id, user_id)
    texts = update.chat_lang.Svu
    rules = get_group_rules(chat_id)
    if rules:
        t = rules['saveyourrole']
        if not t:
            update.message.reply_text(texts.inactive)
            return
    if not get_mention_use(chat_id):
        save_mention_used(chat_id)
        in_game_users = get_allow_players(chat_id)
        all_users = get_all_players(chat_id)
        roleseted_players = get_all_roleseted_players(chat_id)
        users = []
        for user in all_users:
            if user in in_game_users:
                if user not in roleseted_players:
                    users.append(user)

        for user in users:
            t = bot.get_chat_member(chat_id=chat_id, user_id=int(user))
            name = t.user.full_name
            context.bot.send_message(chat_id, text=texts.wur.format(mention(user, name)),
                                     parse_mode='HTML')
            time.sleep(1)
        msg = texts.look_roles.format(len(users)) if isinstance(texts.look_roles, str) else choice(
            texts.look_roles).format(len(users))
        if not users:
            msg = texts.good_guys

        update.message.reply_text(msg)
    else:
        update.message.reply_text(texts.one_time)


@check_channel_join
@check_player_ban
@run_async
def role_list(update, context):
    user_id = update.message.from_user['id']
    chat_id = update.message.chat_id
    list_type = get_list_type(chat_id)
    if list_type == 0 or not list_type:
        try:
            msg = make_user_role_list_v0(chat_id)
        except Exception as e:
            print(e)
            msg = "got error let me check"
        context.bot.send_message(chat_id, msg, parse_mode='HTML', disable_web_page_preview=True)

    elif list_type == 1:
        msg = make_user_role_list_v1(chat_id)
        bot.send_message(chat_id, msg, parse_mode='HTML', disable_web_page_preview=True)
    BotStats.lists_requested += 1


@check_player_ban
@run_async
def vote_equal(update, context):
    chat_id = update.message.chat_id
    user_id = update.message.from_user['id']
    alive_players = get_allow_players(chat_id)
    texts = update.chat_lang.Ev
    if alive_players:
        msg = 'لیست مساوی کردن رای'
        for i in range(0, len(alive_players)):
            user = bot.get_chat_member(chat_id, alive_players[i])
            name = user.user.full_name
            try:
                user_t = bot.get_chat_member(chat_id, alive_players[i + 1])
                name_t = user_t.user.full_name
            except IndexError:
                user_t = bot.get_chat_member(chat_id, alive_players[0])
                name_t = user_t.user.full_name
            msg += f'\n{mention(user.user.id, name)} ➪ {html.escape(name_t)}'
        BotStats.equal_votes += 1
    else:
        msg = texts.no_game
    bot.send_message(chat_id, msg, parse_mode='html')


@run_async
def save_role_reply(update, context):
    # print(update)
    if update.message.reply_to_message.from_user['id'] in [861551208, 920042392, 1084275593]:
        ents = update.message.reply_to_message['entities']

        if update.message.reply_to_message.text.find(
                'نقشت چیه') != -1 or 'لیست کاربران بدون نقش' in update.message.reply_to_message.text \
                or 'لیست کاربر ها' in update.message.reply_to_message.text:
            allow_users = []
            for ent in ents:
                if ent['type'] == 'text_mention':
                    allow_users.append(ent['user'].__dict__['id'])
            shekar = get_shekarchi_db(update.message.chat.id)
            if update.message.from_user['id'] == shekar:
                return
            if update.message.from_user['id'] in allow_users:
                user = {
                    'id': update.message.from_user['id'],
                    'role': update.message.text.replace('\n', ' ')
                    # ,
                    # 'username': update.message.from_user.username
                }

                add_rule(update.message.chat_id, user)

                msg = ''
                if update.message.from_user.id == 798494834:
                    msg = 'نقشت ثبت شد آمیتیس💜'
                update.message.reply_text(msg) if msg else None
        elif update.message.reply_to_message.text.find('رای کیه ؟') != -1:
            allow_users = []
            for ent in ents:
                if ent['type'] == 'text_mention':
                    allow_users.append(ent['user'].__dict__['id'])
            if update.message.from_user['id'] in allow_users:
                # set_vote_db(update.message.chat_id, update.message.text.replace('\n', ' '))
                try:
                    # print(update.message)
                    # print(update.message.entities[1].user)
                    allow_users = get_allow_players(update.message.chat_id)
                    if update.message.entities[0].user:
                        user_id = update.message.entities[0].user.id
                        if user_id in allow_users:
                            vote = user_id
                        else:
                            update.message.reply_text('این شخص زنده نیست')
                    elif update.message.entities[0].type == 'mention':
                        start = update.message.entities[0].offset
                        length = update.message.entities[0].length
                        username = update.message.text[int(start) + 1:int(start) + int(length)]
                        user_id = get_user_id_from_username(username)
                        if user_id:
                            if user_id in allow_users:
                                vote = user_id
                            else:
                                update.message.reply_text('این شخص زنده نیست')
                        elif not user_id:
                            update.message.reply_text('کاربری برای ثبت یافت  نشد با دستور /sv @username امتحان کنید')
                            return None
                        else:
                            vote = None
                    else:
                        vote = None
                    if vote:
                        set_vote_db(update.message.chat_id, vote)
                        update.message.reply_text('رای ثبت شد!')
                    elif not vote:
                        update.message.reply_text(
                            "برای ثبت رای باید بعد از دستور شخص مورد نظر رو بگی مانند زیر:\n /sv @username")
                except:
                    update.message.reply_text(
                        '"برای ثبت رای باید بعد از دستور شخص مورد نظر رو بگی مانند زیر:\n /sv @username')
            # elif update.message.reply_to_message.text.find('رای کیه ؟') != -1:
        #     allow_users = []
        #     for ent in ents:
        #         if ent['type'] == 'text_mention':
        #             allow_users.append(ent['user'].__dict__['id'])
        #     if update.message.from_user['id'] in allow_users:
        #         set_vote_db(update.message.chat_id, update.message.text.replace('\n', ' '))
        #         update.message.reply_text('رای ثبت شد!')


logger = logging.getLogger(__name__)


@run_async
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def generate_setting_buttons(rules, chat_id):
    if rules:
        save_your_role = rules['saveyourrole']
        if save_your_role:
            save_your_role_title = "فعال✅"
        elif not save_your_role:
            save_your_role_title = "غیر فعال❌"
        save_role = rules['saverole']
        if save_role:
            save_role_title = "فعال✅"
        elif not save_role:
            save_role_title = "غیر فعال❌"
        shekar = rules['shekar']
        if shekar:
            shekar_title = "فعال✅"
        elif not shekar:
            shekar_title = "غیر فعال❌"
        cult_role = rules['cult_option']
        if cult_role:
            cult_title = 'فعال✅'
        else:
            cult_title = 'غیر فعال❌'
        list_type = get_list_type(chat_id)
        if list_type == 1:
            list_type_title = 'پیشرفته'
            new_list_type = 0
        elif list_type == 0:
            list_type_title = 'ساده'
            new_list_type = 1
        buttons = [
            [InlineKeyboardButton(f"{shekar_title}",
                                  callback_data=f'setting_set_shekar_{chat_id}_{not shekar}'),
             InlineKeyboardButton("شکارچی💂‍♂️",
                                  callback_data=f'setting_info_shekar')],
            [InlineKeyboardButton(f"{save_your_role_title}",
                                  callback_data=f'setting_set_saveyourrole_{chat_id}_{not save_your_role}'),
             InlineKeyboardButton("🔥/saveYourRole",
                                  callback_data=f'setting_info_saveyourrole')],
            [InlineKeyboardButton(f"{save_role_title}",
                                  callback_data=f'setting_set_saverole_{chat_id}_{not save_role}'),
             InlineKeyboardButton("ثبت نقش🙂",
                                  callback_data=f'setting_info_saverole')
             ],
            [InlineKeyboardButton(f"{list_type_title}",
                                  callback_data=f'setting_set_listtype_{chat_id}_{new_list_type}'),
             InlineKeyboardButton("نوع لیست 📋",
                                  callback_data=f'setting_info_listtype')
             ],
            [InlineKeyboardButton(f'{cult_title}',
                                  callback_data=f'setting_set_cult_{chat_id}_{not cult_role}'),
             InlineKeyboardButton(" لیست انتظار فرقه👤",
                                  callback_data=f'setting_info_cult')
             ],
            [InlineKeyboardButton(f"🔷 ѕυp cнαɴɴel 🔸",
                                  url='https://t.me/lupine_guys')]
            , [InlineKeyboardButton(f"بستن منو",
                                    callback_data='setting_close')]
        ]
        return buttons


@check_channel_join
@run_async
def setting(update, context):
    chat_id = update.message.chat_id
    t = bot.get_chat_member(chat_id, update.message.from_user.id)
    if t.status == 'creator' or t.status == 'administrator' or update.message.from_user.id in get_admins_id():
        rules = get_group_rules(chat_id)
        if not rules:
            buttons = [[InlineKeyboardButton("ثبت گروه", callback_data=f'setting_setup_{chat_id}')]]
            context.bot.send_message(
                chat_id,
                """گروه شما هنوز در سیستم ربات ثبت نشده است😶
    جهت ثبت گروه خود از دکمه زیر استفاده نمایید👇""",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            context.bot.send_message(
                chat_id,
                '''به پنل مدیریتی ربات خوش آمدید👋
                روی دکمه های ردیف سمت راست کلیک کنید تا کاربرد هر دکمه را مشاهده نمایید😉''',
                reply_markup=InlineKeyboardMarkup(generate_setting_buttons(rules, chat_id))
            )


@run_async
def setting_buttons(update, context):
    query = update.callback_query
    chat_id = query.message.chat.id
    user = query.from_user.id
    t = bot.get_chat_member(chat_id, user)
    if t.status == 'creator' or t.status == 'administrator' or user in get_admins_id():
        data = query.data
        data = data.replace('setting_', '')
        if data.find('setup') == 0:
            rules = get_group_rules(chat_id)
            if not rules:
                buttons = [[InlineKeyboardButton(text="درحال ثبت گروه ...", callback_data='nothing')]]
                setup(chat_id)
            else:
                buttons = [[InlineKeyboardButton(text="انگار گروه قبلا ثبت شده بود!", callback_data='nothing')]]
            query.edit_message_text('''گروه شما هنوز در سیستم ربات ثبت نشده است😶
جهت ثبت گروه خود از دکمه زیر استفاده نمایید👇''',
                                    reply_markup=InlineKeyboardMarkup(buttons))
            time.sleep(5)
            rules = get_group_rules(chat_id)
            query.edit_message_text(
                '''به پنل مدیریتی ربات خوش آمدید👋
                روی دکمه های ردیف سمت راست کلیک کنید تا کاربرد هر دکمه را مشاهده نمایید😉''',
                reply_markup=InlineKeyboardMarkup(generate_setting_buttons(rules, chat_id))
            )
        elif data.find('info') == 0:
            data = data.replace('info_', '')
            if data == 'saveyourrole':
                info = "امکان پرسیدن نقش بازیکنان توسط ربات🤖"
            elif data == 'saverole':
                info = "امکان ثبت نقش برای کاربران🙂"
            elif data == 'shekar':
                info = "امکان تعیین شکارچی بازی توسط ادمین💂‍♂️✨"
            elif data == 'listtype':
                info = 'نوع لیست نقش ها📋'
            elif data == 'cult':
                info = 'لیست انتظار فرقه👤'
            query.answer(text=info, show_alert=True)

        elif data.find('set') == 0:
            data = data.replace('set_', '')
            data = data.split('_')
            subject = data[0]
            group_id = data[1]
            cmd = data[2]
            if subject == 'saveyourrole':
                set_saveYourRole(group_id, cmd)
            elif subject == 'saverole':
                set_saveRole(group_id, cmd)
            elif subject == 'shekar':
                set_shekar(group_id, cmd)
            elif subject == 'listtype':
                set_list_type(group_id, cmd)
            elif subject == 'cult':
                set_cult_option(group_id, cmd)
            rules = get_group_rules(chat_id)
            query.edit_message_text(
                '''به پنل مدیریتی ربات خوش آمدید👋
                روی دکمه های ردیف سمت راست کلیک کنید تا کاربرد هر دکمه را مشاهده نمایید😉''',
                reply_markup=InlineKeyboardMarkup(generate_setting_buttons(rules, chat_id))
            )

        elif data.find('close') == 0:
            rules = get_group_rules(chat_id)
            save_your_role = rules['saveyourrole']
            if save_your_role:
                save_your_role_title = "فعال✅"
            elif not save_your_role:
                save_your_role_title = "غیر فعال❌"
            save_role = rules['saverole']
            if save_role:
                save_role_title = "فعال✅"
            elif not save_role:
                save_role_title = "غیر فعال❌"
            shekar = rules['shekar']
            if shekar:
                shekar_title = "فعال✅"
            elif not shekar:
                shekar_title = "غیر فعال❌"
            cult_role = rules['cult_option']
            if cult_role:
                cult_title = 'فعال✅'
            else:
                cult_title = 'غیر فعال❌'
            list_type = get_list_type(chat_id)
            if list_type == 1:
                list_type_title = 'پیشرفته'
            elif list_type == 0:
                list_type_title = 'ساده'
            buttons = [
                [InlineKeyboardButton(f"🔷 ѕυp cнαɴɴel 🔸", url='https://t.me/lupine_guys')]
            ]
            query.edit_message_text(
                '''
‏شکارچی💂‍♂️ : {}
‏saveYourRole🔥 : {}
‏ثبت نقش🙂 : {}
نوع لیست📋: {}
لیست انتظار فرقه👤: {}
    '''.format(shekar_title, save_your_role_title, save_role_title, list_type_title, cult_title),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    else:
        query.answer('این پنل فقط مخصوص مدیران گروه است')


@check_channel_join
@run_async
def helper_setting(update, context):
    chat_id = update.message.chat_id
    t = bot.get_chat_member(chat_id, update.message.from_user.id)
    if t.status == 'creator' or t.status == 'administrator' or update.message.from_user.id in get_admins_id():
        settings = get_group_setting(chat_id)
        if not settings:
            buttons = [[InlineKeyboardButton("ثبت گروه", callback_data=f'setting_setup_{chat_id}')]]
            context.bot.send_message(
                chat_id,
                """گروه شما در هلپر ثبت نشده است""",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        if settings:

            if settings['jointime_pin']:
                join_time = "Active ✅"
                join_time_order = 0
            else:
                join_time = "Inactive ❌"
                join_time_order = 1
            if settings['game_started_pin']:
                next_game = "Active ✅"
                next_game_order = 0
            else:
                next_game = "Inactive ❌"
                next_game_order = 1

            if settings['is_confirm_tsww_enable']:
                tsww = "Active ✅"
                tsww_order = False
            else:
                tsww = "Inactive ❌"
                tsww_order = True
            if settings['is_confirm_score_enable']:
                ss = "Active ✅"
                ss_order = 0
            else:
                ss = "Inactive ❌"
                ss_order = 1
            if settings['is_startnewgame_enable']:
                sn = "Active ✅"
                sn_order = False
            else:
                sn = "Inactive ❌"
                sn_order = True
            if settings['start_mode'] == 1:
                sg = "/startChaos"
                sg_order = 2
            elif settings['start_mode'] == 2:
                sg = "/startGame"
                sg_order = 0
            else:
                sg = "بازی استارت نمیشود"
                sg_order = 1
            if settings['role_saver'] == 1:
                rs = "Role saver"
                rs_order = 2
            elif settings['role_saver'] == 2:
                rs = "TSWW"
                rs_order = 0
            else:
                rs = "بدون ثبت نقش"
                rs_order = 1

            buttons = [
                [InlineKeyboardButton(join_time,
                                      callback_data=f'helperSetting_set_joinTime_{chat_id}_{join_time_order}'),
                 InlineKeyboardButton("پین #players",
                                      callback_data=f'helperSetting_info_joinTime')],
                [InlineKeyboardButton(next_game,
                                      callback_data=f'helperSetting_set_nextGame_{chat_id}_{next_game_order}'),
                 InlineKeyboardButton("پین #next",
                                      callback_data=f'helperSetting_info_nextGame')],
                [InlineKeyboardButton(tsww,
                                      callback_data=f'helperSetting_set_tsww_{chat_id}_{tsww_order}'),
                 InlineKeyboardButton("ثبت امتیاز TSWW",
                                      callback_data=f'helperSetting_info_tsww')
                 ],
                [InlineKeyboardButton(ss,
                                      callback_data=f'helperSetting_set_fillIt_{chat_id}_{ss_order}'),
                 InlineKeyboardButton("ثبت /Fillit",
                                      callback_data=f'helperSetting_info_fillIt')
                 ],
                [InlineKeyboardButton(rs,
                                      callback_data=f'helperSetting_set_roleSaver_{chat_id}_{rs_order}'),
                 InlineKeyboardButton("ثبت نقش",
                                      callback_data=f'helperSetting_info_roleSaver')
                 ],
                [InlineKeyboardButton(sn,
                                      callback_data=f'helperSetting_set_startNewGame_{chat_id}_{sn_order}'),
                 InlineKeyboardButton("استارت بازی جدید",
                                      callback_data=f'helperSetting_info_startNewGame')
                 ],
                [InlineKeyboardButton(sg,
                                      callback_data=f'helperSetting_set_startMode_{chat_id}_{sg_order}'),
                 InlineKeyboardButton("نوع استارت بازی",
                                      callback_data=f'helperSetting_info_startMode')
                 ], [InlineKeyboardButton(f"🔷 ѕυp cнαɴɴel 🔸",
                                          url='https://t.me/lupine_guys')]
                , [InlineKeyboardButton(f"بستن منو",
                                        callback_data='helperSetting_close')]
            ]
            context.bot.send_message(
                chat_id,
                '''به پنل مدیریتی ربات خوش آمدید👋
                روی دکمه های ردیف سمت راست کلیک کنید تا کاربرد هر دکمه را مشاهده نمایید😉''',
                reply_markup=InlineKeyboardMarkup(buttons)
            )


@check_channel_join
@run_async
def black_helper_setting(update, context):
    chat_id = update.message.chat_id
    t = bot.get_chat_member(chat_id, update.message.from_user.id)
    if t.status == 'creator' or t.status == 'administrator' or update.message.from_user.id in get_admins_id():
        settings = black_get_group_setting(chat_id)
        if not settings:
            buttons = [[InlineKeyboardButton("ثبت گروه", callback_data=f'setting_setup_{chat_id}')]]
            context.bot.send_message(
                chat_id,
                """گروه شما در هلپر بلک ثبت نشده است"""
            )
        if settings:

            if settings['jointime_pin']:
                join_time = "Active ✅"
                join_time_order = 0
            else:
                join_time = "Inactive ❌"
                join_time_order = 1
            if settings['game_started_pin']:
                next_game = "Active ✅"
                next_game_order = 0
            else:
                next_game = "Inactive ❌"
                next_game_order = 1
            #
            # if settings['is_confirm_tsww_enable']:
            #     tsww = "Active ✅"
            #     tsww_order = False
            # else:
            #     tsww = "Inactive ❌"
            #     tsww_order = True
            # if settings['is_confirm_score_enable']:
            #     ss = "Active ✅"
            #     ss_order = 0
            # else:
            #     ss = "Inactive ❌"
            #     ss_order = 1
            if settings['is_startnewgame_enable']:
                sn = "Active ✅"
                sn_order = False
            else:
                sn = "Inactive ❌"
                sn_order = True
            if settings['role_saver'] == 1:
                rs = "Role saver"
                rs_order = 2
            elif settings['role_saver'] == 2:
                rs = "TSWW"
                rs_order = 0
            else:
                rs = "بدون ثبت نقش"
                rs_order = 1
            if settings['start_mode'] == 1:
                sg = "/startChaos"
                sg_order = 2
            elif settings['start_mode'] == 2:
                sg = "/startGame"
                sg_order = 3
            elif settings['start_mode'] == 3:
                sg = '/startfoolish'
                sg_order = 4
            elif settings['start_mode'] == 4:
                sg = '/sartmighty'
                sg_order = 5
            elif settings['start_mode'] == 5:
                sg = '/startclassic'
                sg_order = 6
            elif settings['start_mode'] == 6:
                sg = '/startromance'
                sg_order = 7
            else:
                sg = "بازی استارت نمیشود"
                sg_order = 1

            buttons = [
                [InlineKeyboardButton(join_time,
                                      callback_data=f'helperSettingB_set_joinTime_{chat_id}_{join_time_order}'),
                 InlineKeyboardButton("پین #players",
                                      callback_data=f'helperSettingB_info_joinTime')],
                [InlineKeyboardButton(next_game,
                                      callback_data=f'helperSettingB_set_nextGame_{chat_id}_{next_game_order}'),
                 InlineKeyboardButton("پین #next",
                                      callback_data=f'helperSettingB_info_nextGame')],
                # [InlineKeyboardButton(tsww,
                #                       callback_data=f'helperSetting_set_tsww_{chat_id}_{tsww_order}'),
                #  InlineKeyboardButton("ثبت امتیاز TSWW",
                #                       callback_data=f'helperSetting_info_tsww')
                #  ],
                # [InlineKeyboardButton(ss,
                #                       callback_data=f'helperSetting_set_fillIt_{chat_id}_{ss_order}'),
                #  InlineKeyboardButton("ثبت /Fillit",
                #                       callback_data=f'helperSetting_info_fillIt')
                #  ],
                [InlineKeyboardButton(rs,
                                      callback_data=f'helperSettingB_set_roleSaver_{chat_id}_{rs_order}'),
                 InlineKeyboardButton("ثبت نقش",
                                      callback_data=f'helperSettingB_info_roleSaver')
                 ],
                [InlineKeyboardButton(sn,
                                      callback_data=f'helperSettingB_set_startNewGame_{chat_id}_{sn_order}'),
                 InlineKeyboardButton("استارت بازی جدید",
                                      callback_data=f'helperSettingB_info_startNewGame')
                 ],
                [InlineKeyboardButton(sg,
                                      callback_data=f'helperSettingB_set_startMode_{chat_id}_{sg_order}'),
                 InlineKeyboardButton("نوع استارت بازی",
                                      callback_data=f'helperSettingB_info_startMode')
                 ], [InlineKeyboardButton(f"🔷 ѕυp cнαɴɴel 🔸",
                                          url='https://t.me/lupine_guys')]
                , [InlineKeyboardButton(f"بستن منو",
                                        callback_data='helperSettingB_close')]
            ]
            context.bot.send_message(
                chat_id,
                '''به پنل مدیریتی هلپر بلک ورولف خوش آمدید👋
                روی دکمه های ردیف سمت راست کلیک کنید تا کاربرد هر دکمه را مشاهده نمایید😉''',
                reply_markup=InlineKeyboardMarkup(buttons)
            )


@run_async
def helper_setting_buttons(update, context):
    query = update.callback_query
    chat_id = query.message.chat.id
    user = query.from_user.id
    t = bot.get_chat_member(chat_id, user)
    if t.status == 'creator' or t.status == 'administrator' or user in get_admins_id():
        # print(update)
        data = query.data
        data = data.replace('helperSetting_', '')
        if data.find('info') == 0:
            data = data.replace('info_', '')
            if data == 'joinTime':
                info = 'با فعال کردن این گزینه لیست پلیرهای بازی در گروه پین📌میشود.'
            elif data == 'nextGame':
                info = 'این گزینه پیام اطلاع از شروع بازی بعدی را در گروه پین📌 میکند.'
            elif data == 'tsww':
                info = 'بعد از پایان هربازی امتیازهای کسب شده توسط بازیکنان را ثبت میکند.'
            elif data == 'fillIt':
                info = 'اگر شما بازی جدیدی را در گروه خود شروع کرده باشید، با فعال کردن این گزینه پیام شروع بازی در چنل اطلاع رسانی ثبت میشود و دیگران را مطلع میکند'
            elif data == 'roleSaver':
                info = 'با گزینه ی ثبت نقش میتوانید انتخاب کنید که نقش بازیکنان در طول بازی با کدام ربات ثبت، و نمایش داده شود'
            elif data == 'startNewGame':
                info = 'این گزینه یک بازی جدید را در گروه شروع میکند.'
            elif data == 'startMode':
                info = 'شما میتوانید حالت دلخواه خود را برای بازی انتخاب کنید. برای مثال بازی ساده باشد یا حالت آشوب داشته باشد.'

            query.answer(text=info, show_alert=True)

        elif data.find('set') == 0:
            data = data.replace('set_', '')
            data = data.split('_')
            subject = data[0]
            group_id = data[1]
            cmd = data[2]
            if subject == 'joinTime':
                set_pin_players(group_id, cmd)
            elif subject == 'nextGame':
                set_next_pin(group_id, cmd)
            elif subject == 'tsww':
                set_tsww(group_id, cmd)
            elif subject == 'fillIt':
                set_fillIt(group_id, cmd)
            elif subject == 'startNewGame':
                set_startNewGame(group_id, cmd)
            elif subject == 'startMode':
                set_startmode(group_id, cmd)
            elif subject == 'roleSaver':
                set_roleSaver(group_id, cmd)
            settings = get_group_setting(chat_id)
            if settings['jointime_pin']:
                join_time = "Active ✅"
                join_time_order = 0
            else:
                join_time = "Inactive ❌"
                join_time_order = 1
            if settings['game_started_pin']:
                next_game = "Active ✅"
                next_game_order = 0
            else:
                next_game = "Inactive ❌"
                next_game_order = 1

            if settings['is_confirm_tsww_enable']:
                tsww = "Active ✅"
                tsww_order = False
            else:
                tsww = "Inactive ❌"
                tsww_order = True
            if settings['is_confirm_score_enable']:
                ss = "Active ✅"
                ss_order = 0
            else:
                ss = "Inactive ❌"
                ss_order = 1
            if settings['is_startnewgame_enable']:
                sn = "Active ✅"
                sn_order = False
            else:
                sn = "Inactive ❌"
                sn_order = True
            if settings['role_saver'] == 1:
                rs = "Role saver"
                rs_order = 2
            elif settings['role_saver'] == 2:
                rs = "TSWW"
                rs_order = 0
            else:
                rs = "بدون ثبت نقش"
                rs_order = 1
            if settings['start_mode'] == 1:
                sg = "/startChaos"
                sg_order = 2
            elif settings['start_mode'] == 2:
                sg = "/startGame"
                sg_order = 0
            else:
                sg = "بازی استارت نمیشود"
                sg_order = 1

            buttons = [
                [InlineKeyboardButton(join_time,
                                      callback_data=f'helperSetting_set_joinTime_{chat_id}_{join_time_order}'),
                 InlineKeyboardButton("پین #players",
                                      callback_data=f'helperSetting_info_joinTime')],
                [InlineKeyboardButton(next_game,
                                      callback_data=f'helperSetting_set_nextGame_{chat_id}_{next_game_order}'),
                 InlineKeyboardButton("پین #next",
                                      callback_data=f'helperSetting_info_nextGame')],
                [InlineKeyboardButton(tsww,
                                      callback_data=f'helperSetting_set_tsww_{chat_id}_{tsww_order}'),
                 InlineKeyboardButton("ثبت امتیاز TSWW",
                                      callback_data=f'helperSetting_info_tsww')
                 ],
                [InlineKeyboardButton(ss,
                                      callback_data=f'helperSetting_set_fillIt_{chat_id}_{ss_order}'),
                 InlineKeyboardButton("ثبت /Fillit",
                                      callback_data=f'helperSetting_info_fillIt')
                 ],
                [InlineKeyboardButton(rs,
                                      callback_data=f'helperSetting_set_roleSaver_{chat_id}_{rs_order}'),
                 InlineKeyboardButton("ثبت نقش",
                                      callback_data=f'helperSetting_info_roleSaver')
                 ],
                [InlineKeyboardButton(sn,
                                      callback_data=f'helperSetting_set_startNewGame_{chat_id}_{sn_order}'),
                 InlineKeyboardButton("استارت بازی جدید",
                                      callback_data=f'helperSetting_info_startNewGame')
                 ],
                [InlineKeyboardButton(sg,
                                      callback_data=f'helperSetting_set_startMode_{chat_id}_{sg_order}'),
                 InlineKeyboardButton("نوع استارت بازی",
                                      callback_data=f'helperSetting_info_startMode')
                 ], [InlineKeyboardButton(f"🔷 ѕυp cнαɴɴel 🔸",
                                          url='https://t.me/lupine_guys')]
                , [InlineKeyboardButton(f"بستن منو",
                                        callback_data='helperSetting_close')]
            ]
            query.edit_message_text(
                '''به پنل مدیریتی هلپر بلک ورولف خوش آمدید👋
                روی دکمه های ردیف سمت راست کلیک کنید تا کاربرد هر دکمه را مشاهده نمایید😉''',
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        elif data.find('close') == 0:

            buttons = [
                [InlineKeyboardButton(f"🔷 ѕυp cнαɴɴel 🔸", url='https://t.me/lupine_guys')]
            ]
            query.edit_message_text(
                '''تنظیمات ثبت شد''',
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    else:
        query.answer('این پنل فقط مخصوص مدیران گروه است')


@run_async
def black_helper_setting_buttons(update, context):
    query = update.callback_query
    chat_id = query.message.chat.id
    user = query.from_user.id
    t = bot.get_chat_member(chat_id, user)
    if t.status == 'creator' or t.status == 'administrator' or user in get_admins_id():
        # print(update)
        data = query.data
        data = data.replace('helperSettingB_', '')
        if data.find('info') == 0:
            data = data.replace('info_', '')
            if data == 'joinTime':
                info = 'با فعال کردن این گزینه لیست پلیرهای بازی در گروه پین📌میشود.'
            elif data == 'nextGame':
                info = 'این گزینه پیام اطلاع از شروع بازی بعدی را در گروه پین📌 میکند.'
            elif data == 'tsww':
                info = 'بعد از پایان هربازی امتیازهای کسب شده توسط بازیکنان را ثبت میکند.'
            elif data == 'fillIt':
                info = 'اگر شما بازی جدیدی را در گروه خود شروع کرده باشید، با فعال کردن این گزینه پیام شروع بازی در چنل اطلاع رسانی ثبت میشود و دیگران را مطلع میکند'
            elif data == 'roleSaver':
                info = 'با گزینه ی ثبت نقش میتوانید انتخاب کنید که نقش بازیکنان در طول بازی با کدام ربات ثبت، و نمایش داده شود'
            elif data == 'startNewGame':
                info = 'این گزینه یک بازی جدید را در گروه شروع میکند.'
            elif data == 'startMode':
                info = 'شما میتوانید حالت دلخواه خود را برای بازی انتخاب کنید. برای مثال بازی ساده باشد یا حالت آشوب داشته باشد.'

            query.answer(text=info, show_alert=True)

        elif data.find('set') == 0:
            data = data.replace('set_', '')
            data = data.split('_')
            subject = data[0]
            group_id = data[1]
            cmd = data[2]
            if subject == 'joinTime':
                black_set_pin_players(group_id, cmd)
            elif subject == 'nextGame':
                black_set_next_pin(group_id, cmd)
            # elif subject == 'tsww':
            #     black_set_tsww(group_id, cmd)
            # elif subject == 'fillIt':
            #     black_set_fillIt(group_id, cmd)
            elif subject == 'startNewGame':
                black_set_startNewGame(group_id, cmd)
            elif subject == 'startMode':
                black_set_startmode(group_id, cmd)
            elif subject == 'roleSaver':
                black_set_roleSaver(group_id, cmd)
            settings = black_get_group_setting(chat_id)
            if settings['jointime_pin']:
                join_time = "Active ✅"
                join_time_order = 0
            else:
                join_time = "Inactive ❌"
                join_time_order = 1
            if settings['game_started_pin']:
                next_game = "Active ✅"
                next_game_order = 0
            else:
                next_game = "Inactive ❌"
                next_game_order = 1
            #
            # if settings['is_confirm_tsww_enable']:
            #     tsww = "Active ✅"
            #     tsww_order = False
            # else:
            #     tsww = "Inactive ❌"
            #     tsww_order = True
            # if settings['is_fillit_enable']:
            #     ss = "Active ✅"
            #     ss_order = 0
            # else:
            #     ss = "Inactive ❌"
            #     ss_order = 1
            if settings['is_startnewgame_enable']:
                sn = "Active ✅"
                sn_order = False
            else:
                sn = "Inactive ❌"
                sn_order = True
            if settings['role_saver'] == 1:
                rs = "Role saver"
                rs_order = 2
            elif settings['role_saver'] == 2:
                rs = "TSWW"
                rs_order = 0
            else:
                rs = "بدون ثبت نقش"
                rs_order = 1
            if settings['start_mode'] == 1:
                sg = "/startChaos"
                sg_order = 2
            elif settings['start_mode'] == 2:
                sg = "/startGame"
                sg_order = 3
            elif settings['start_mode'] == 3:
                sg = '/startfoolish'
                sg_order = 4
            elif settings['start_mode'] == 4:
                sg = '/sartmighty'
                sg_order = 5
            elif settings['start_mode'] == 5:
                sg = '/startclassic'
                sg_order = 6
            elif settings['start_mode'] == 6:
                sg = '/startromance'
                sg_order = 7
            else:
                sg = "بازی استارت نمیشود"
                sg_order = 1

            buttons = [
                [InlineKeyboardButton(join_time,
                                      callback_data=f'helperSettingB_set_joinTime_{chat_id}_{join_time_order}'),
                 InlineKeyboardButton("پین #players",
                                      callback_data=f'helperSettingB_info_joinTime')],
                [InlineKeyboardButton(next_game,
                                      callback_data=f'helperSettingB_set_nextGame_{chat_id}_{next_game_order}'),
                 InlineKeyboardButton("پین #next",
                                      callback_data=f'helperSettingB_info_nextGame')],
                # [InlineKeyboardButton(tsww,
                #                       callback_data=f'helperSetting_set_tsww_{chat_id}_{tsww_order}'),
                #  InlineKeyboardButton("ثبت امتیاز TSWW",
                #                       callback_data=f'helperSetting_info_tsww')
                #  ],
                # [InlineKeyboardButton(ss,
                #                       callback_data=f'helperSetting_set_fillIt_{chat_id}_{ss_order}'),
                #  InlineKeyboardButton("ثبت /Fillit",
                #                       callback_data=f'helperSetting_info_fillIt')
                #  ],
                [InlineKeyboardButton(rs,
                                      callback_data=f'helperSettingB_set_roleSaver_{chat_id}_{rs_order}'),
                 InlineKeyboardButton("ثبت نقش",
                                      callback_data=f'helperSettingB_info_roleSaver')
                 ],
                [InlineKeyboardButton(sn,
                                      callback_data=f'helperSettingB_set_startNewGame_{chat_id}_{sn_order}'),
                 InlineKeyboardButton("استارت بازی جدید",
                                      callback_data=f'helperSettingB_info_startNewGame')
                 ],
                [InlineKeyboardButton(sg,
                                      callback_data=f'helperSettingB_set_startMode_{chat_id}_{sg_order}'),
                 InlineKeyboardButton("نوع استارت بازی",
                                      callback_data=f'helperSettingB_info_startMode')
                 ], [InlineKeyboardButton(f"🔷 ѕυp cнαɴɴel 🔸",
                                          url='https://t.me/lupine_guys')]
                , [InlineKeyboardButton(f"بستن منو",
                                        callback_data='helperSettingB_close')]
            ]
            query.edit_message_text(
                '''به پنل مدیریتی ربات خوش آمدید👋
                روی دکمه های ردیف سمت راست کلیک کنید تا کاربرد هر دکمه را مشاهده نمایید😉''',
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        elif data.find('close') == 0:

            buttons = [
                [InlineKeyboardButton(f"🔷 ѕυp cнαɴɴel 🔸", url='https://t.me/lupine_guys')]
            ]
            query.edit_message_text(
                '''تنظیمات ثبت شد''',
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    else:
        query.answer('این پنل فقط مخصوص مدیران گروه است')


def start(update, context):
    texts = update.chat_lang
    if context.args:
        data = context.args[0].split('___')
        if data:
            if data[0] == 'giftEmoji':
                emoji_gift_start(update, context)
                return
    update.message.reply_text(texts.start)


def forcedisable(update, context):
    group_id = update.message.chat.id
    user = update.message.from_user.id
    t = bot.get_chat_member(group_id, user)
    settings = get_group_setting(group_id)
    if settings:
        if t.status == 'creator' or t.status == 'administrator' or user in get_admins_id():
            set_pin_players(group_id, 0)
            set_next_pin(group_id, 0)
            set_fillIt(group_id, 0)
            set_tsww(group_id, False)
            set_startNewGame(group_id, False)
            set_startmode(group_id, 0)
            set_roleSaver(group_id, 0)
            update.message.reply_text("تمام تنظیمات هلپر در حالت فعال قرار گرفت بررسی با : /helper_setting")


@check_channel_join
@check_player_ban
@run_async
def my_afks(update, context):
    user_id = update.message.from_user.id
    texts = update.user_lang.Myafk
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
    afks = get_user_afks(user_id, days)
    text = texts.header.format(mention_markdown(user_id, 'شما'), days)
    afk_count = 0
    for gap, afk in afks.items():
        text += f'\n‎{gap} - {afk}'
        afk_count += afk
    if afk_count > 5:
        text += '\n\nDon\'t ruin the games...'
    else:
        text = texts.no_afk.format(days)
    if update.effective_chat.id == user_id:
        update.message.reply_text(text, parse_mode='markdown', disable_web_page_preview=True)
    else:
        try:
            context.bot.send_message(user_id, text, parse_mode='markdown', disable_web_page_preview=True)
            update.message.reply_text('Pv check', parse_mode='markdown', disable_web_page_preview=True)
        except:
            update.message.reply_text(update.user_lang.Mypanel.start_pv, parse_mode='markdown',
                                      disable_web_page_preview=True)
    BotStats.myafks += 1


def getlink(update, context):
    if context.args:
        chat_id = context.args[0]
        try:
            chat = bot.get_chat(chat_id)
        except:
            update.message.reply_text(f'نیسم توش', parse_mode='markdown')
        link = chat.invite_link
        if link:
            update.message.reply_text(f'[{chat.title}]({link})', parse_mode='markdown')
        else:
            try:
                link = bot.export_chat_invite_link(chat_id)
                update.message.reply_text(f'[{chat.title}]({link})', parse_mode='markdown')
            except:
                update.message.reply_text(f'نمیش', parse_mode='markdown')


def setlink(update, context):
    if context.args:
        chat_id = context.args[0]
        try:
            chat = bot.get_chat(chat_id)
        except:
            update.message.reply_text(f'نیسم توش', parse_mode='markdown')
        link = chat.invite_link
        if link:
            update_gp_url(int(chat_id), link)
            update.message.reply_text(f'[{chat.title}]({link}) link has been saved in database', parse_mode='markdown')
        else:
            try:
                link = bot.export_chat_invite_link(chat_id)
                update_gp_url(int(chat_id), link)
                update.message.reply_text(f'[{chat.title}]({link}) link has been saved in database',
                                          parse_mode='markdown')
            except:
                update.message.reply_text(f'نمیش', parse_mode='markdown')


def check_helper(update, context):
    if context.args:
        chat_id = context.args[0]
        try:
            chat = bot.get_chat(int(chat_id))
        except:
            update.message.reply_text('I\'m not There')
            return
        res = ''
        for helper in get_helpers_id():
            try:
                h = bot.get_chat_member(int(chat_id), helper)
                if h.status != 'left':
                    res += f'\nFound {mention_markdown(helper, h.user.full_name)} With {h.status} status in {chat.title if not chat.invite_link else f"[{chat.title}]({chat.invite_link})"}'
            except:
                pass
        if not res:
            res = 'There are no Helpers There'
        update.message.reply_text(res, parse_mode='markdown')


def rs_stats(update, context):
    text = """
Data since {date}
➸ Roles Set (/sn): {roles_set}
➸ Lists Updated (/up): {lists_updated}
➸ Lists Requested (/li): {lists_requested}
➸ Shekars Set (/shekar): {shekars_set}
➸ Votes Saved (/sv): {votes_saved}
➸ Votes Said (/vt): {votes_said}
➸ Votes Equaled (/ev): {equal_votes}
➸ Gap State (/gpstate): {gpstate}
➸ My Afks (/myafks): {myafks}
➸ Emoji Panel (/mypanel): {panel_emoji}
➸ Most Roles (/mostroles): {most_roles}
➸ Most Roles Detailed (/most_roles_detailed): {most_roles_detailed}
➸ Most Votes (/votes): {most_votes}
➸ Most Roles Pv (/mostroles): {most_roles_pv}
➸ Sc (/sc): {sc}
➸ Rc (/rc): {rc}
➸ Cult up (/cultup): {cultup}
➸ My Afks (/myafks): {myafks}
➸ Langs set (/set_lang): {set_lang}
    """

    attrs = {a: getattr(BotStats, a) for a in dir(BotStats) if not a.startswith('__')}
    update.message.reply_text(text.format(**attrs))


def rs_stats_reset(update, context):
    rs_stats(update, context)
    BotStats.date = datetime.now(timezone('Asia/Tehran')).strftime('%Y-%m-%d %H:%M:%S')
    [setattr(BotStats, a, 0) for a in dir(BotStats) if not a.startswith('__') and a != 'date']
    update.message.reply_text('حل')


def setlang(update, context):
    buttons = [
        [InlineKeyboardButton('فارسی🇮🇷', callback_data='setlang fa'),
         InlineKeyboardButton('فارسی بی ادبی🔞🇮🇷', callback_data='setlang fb')],
        [InlineKeyboardButton('English🇺🇸', callback_data='setlang en')]
    ]
    txt = """زبان مورد نظر خود را انتخاب کنید🇮🇷🇺🇸
Select Your Language🇮🇷🇺🇸"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if chat_id == user_id or (
            context.bot.get_chat_member(chat_id, user_id).status != 'member' or user_id in get_admins_id()):
        update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(buttons))


def setlang_buttons(update, context):
    lang = update.callback_query.data.split()[1]
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    msg = update.effective_message
    if chat_id == user_id:
        change_chat_lang(user_id, lang)
        texts = update.user_lang.SetLang
        msg.edit_text(texts.lang_set)
    else:
        if context.bot.get_chat_member(chat_id, user_id).status != 'member' or user_id in get_admins_id():
            change_chat_lang(chat_id, lang)
            texts = update.chat_lang.SetLang
            msg.edit_text(texts.lang_set)
            BotStats.set_lang += 1
        else:
            texts = update.user_lang.SetLang
            update.callback_query.answer(texts.not_admin)


def biadabs(update, context):
    update.message.reply_text('\n'.join(get_bi_adab_chats()), parse_mode='markdown', disable_web_page_preview=True)


def get_data(update, context):
    update.message.reply_text('games' + ','.join(get_game_bots_id()))


def main():
    dp.add_handler(CommandHandler('start', start, filters=Filters.private))
    dp.add_handler(CommandHandler('sn', set_rule, filters=Filters.group))
    dp.add_handler(CommandHandler('up', update_list, filters=Filters.group))
    dp.add_handler(CommandHandler('li', role_list, filters=Filters.group))
    dp.add_handler(CommandHandler('dl', delete_role, filters=Filters.group))
    dp.add_handler(CommandHandler('shekar', set_shekarchi, filters=Filters.group))
    dp.add_handler(CommandHandler('sv', set_vote, filters=Filters.group))
    dp.add_handler(CommandHandler('vt', say_vote, filters=Filters.group))
    dp.add_handler(CommandHandler('ev', vote_equal, filters=Filters.group))
    dp.add_handler(CommandHandler('block', ban, filters=Filters.group & Filters.reply))
    dp.add_handler(CommandHandler('unblock', unban, filters=Filters.group & Filters.reply))
    dp.add_handler(CommandHandler('mystate', my_state))
    # dp.add_handler(CommandHandler('lupine', botstats))
    dp.add_handler(CommandHandler('gpstate', group_state, filters=Filters.group))
    dp.add_handler(CommandHandler('saveyourrole', save_your_role, filters=Filters.group))
    dp.add_handler(CommandHandler('setting', setting, filters=Filters.group))
    dp.add_handler(CommandHandler('helper_setting', helper_setting, filters=Filters.group))
    dp.add_handler(CommandHandler('black_helper_setting', black_helper_setting, filters=Filters.group))
    dp.add_handler(CommandHandler('bests', bests_list, filters=Filters.chat([-1001476763360, -1001444185267])))
    dp.add_handler(CommandHandler('checklist', check_list, filters=Filters.chat([-1001476763360, -1001444185267])))
    dp.add_handler(CommandHandler('scoreon', onscore, filters=Filters.user([674759339, 951153044])))
    dp.add_handler(CommandHandler('scoreoff', offscore, filters=Filters.user([674759339, 951153044])))
    dp.add_handler(CommandHandler('mypanel', panel_emoji))
    dp.add_handler(CommandHandler(('most_roles', 'mostroles'), most_roles))
    dp.add_handler(
        CommandHandler(('most_roles_detailed', 'mostrolesdetailed'), most_roles_detailed, filters=Filters.group))
    dp.add_handler(CommandHandler('votes', most_votes))
    dp.add_handler(CommandHandler('setlang', setlang))
    dp.add_handler(CommandHandler('myafks', my_afks))
    dp.add_handler(CommandHandler('set_next', set_next, filters=Filters.group))
    dp.add_handler(CommandHandler('forcedisable', forcedisable, filters=Filters.group))
    dp.add_handler(CommandHandler(('rs_stats', 'rsstats'), rs_stats, filters=Filters.chat(lab)))
    dp.add_handler(CommandHandler('rsstats_reset', rs_stats_reset, filters=Filters.chat(lab)))
    dp.add_handler(CommandHandler('getlink', getlink, filters=Filters.chat(lab)))
    dp.add_handler(CommandHandler('setlink', setlink, filters=Filters.chat(lab)))
    dp.add_handler(CommandHandler('check_helper', check_helper, filters=Filters.chat(lab)))
    dp.add_handler(CommandHandler('biadabs', biadabs, filters=Filters.chat(lab)))
    dp.add_handler(CommandHandler('lists', get_data))
    dp.add_handler(MessageHandler(Filters.reply & ~Filters.update.edited_message, save_role_reply))
    dp.add_handler(CallbackQueryHandler(setting_buttons, pattern=r'^setting'))
    dp.add_handler(CallbackQueryHandler(helper_setting_buttons, pattern=r'^helperSetting_'))
    dp.add_handler(CallbackQueryHandler(panel_emoji_c, pattern=r'^e-panel '))
    dp.add_handler(CallbackQueryHandler(black_helper_setting_buttons, pattern=r'^helperSettingB_'))
    dp.add_handler(CallbackQueryHandler(most_roles_buttons, pattern=r'^most_roles'))
    dp.add_handler(CallbackQueryHandler(setlang_buttons, pattern=r'^setlang'))
    dp.add_handler(InlineQueryHandler(inline_handler.inline_handler))
    dp.add_error_handler(error)
