import logging
import re
import time
from datetime import datetime

import psycopg2 as psycopg2
from pytz import timezone
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram.ext.dispatcher import run_async

from telegram.utils.helpers import mention_html as mention
import html

import db_cmd
import RANK_STATEMENT as RANK
from Panel_Emoji import panel_emoji, panel_emoji_c

admins = [340724963, 674759339, 638994540, 951153044]

iran = timezone('Asia/Tehran')


def now():
    sa_time = datetime.now(iran)
    return sa_time.strftime('%Y-%m-%d %H:%M:%S')


@run_async
def addusers(users):
    allusers = db_cmd.get_all_users_with_username()
    for user in users:
        if user.id not in allusers:
            db_cmd.add_user(user.id, user.username)
        elif user.id in allusers:
            if user.username != allusers[user.id]:
                db_cmd.update_user(user.id, user.username)


@run_async
def set_rule(update, context):
    # print('sn')
    user_id = update.message.from_user['id']
    chat_id = update.message.chat_id
    status = db_cmd.get_player_status(chat_id, user_id)
    allow_users = db_cmd.get_allow_players(update.message.chat_id)
    # print(status)

    if status:
        pass
    elif status and user_id in allow_users:
        update.message.reply_text('از یه ادمین بخواه تا رفع مسدودیتت بکنه')
    if not status:
        rules = db_cmd.get_group_rules(chat_id)
        if rules:
            if not rules['saverole']:
                update.message.reply_text('امکان استفاده از این دستور غیر فعال است')
                return
        if not update.message.__dict__['reply_to_message']:
            # context.bot.send_message(chat_id , " ", reply_to_message_id=)
            all_players = db_cmd.get_all_players(update.message.chat_id)
            if all_players:
                if user_id in allow_users:
                    # print(update.message.entities[0])
                    # print(update.message.entities[0]['length'])
                    length = update.message.entities[0]['length']
                    text = update.message.text
                    role = text[int(length):len(text)]
                    # print(role)
                    if not role:
                        update.message.reply_text('فوت نکن')
                    if role:
                        user = {
                            'id': user_id,
                            'role': role.replace('\n', ' '),
                            # 'username': update.message.from_user.username
                        }
                        db_cmd.add_rule(update.message.chat_id, user)
                        update.message.reply_text('نقشت ثبت شد')
                elif user_id not in allow_users and user_id in all_players:
                    update.message.reply_text('چک کن ببین انگار مردی')
                elif user_id not in allow_users:
                    update.message.reply_text('تو بازی نیستی ک')

            if not all_players:
                update.message.reply_text('بازی ای در جریان نیست\n یدونه شروع کن')


@run_async
def set_shekarchi(update, context):
    user = update.message.from_user
    chat_id = update.message.chat_id
    user_id = update.message.from_user['id']
    status = db_cmd.get_player_status(chat_id, user_id)
    if status:
        pass
    if not status:
        rules = db_cmd.get_group_rules(chat_id)
        if rules:
            if not rules['shekar']:
                update.message.reply_text('امکان استفاده از این دستور غیر فعال است')
                return
        t = bot.get_chat_member(chat_id=chat_id, user_id=int(user.id))
        if t.status == 'creator' or t.status == 'administrator' or update.message.from_user.id in admins:
            if update.message.reply_to_message:
                rep_user = update.message.reply_to_message.from_user
                db_cmd.set_shekarchi_db(chat_id, rep_user.id)
                t = bot.get_chat_member(chat_id=chat_id, user_id=int(rep_user.id)).user
                context.bot.send_message(chat_id,
                                         # f'[{t.name.replace("]","").replace("[","")}](tg://user?id={rep_user.id}) شکارچی بازی شد ',
                                         '{} شکارچی بازی شد '.format(mention(rep_user.id, t.name)),
                                         parse_mode='HTML')
            elif not update.message.reply_to_message:
                update.message.reply_text("روی شکارچی این دستور رو باید بزنید")

        else:
            update.message.reply_text('تنها مدیران میتوانند از این دستور استفاده کنن')


@run_async
def set_nazer(update, context):
    user = update.message.from_user
    chat_id = update.message.chat_id
    t = bot.get_chat_member(chat_id=chat_id, user_id=int(user.id))
    if t.status == 'creator' or t.status == 'administrator' or update.message.from_user.id in admins:
        if update.message.reply_to_message:
            rep_user = update.message.reply_to_message.from_user
            db_cmd.set_nazer_db(chat_id, rep_user.id)
        elif not update.message.reply_to_message:
            update.message.reply_text("روی ناظر این دستور رو باید بزنید")

    else:
        update.message.reply_text('تنها مدیران میتوانند از این دستور استفاده کنن')


@run_async
def set_vote(update, context):
    chat_id = update.message.chat_id
    user_id = update.message.from_user['id']
    status = db_cmd.get_player_status(chat_id, user_id)
    if status:
        pass
    if not status:
        user = update.message.from_user
        chat_id = update.message.chat_id
        shekarchi = db_cmd.get_shekarchi_db(chat_id)
        rules = db_cmd.get_group_rules(chat_id)
        if rules:
            if not rules['shekar']:
                update.message.reply_text('امکان استفاده از این دستور غیر فعال است')
                return
        if shekarchi:
            if user.id == shekarchi:
                length = update.message.entities[0]['length']
                text = update.message.text
                try:
                    # print(update.message)
                    # print(update.message.entities[1].user)
                    allow_users = db_cmd.get_allow_players(chat_id)
                    if update.message.entities[1].user:
                        user_id = update.message.entities[1].user.id
                        if user_id in allow_users:
                            vote = user_id
                        else:
                            update.message.reply_text('این شخص زنده نیست')
                            return None
                    elif update.message.entities[1].type == 'mention':
                        start = update.message.entities[1].offset
                        length = update.message.entities[1].length
                        username = text[int(start) + 1:int(start) + int(length)]
                        user_id = db_cmd.get_user_id_from_username(username)
                        if user_id:
                            if user_id in allow_users:
                                vote = user_id
                            else:
                                update.message.reply_text('این شخص زنده نیست')
                                return None
                        else:
                            vote = None
                    else:
                        vote = None
                except:
                    update.message.reply_text(
                        'برای ثبت رای باید بعد از دستور شخص مورد نظر رو بگی مانند زیر:\n /sv @username')
                # vote = text[int(length):len(text)].replace('\n', ' ')
                if vote:
                    db_cmd.set_vote_db(chat_id, vote)
                    update.message.reply_text('رای ثبت شد!')
                elif not vote:
                    update.message.reply_text(
                        "برای ثبت رای باید بعد از دستور شخص مورد نظر رو بگی مانند زیر:\n /sv @username")
            elif user.id != shekarchi:
                update.message.reply_text('تنها شکارچی میتواند رای ثبت کند')
        elif not shekarchi:
            update.message.reply_text('شکارچی ای یافت نشد')


from telegram.utils.helpers import mention_markdown, escape_markdown


@run_async
def say_vote(update, context):
    chat_id = update.message.chat_id
    vote = db_cmd.get_vote_db(chat_id)
    user_id = update.message.from_user['id']
    status = db_cmd.get_player_status(chat_id, user_id)
    if status:
        pass
    if not status:
        rules = db_cmd.get_group_rules(chat_id)
        if rules:
            if not rules['shekar']:
                update.message.reply_text('امکان استفاده از این دستور غیر فعال است')
                return
        shekar = db_cmd.get_shekarchi_db(chat_id)
        if shekar in db_cmd.get_allow_players(chat_id):
            allow_users = db_cmd.get_allow_players(chat_id)
            if vote:
                if int(vote) in allow_users:
                    t = bot.get_chat_member(chat_id=chat_id, user_id=int(vote)).user
                    msg = f"""
رای {mention_markdown(int(vote), escape_markdown(t.name))}        

        
        
مخالف رای شکار نباشه
                """
                    context.bot.send_message(chat_id, msg, parse_mode='Markdown')
                    time.sleep(2)
                    context.bot.send_message(chat_id, msg, parse_mode='Markdown')
                    time.sleep(3)
                    context.bot.send_message(chat_id, msg, parse_mode='Markdown')
                # elif int(vote) in allow_users:

            elif not vote or int(vote) not in allow_users:
                if shekar:
                    update.message.reply_text('رایی ثبت نشده')
                    t = bot.get_chat_member(chat_id=chat_id, user_id=int(shekar)).user
                    context.bot.send_message(
                        chat_id,
                        # f"""[{t.first_name.replace("]","").replace("[","")}](tg://user?id={shekar}) رای کیه ؟""",
                        """{} رای کیه ؟""".format(mention_markdown(int(vote), escape_markdown(t.first_name))),
                        parse_mode='Markdown'
                    )
                if not shekar:
                    update.message.reply_text('شکارچی ای برای بازی ثبت نشده است')
        else:
            update.message.reply_text('شکار متاسفانه مرده')


game_finish = r'طول مدت بازی|مدت زمان بازی|مدت بازی|مدت بُکُن بُکُن'
game_list = r'بازیکن های زنده|فراموشکارای زنده|هنرمندای فعال|دانشجوهای مشغول به تحصیل|مسافرای زنده ی توی قطار|بازیکنان زنده|بازیکن های آنلاین|کونده های زنده |بازیکنان درحال بازی|برره ای های زنده|مسافر های زنده:|کشتی گیران سالم|هیولاهای زنده|بازمانده ها'
death = r'مرده|اخراج شده|کنار رفته|آفلاین|تبعید شده|بگا رفته|خارج شده|سقَط شده|فرار کرده|اخراج شده|نفله وشده'


@run_async
def update_list(update, context):
    print('up')
    user_id = update.message.from_user['id']
    chat_id = update.message.chat_id
    status = db_cmd.get_player_status(chat_id, user_id)
    print(chat_id, status, update.message.chat.title)
    if status:
        pass
    if not status:
        if update.message.reply_to_message \
                and update.message.reply_to_message.from_user.id in [175844556, 198626752, 951153044, 618096097,
                                                                     1029642148]:
            if update.message.reply_to_message.message_id not in db_cmd.get_used_message(chat_id):
                message_date = update.message.reply_to_message.date
                text = update.message.reply_to_message.text
                ents = update.message.reply_to_message['entities']
                import datetime as dt
                dd = message_date + dt.timedelta(hours=3.5) - dt.timedelta(minutes=2.5)
                ld = db_cmd.get_last_game_time(chat_id)
                tsda = ld >= dd
                if re.search(game_finish, text):
                    db_cmd.delete_game(update.message.chat_id,
                                       update.message.reply_to_message.message_id)
                    context.bot.send_message(chat_id, 'بازی خوبی بود')
                #     todo congratulations to winners
                elif re.search(death, text):
                    allow_users = []
                    for ent in ents:
                        if ent['type'] == 'text_mention':
                            allow_users.append(ent['user'].id)
                    players_data = {
                        'players': allow_users
                    }
                    db_cmd.update_game_db(update.message.chat_id, players_data,
                                          update.message.reply_to_message.message_id)
                    db_cmd.save_mention_usable(chat_id)
                    # if chat_id == -1001476763360:
                    #     context.bot.send_message(chat_id, 'sina لیست را اپدیت کرد')
                    if chat_id == -1001414470547:
                        context.bot.send_message(chat_id, '-Lιѕт Uρɗαтєɗ Ɓу -Nιмα ☻')
                    elif chat_id == -1001423339319:
                        context.bot.send_message(chat_id, 'Janan  لیست را اپدیت کرد')
                    elif chat_id == -1001482994041:
                        context.bot.send_message(chat_id, '-ɴαєιм°🕸 updated list')
                    elif chat_id == -1001128468995:
                        context.bot.send_message(chat_id, 'ʟɪsᴛ ᴜᴘᴅᴀᴛᴇᴅ ʙʏ 𝑵𝒆𝒈𝒂𝒉𐂊')
                    elif chat_id == -1001259701545:
                        context.bot.send_message(chat_id, 'ʟɪsᴛ ᴜᴘᴅᴀᴛᴇᴅ ʙʏ _Aмeeɴ⃤')
                    elif chat_id == -1001410480062:
                        context.bot.send_message(chat_id,
                                                 '𝐋𝐢𝐬𝐭 𝐔𝐩𝐝𝐚𝐭𝐞𝐝 𝐁𝐲:\n★ • Mєhrαn .• | ¤ 🇮🇱 ¤ | •.')
                    else:
                        context.bot.send_message(chat_id, 'لیست اپدیت شد')

                    players = db_cmd.get_role_list(chat_id)
                    msg = "لیست نقش های ثبت شده \n\n"
                    allow_players = db_cmd.get_allow_players(chat_id)
                    shekar = db_cmd.get_shekarchi_db(chat_id)
                    if shekar in allow_players:
                        t = bot.get_chat_member(chat_id=chat_id, user_id=int(shekar))
                        msg += "`شکارچی` : {}\n".format(mention(shekar, html.escape(t.user.first_name)))
                    for player in players:
                        if player not in allow_players:
                            continue
                        if player == shekar:
                            continue
                        t = bot.get_chat_member(chat_id=chat_id, user_id=int(player))
                        name = t.user.full_name
                        msg += f'{name} : {players[player]}\n'
                    if not players:
                        msg = "هیشکی نقششو ثبت نکرده 😐 \n"
                        rules = db_cmd.get_group_rules(chat_id)
                        if rules:
                            t = rules['saveyourrole']
                            if t:
                                msg += 'با /saveYourRole ازشون ک نقششونو بپرسید'
                            elif rules['saverole']:
                                msg += 'با /sn نقش خودتونو ثبت کنید'
                            else:
                                msg = ""
                                return
                        else:
                            msg += 'با /saveYourRole ازشون ک نقششونو بپرسید'
                    context.bot.send_message(chat_id, msg,
                                             parse_mode='HTML')

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
                    db_cmd.delete_game(update.message.chat_id,
                                       update.message.__dict__['reply_to_message']['message_id'])
                    db_cmd.add_game(update.message.chat_id, players_data,
                                    update.message.__dict__['reply_to_message']['message_id'])
                    rules = db_cmd.get_group_rules(chat_id)
                    messge = f'با {len(allow_users)} بازیکن بازی شروع شد\n'
                    if rules:
                        t = rules['saveyourrole']
                        if t:
                            messge += ' برای اینکه نقش اون هارو بخاهید از دستور /saveYourRole استفاده کنید'
                        elif rules['saverole']:
                            messge += 'با /sn نقش خودتونو ثبت کنید'
                        else:
                            pass
                    else:
                        messge += ' برای اینکه نقش اون هارو بخاهید از دستور /saveYourRole استفاده کنید'
                    buttons = [
                        [InlineKeyboardButton(f"Ads by lupine♨️", url='https://t.me/Ads_by_lupine/9')]
                    ]
                    context.bot.send_message(chat_id, messge,
                                             reply_markup=InlineKeyboardMarkup(buttons)
                                             )
                    addusers(users)
                else:
                    pass
            else:
                update.message.reply_text('این لیست قبلا ثبت شده است')


@run_async
def ban(update, context):
    t = bot.get_chat_member(chat_id=update.message.chat_id, user_id=int(update.message.from_user['id']))
    if t.status == 'creator' or t.status == 'administrator' or update.message.from_user.id in admins:
        status = db_cmd.get_player_status(update.message.chat_id, update.message.reply_to_message.from_user['id'])
        if status:
            update.message.reply_text('این یتیم و قبلا یکی دیگه بنش کرده ولش کن')
            pass
        if not status:
            db_cmd.ban_user(update.message.chat_id, update.message.reply_to_message.from_user, update.message.from_user)
            update.message.reply_text('با موفقیت مسدود شد\n دیگه نمیتونه توی این گروه از هیچ دستوری استفاده کنه')
    else:
        update.message.reply_text('برو به ادمینت بگو بیاد')


@run_async
def unban(update, context):
    status = db_cmd.get_player_status(update.message.chat_id, update.message.reply_to_message.from_user['id'])
    t = bot.get_chat_member(chat_id=update.message.chat_id, user_id=int(update.message.from_user['id']))
    if t.status == 'creator' or t.status == 'administrator' or update.message.from_user.id in admins:
        if status:
            db_cmd.unban_user(update.message.chat_id, update.message.reply_to_message.from_user,
                              update.message.from_user)
            update.message.reply_text('از مسدودیت بیرون اومد')

        if not status:
            update.message.reply_text('بچه خوبیه مسدود نیسش')
    else:
        update.message.reply_text('من فقط به یه ادمین راجب این موضوع جواب میدم')


@run_async
def delete_role(update, context):
    user_id = update.message.from_user['id']
    chat_id = update.message.chat_id
    t = bot.get_chat_member(chat_id=update.message.chat_id, user_id=int(update.message.from_user['id']))
    if t.status == 'creator' or t.status == 'administrator' or update.message.from_user.id in admins:
        db_cmd.delete_rule(chat_id, update.message.reply_to_message.from_user)
        update.message.reply_text('باش')


@run_async
def my_state(update, context):
    user_id = update.message.from_user['id']
    user = update.message.from_user
    chat_id = update.message.chat_id
    status = db_cmd.get_player_status(chat_id, user_id)
    if status:
        pass
    if not status:

        info = db_cmd.get_player_info(chat_id, user_id)
        if chat_id == user_id:
            gp = 'Private'
        else:
            gp = mention(update.message.chat_id, update.message.chat['title'])
        # if info:

        if info:
            message = '''
‏┓ <b>نام</b>
┃‏{name}
‏┫  <b>نوع کاربر</b> <a href="https://t.me/lupine_guys/32">❓</a>
┃‏<code>{type}</code>
‏┫  <b>تعداد کل نقش های ثبت کرده</b>
┃‏<code>{set}</code>
‏┫ <b>تعداد نقش های ثبت کرده در این گروه</b>
┃‏<code>{gp_set}</code>
‏┫ <b>تعداد گروه هایی که توشون نقش ثبت کرده</b>
┃‏<code>{gp_set_count}</code>
┛‏
    ‏made in group {gp}
                '''.format(name=mention(update.message.from_user['id'], update.message.from_user['first_name']),
                           type=RANK.UserStatus(user).status,
                           set=info['role_count'],
                           gp_set=info['group_role'],
                           gp_set_count=info['group_count'],
                           gp=gp)
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
        if not info:
            update.message.reply_text('به نظر میرسه تاحالا استفاده ای ازم نکردی 😐😂')


@run_async
def group_state(update, context):
    user_id = update.message.from_user['id']
    chat_id = update.message.chat_id
    status = db_cmd.get_player_status(chat_id, user_id)
    if status:
        pass
    if not status:
        info = db_cmd.get_group_info(chat_id)
        if info:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text='''
┏ ɢʀᴏᴜᴘ ɴᴀᴍᴇ 
┃‎ [{}](tg://user?id={})
┣ ᴄᴏᴜɴᴛ ᴏғ ɢᴀᴍᴇs
┃‎ `{}`
┣ ᴄᴏᴜɴᴛ ᴏғ ʀᴏʟᴇs 
┃‎ `{}`
┣ ᴄᴏᴜɴᴛ ᴏғ ᴘʟᴀʏᴇʀs
┃‎ `{}`
┗'''.format(update.message.chat['title'].replace("]", "").replace("[", ""),
            update.message.chat['id'], info['all_games_count'], info['role_count'],
            info['player_count']),
                parse_mode='Markdown'
            )
        if not info:
            update.message.reply_text(
                'به نظر میرسه تاحالا بازی ای رو با من ثبت نکردید\n با دستور /up میتونید بازی هاتونو ثبت کنید🙂')


@run_async
def save_your_role(update, context):
    user_id = update.message.from_user['id']
    chat_id = update.message.chat_id
    status = db_cmd.get_player_status(chat_id, user_id)
    if status:
        pass
    if not status:
        rules = db_cmd.get_group_rules(chat_id)
        if rules:
            t = rules['saveyourrole']
            if not t:
                update.message.reply_text('امکان استفاده از این دستور غیر فعال است')
                return
        if not db_cmd.get_mention_use(chat_id):
            db_cmd.save_mention_used(chat_id)
            in_game_users = db_cmd.get_allow_players(chat_id)
            all_users = db_cmd.get_all_players(chat_id)
            roleseted_players = db_cmd.get_all_roleseted_players(chat_id)
            users = []
            for user in all_users:
                if user in in_game_users:
                    if user not in roleseted_players:
                        users.append(user)

            for user in users:
                t = bot.get_chat_member(chat_id=chat_id, user_id=int(user))
                name = t.user.full_name
                context.bot.send_message(chat_id, text="""{} نقشت چیه ؟""".format(mention(user, html.escape(name))),
                                         parse_mode='HTML')
                time.sleep(1)
            msg = f'ببین نقش این {len(users)}‏ نفر چیه'
            if not users:
                msg = 'بچه های خوبی دارید همشون نقشاشونو ثبت کردن 😅'

            update.message.reply_text(msg)
        else:
            update.message.reply_text("شما تنها یک بار در هر روز میتوانید درخواست نقش کنید")


@run_async
def role_list(update, context):
    user_id = update.message.from_user['id']
    chat_id = update.message.chat_id
    status = db_cmd.get_player_status(chat_id, user_id)
    if status:
        pass
    if not status:
        players = db_cmd.get_role_list(chat_id)
        msg = "لیست نقش های ثبت شده \n\n"
        allow_players = db_cmd.get_allow_players(chat_id)
        shekar = db_cmd.get_shekarchi_db(chat_id)
        if shekar in allow_players:
            t = bot.get_chat_member(chat_id=chat_id, user_id=int(shekar))
            # msg += f"`شکارچی` : [{t.user.full_name.replace(']','').replace('[','')}](tg://user?id={shekar})\n"
            msg += "`شکارچی` : {}\n".format(mention(shekar, html.escape(t.user.first_name)))
        for player in players:
            if player not in allow_players:
                continue
            if player == shekar:
                continue
            t = bot.get_chat_member(chat_id=chat_id, user_id=int(player))
            name = t.user.full_name
            # msg += f'[{name.replace("]","").replace("[","")}](tg://user?id={player}) : {players[player]}\n'
            msg += f'{mention(player, html.escape(name))} : {players[player]}\n'
        if not players:
            msg = "هیشکی نقششو ثبت نکرده 😐 \n با /saveYourRole ازشون بخواه ک نقششونو ثبت بکنن"
        context.bot.send_message(chat_id, msg,
                                 parse_mode='HTML')


@run_async
def save_role_reply(update, context):
    # print(update)
    if update.message.reply_to_message.from_user['id'] in [861551208, 920042392]:
        ents = update.message.reply_to_message['entities']

        if update.message.reply_to_message.text.find('نقشت چیه ؟') != -1:
            allow_users = []
            for ent in ents:
                if ent['type'] == 'text_mention':
                    allow_users.append(ent['user'].__dict__['id'])
            if update.message.from_user['id'] in allow_users:
                user = {
                    'id': update.message.from_user['id'],
                    'role': update.message.text.replace('\n', ' ')
                    # ,
                    # 'username': update.message.from_user.username
                }

                db_cmd.add_rule(update.message.chat_id, user)
                update.message.reply_text('نقشت ثبت شد')
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
                    allow_users = db_cmd.get_allow_players(update.message.chat_id)
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
                        user_id = db_cmd.get_user_id_from_username(username)
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
                        db_cmd.set_vote_db(update.message.chat_id, vote)
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


@run_async
def setting(update, context):
    chat_id = update.message.chat_id
    t = bot.get_chat_member(chat_id, update.message.from_user.id)
    if t.status == 'creator' or t.status == 'administrator' or update.message.from_user.id in admins:
        rules = db_cmd.get_group_rules(chat_id)
        if not rules:
            buttons = [[InlineKeyboardButton("ثبت گروه", callback_data=f'setting_setup_{chat_id}')]]
            context.bot.send_message(
                chat_id,
                """گروه شما هنوز در سیستم ربات ثبت نشده است😶
    جهت ثبت گروه خود از دکمه زیر استفاده نمایید👇""",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
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
                 ], [InlineKeyboardButton(f"🔷 ѕυp cнαɴɴel 🔸",
                                          url='https://t.me/lupine_guys')]
                , [InlineKeyboardButton(f"بستن منو",
                                        callback_data='setting_close')]
            ]
            context.bot.send_message(
                chat_id,
                '''به پنل مدیریتی ربات خوش آمدید👋
                روی دکمه های ردیف سمت راست کلیک کنید تا کاربرد هر دکمه را مشاهده نمایید😉''',
                reply_markup=InlineKeyboardMarkup(buttons)
            )


@run_async
def setting_buttons(update, context):
    query = update.callback_query
    chat_id = query.message.chat.id
    user = query.from_user.id
    t = bot.get_chat_member(chat_id, user)
    if t.status == 'creator' or t.status == 'administrator' or user in admins:
        # print(update)
        data = query.data
        data = data.replace('setting_', '')
        if data.find('setup') == 0:
            rules = db_cmd.get_group_rules(chat_id)
            if not rules:
                buttons = [[InlineKeyboardButton(text="درحال ثبت گروه ...", callback_data='nothing')]]
                db_cmd.setup(chat_id)
            else:
                buttons = [[InlineKeyboardButton(text="انگار گروه قبلا ثبت شده بود!", callback_data='nothing')]]
            query.edit_message_text('''گروه شما هنوز در سیستم ربات ثبت نشده است😶
جهت ثبت گروه خود از دکمه زیر استفاده نمایید👇''',
                                    reply_markup=InlineKeyboardMarkup(buttons))
            time.sleep(5)

            rules = db_cmd.get_group_rules(chat_id)
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
                 ], [InlineKeyboardButton(f"🔷 ѕυp cнαɴɴel 🔸",
                                          url='https://t.me/lupine_guys')]
                , [InlineKeyboardButton(f"بستن منو",
                                        callback_data='setting_close')]
            ]
            query.edit_message_text(
                '''به پنل مدیریتی ربات خوش آمدید👋
                روی دکمه های ردیف سمت راست کلیک کنید تا کاربرد هر دکمه را مشاهده نمایید😉''',
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        elif data.find('info') == 0:
            data = data.replace('info_', '')
            if data == 'saveyourrole':
                info = "امکان پرسیدن نقش بازیکنان توسط ربات🤖"
            elif data == 'saverole':
                info = "امکان ثبت نقش برای کاربران🙂"
            elif data == 'shekar':
                info = "امکان تعیین شکارچی بازی توسط ادمین💂‍♂️✨"
            query.answer(text=info, show_alert=True)

        elif data.find('set') == 0:
            data = data.replace('set_', '')
            data = data.split('_')
            subject = data[0]
            group_id = data[1]
            cmd = data[2]
            if subject == 'saveyourrole':
                db_cmd.set_saveYourRole(group_id, cmd)
            elif subject == 'saverole':
                db_cmd.set_saveRole(group_id, cmd)
            elif subject == 'shekar':
                db_cmd.set_shekar(group_id, cmd)
            rules = db_cmd.get_group_rules(chat_id)
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
                 ], [InlineKeyboardButton(f"🔷 ѕυp cнαɴɴel 🔸",
                                          url='https://t.me/lupine_guys')]
                , [InlineKeyboardButton(f"بستن منو",
                                        callback_data='setting_close')]
            ]
            query.edit_message_text(
                '''به پنل مدیریتی ربات خوش آمدید👋
                روی دکمه های ردیف سمت راست کلیک کنید تا کاربرد هر دکمه را مشاهده نمایید😉''',
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        elif data.find('close') == 0:
            rules = db_cmd.get_group_rules(chat_id)
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
            buttons = [
                [InlineKeyboardButton(f"🔷 ѕυp cнαɴɴel 🔸", url='https://t.me/lupine_guys')]
            ]
            query.edit_message_text(
                '''
‏شکارچی💂‍♂️ : {}
‏saveYourRole🔥 : {}
‏ثبت نقش🙂 : {}

تنظیمات ثبت شد
    '''.format(shekar_title, save_your_role_title, save_role_title),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    else:
        query.answer('این پنل فقط مخصوص مدیران گروه است')


@run_async
def helper_setting(update, context):
    chat_id = update.message.chat_id
    t = bot.get_chat_member(chat_id, update.message.from_user.id)
    if t.status == 'creator' or t.status == 'administrator' or update.message.from_user.id in admins:
        settings = db_cmd.get_group_setting(chat_id)
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


@run_async
def black_helper_setting(update, context):
    chat_id = update.message.chat_id
    t = bot.get_chat_member(chat_id, update.message.from_user.id)
    if t.status == 'creator' or t.status == 'administrator' or update.message.from_user.id in admins:
        settings = db_cmd.black_get_group_setting(chat_id)
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
    if t.status == 'creator' or t.status == 'administrator' or user in admins:
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
                db_cmd.set_pin_players(group_id, cmd)
            elif subject == 'nextGame':
                db_cmd.set_next_pin(group_id, cmd)
            elif subject == 'tsww':
                db_cmd.set_tsww(group_id, cmd)
            elif subject == 'fillIt':
                db_cmd.set_fillIt(group_id, cmd)
            elif subject == 'startNewGame':
                db_cmd.set_startNewGame(group_id, cmd)
            elif subject == 'startMode':
                db_cmd.set_startmode(group_id, cmd)
            elif subject == 'roleSaver':
                db_cmd.set_roleSaver(group_id, cmd)
            settings = db_cmd.get_group_setting(chat_id)
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
    if t.status == 'creator' or t.status == 'administrator' or user in admins:
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
                db_cmd.black_set_pin_players(group_id, cmd)
            elif subject == 'nextGame':
                db_cmd.black_set_next_pin(group_id, cmd)
            # elif subject == 'tsww':
            #     db_cmd.black_set_tsww(group_id, cmd)
            # elif subject == 'fillIt':
            #     db_cmd.black_set_fillIt(group_id, cmd)
            elif subject == 'startNewGame':
                db_cmd.black_set_startNewGame(group_id, cmd)
            elif subject == 'startMode':
                db_cmd.black_set_startmode(group_id, cmd)
            elif subject == 'roleSaver':
                db_cmd.black_set_roleSaver(group_id, cmd)
            settings = db_cmd.black_get_group_setting(chat_id)
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


import chern_list


def start(update, context):
    if context.args:
        data = context.args[0].split('_')
        if data[0] == 'chern-list':
            context.bot.send_message(update.message.chat_id, "درحال پردازش لطفا واسا ...    ")
            msg = chern_list.make_list(data[1])
            if not msg:
                msg = 'لیست خالی است'
            context.bot.send_message(update.message.chat_id, msg, parse_mode='HTML')
            return
    context.bot.send_message(update.message.chat_id, "salam mn to pv kry nmknm bra to")
    pass


def main():
    global conn
    conn = psycopg2.connect()
    global bot
    u = Updater()
    bot = u.bot
    dp = u.dispatcher

    dp.add_handler(CommandHandler('start', start, filters=Filters.private))
    dp.add_handler(CommandHandler('sn', set_rule, filters=Filters.group))
    dp.add_handler(CommandHandler('up', update_list, filters=Filters.group))
    dp.add_handler(CommandHandler('li', role_list, filters=Filters.group))
    dp.add_handler(CommandHandler('dl', delete_role, filters=Filters.group))
    dp.add_handler(CommandHandler('shekar', set_shekarchi, filters=Filters.group))
    dp.add_handler(CommandHandler('sv', set_vote, filters=Filters.group))
    dp.add_handler(CommandHandler('vt', say_vote, filters=Filters.group))
    dp.add_handler(CommandHandler('block', ban, filters=Filters.group))
    dp.add_handler(CommandHandler('unblock', unban, filters=Filters.group))
    dp.add_handler(CommandHandler('mystate', my_state))
    dp.add_handler(CommandHandler('gpstate', group_state, filters=Filters.group))
    dp.add_handler(CommandHandler('saveyourrole', save_your_role, filters=Filters.group))
    dp.add_handler(CommandHandler('setting', setting, filters=Filters.group))
    dp.add_handler(CommandHandler('helper_setting', helper_setting, filters=Filters.group))
    dp.add_handler(CommandHandler('black_helper_setting', black_helper_setting, filters=Filters.group))
    dp.add_handler(MessageHandler(Filters.reply, save_role_reply))
    dp.add_handler(CallbackQueryHandler(setting_buttons, pattern=r'^setting'))
    dp.add_handler(CallbackQueryHandler(helper_setting_buttons, pattern=r'^helperSetting_'))
    dp.add_handler(CallbackQueryHandler(black_helper_setting_buttons, pattern=r'^helperSettingB_'))
    dp.add_handler(CommandHandler('mypanel', panel_emoji))
    dp.add_handler(CallbackQueryHandler(panel_emoji_c, pattern=r'^pannel1$|^pannel2$|^pannel3$|'))
    dp.add_handler(
        CallbackQueryHandler(panel_emoji_c,
                             pattern=r'^1$|^2$|^3$|^4$|^5$|^6$|^7$|^8$|9$|^10$|^11$|^12$|^13$|^14$|^15$'))
    dp.add_handler(CallbackQueryHandler(panel_emoji_c, pattern='exitp'))
    dp.add_handler(CallbackQueryHandler(panel_emoji_c, pattern='returnp'))
    dp.add_error_handler(error)
    print(1)
    u.start_polling()
    u.idle()


if __name__ == '__main__':
    main()
