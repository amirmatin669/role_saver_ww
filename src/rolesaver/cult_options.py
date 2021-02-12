import json
from datetime import datetime
from .db_cmd import *
from pytz import timezone
from telegram.ext import CommandHandler, run_async
from telegram.utils import helpers

from . import updater, get_cur, BotStats

bot = updater.bot
dp = updater.dispatcher
iran = timezone('Asia/Tehran')


def now():
    sa_time = datetime.now(iran)
    return sa_time.strftime('%Y-%m-%d %H:%M:%S')


def save_json_to_db(dict_obj):
    conn, cur = get_cur()
    cur.execute("""
    insert into v2.cult_option_(update_at, data) values (%s,%s)
    """, (now(), json.dumps(dict_obj)))
    conn.commit()


def load_json_from_db():
    conn, cur = get_cur()
    cur.execute("""
select data
from v2.cult_option_
order by update_at desc
limit 1;
    """)
    res = cur.fetchone()
    if res:
        return res[0]
    return res


info = load_json_from_db()
if not info:
    info = {}


@run_async
def savecult(update, context):
    global info
    chat_id = update.message.chat.id
    msg_id = update.message.message_id
    user_id = update.message.from_user.id
    allow_users = get_allow_players(chat_id)
    status = get_player_status(chat_id, user_id)
    rules = get_group_rules(chat_id)
    cult_option = rules['cult_option']
    if cult_option:
        all_players = get_all_players(chat_id)
        if not status and user_id in allow_users:
            try:
                bot.delete_message(chat_id, msg_id)
            except Exception as e:
                print(e)
            if chat_id not in info:
                info[chat_id] = []
            user_id = update.message.from_user.id
            if user_id not in info[chat_id]:
                info[chat_id].append(user_id)
            save_json_to_db(info)
            BotStats.sc += 1
        if not status and user_id not in allow_users and user_id in all_players:
            update.message.reply_text("چک کن ببین انگار مردی")
        if not status and user_id not in allow_users and user_id not in all_players:
            update.message.reply_text("تو بازی نیستی که")
    else:
        update.message.reply_text(" اینجا نمیتونی از این دستور استفاده کنی")


@run_async
def up_job(context):
    chat_id = context.job.context[0]
    cult_list_id = context.job.context[1]
    context.bot.delete_message(chat_id, cult_list_id)


@run_async
def no_cult(context):
    chat_id = context.job.context[0]
    uncult_list_id = context.job.context[1]
    context.bot.delete_message(chat_id, uncult_list_id)


@run_async
def up(update, context):
    global gp, info
    chat_id = update.message.chat.id
    try:
        cults = info[chat_id]
    except KeyError:
        bot.sendMessage(chat_id, "مثل این که کسی اینجا نمیخواد فرقه شه!")
    msg_id = update.message.message_id
    user_id = update.message.from_user.id
    try:
        bot.delete_message(chat_id, msg_id)
    except Exception as e:
        print(e)
    allow_users = get_allow_players(chat_id)
    first_text = 'لیست کسایی که میخوان فرقه بشن\n'
    rules = get_group_rules(chat_id)
    cult_option = rules['cult_option']
    status = get_player_status(chat_id, user_id)
    if not status:
        if cult_option:
            if cults != []:
                for i in cults:
                    if i in allow_users:
                        cult_info = bot.get_chat(i)
                        cult_name = cult_info.first_name
                        cult_mention = helpers.mention_html(i, cult_name)
                        first_text += f"↬ {cult_mention}\n"
                    else:
                        update.message.reply_text("چک کن ببین انگار مردی")
                cult_list = bot.sendMessage(chat_id,
                                            f"{first_text}\nبرای خارج شدن از این لیست میتونید از دستور /rc استفاده کنید\n<b>『سنگی نیس که خورد نشه،طلسمی نیس که نشکونم』</b>"
                                            , parse_mode='HTML')
                cult_id = cult_list.message_id
                BotStats.cultup += 1
            else:
                uncult_list = bot.sendMessage(chat_id, 'مثل این که کسی اینجا نمیخواد فرقه شه!')
                uncult_id = uncult_list.message_id
        else:
            update.message.reply_text("امکان استفاده از این دستور اینجا وجود نداره")
        try:
            context.job_queue.run_once(up_job, 10, context=[update.message.chat_id, cult_id])
        except:
            context.job_queue.run_once(up_cult, 2, context=[update.message.chat_id, uncult_id])


@run_async
def dl(update, context):
    global info
    chat_id = update.message.chat.id
    msg_id = update.message.message_id
    tarsu_id = update.message.from_user.id
    try:
        bot.delete_message(chat_id, msg_id)
    except Exception as e:
        print(e)
    gap_ferghes = info[chat_id]
    if tarsu_id in gap_ferghes:
        gap_ferghes.remove(tarsu_id)
        save_json_to_db(info)
        BotStats.rc += 1


dp.add_handler(CommandHandler('sc', savecult))
dp.add_handler(CommandHandler('cultup', up))
dp.add_handler(CommandHandler('rc', dl))
