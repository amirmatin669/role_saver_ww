from os import getenv
from jdatetime import datetime
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from psycopg2._psycopg import cursor, connection
import psycopg2.extensions
# from pyrogram import Client
from telegram.ext import Updater, CommandHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from time import sleep
from pytz import timezone

update_game, start_game, finish_game, send_next = None, None, None, None

lab = -1001444185267

updater_token = getenv("DISPATCHER_TOKEN", '')
role_saver_token = getenv("ROLE_SAVER_TOKEN", '')

updater = Updater(token=updater_token, use_context=True, workers=55)  # test

# rs_bot = Client(':memory:', bot_token=role_saver_token,
#                 api_id=1038622,
#                 api_hash="87ca332fa9f9b84d89c28a02a2abd0dc"
#                 )

database = getenv("DATABASE_ARGS", '')
database_kw = {
    'host': database.split('%%')[0],
    'database': database.split('%%')[1],
    'user': database.split('%%')[2],
    'password': database.split('%%')[3]
}


def get_cur() -> (connection, cursor):
    if not hasattr(get_cur, 'conn') or get_cur.conn.closed != 0:
        get_cur.conn = psycopg2.connect(**database_kw)
    if get_cur.conn.status == psycopg2.extensions.STATUS_IN_TRANSACTION:
        get_cur.conn.rollback()
    cur: cursor = get_cur.conn.cursor()
    conn: connection = get_cur.conn
    return conn, cur


def check_channel_join(func):
    def check(user_id):
        try:
            return updater.bot.get_chat_member('@lupine_guys', user_id).status != 'left'
        except:
            return False

    markup = InlineKeyboardMarkup([[InlineKeyboardButton('Lupine Guys', url='t.me/lupine_guys')]])

    def wrapper(update, context):
        if not check(update.effective_user.id):
            txt = 'برای استفاده از این دستور باید در چنل [لوپین گایز](t.me/{}) عضو باشید'.format('lupine_guys')
            return update.message.reply_text(txt, parse_mode='markdown', disable_web_page_preview=True,
                                             reply_markup=markup)
        return func(update, context)

    return wrapper


class BotStats:
    date = datetime.now(timezone('Asia/Tehran')).strftime('%Y-%m-%d %H:%M:%S')
    roles_set = 0
    lists_updated = 0
    lists_requested = 0
    shekars_set = 0
    votes_saved = 0
    votes_said = 0
    equal_votes = 0
    my_state = 0
    gpstate = 0
    panel_emoji = 0
    most_roles = 0
    most_roles_detailed = 0
    most_votes = 0
    most_roles_pv = 0
    sc = 0
    rc = 0
    cultup = 0
    myafks = 0
    set_lang = 0


def start_game_req():
    print(request.date)
    try:
        j_req = request.get_json(force=True)
        # print(j_req)
    except Exception as e:
        res = {
            'error': 'cant parse your request as json',
            'message': e
        }
        return jsonify(res)
    if ('message_id' or 'text' or 'users' or 'chat_id') not in j_req:
        res = {
            'error': 'item missing',
            'message': ' check game_message_id, text, users, chat_id is exist'
        }
        return jsonify(res)
    game_message_id = j_req['message_id']
    text = j_req['text']
    users = j_req['users']
    chat_id = j_req['chat_id']
    start_game(chat_id, users, game_message_id, text)
    res = {
        'error': '',
        'message': 'done'
    }
    return jsonify(res)


def update_game_req():
    print(request.date)
    try:
        j_req = request.get_json(force=True)
        # print(j_req)
    except Exception as e:
        res = {
            'error': 'cant parse your request as json',
            'message': e
        }
        return jsonify(res)
    if ('message_id' or 'text' or 'users' or 'chat_id') not in j_req:
        res = {
            'error': 'item missing',
            'message': ' check game_message_id, text, users, chat_id is exist'
        }
        return jsonify(res)
    game_message_id = j_req['message_id']
    text = j_req['text']
    users = j_req['users']
    chat_id = j_req['chat_id']
    update_game(chat_id, users, game_message_id, text)
    res = {
        'error': '',
        'message': 'done'
    }
    return jsonify(res)


def finish_game_req():
    print(request.date)
    try:
        j_req = request.get_json(force=True)
        # print(j_req)
    except Exception as e:
        res = {
            'error': 'cant parse your request as json',
            'message': e
        }
        return jsonify(res)
    if ('message_id' or 'chat_id') not in j_req:
        res = {
            'error': 'item missing',
            'message': ' check game_message_id and chat_id exist'
        }
        return jsonify(res)
    game_message_id = j_req['message_id']
    chat_id = j_req['chat_id']
    finish_game(chat_id, game_message_id)
    res = {
        'error': '',
        'message': 'done'
    }
    return jsonify(res)


def game_started_pin():
    try:
        j_req = request.get_json(force=True)
    except Exception as e:
        res = {
            'error': 'cant parse your request as json',
            'message': e
        }
        return jsonify(res)
    if 'chat_id' not in j_req:
        res = {
            'error': 'item missing',
            'message': 'check if chat_id is exist'
        }
        return jsonify(res)
    if send_next(j_req['chat_id']):
        res = {
            'error': '',
            'message': 'done'
        }
        sleep(0.1)
    else:
        res = {
            'error': 'sending next not complete',
            'message': 'err'
        }
    return jsonify(res)


def app(web_app: Flask):
    global update_game, start_game, finish_game, send_next
    from .v3_4 import main, update_game, start_game, finish_game
    from .next_option import send_next
    from . import cult_options
    from .score_for_lupine import afk_request

    main()
    web_app.add_url_rule('/v1/uploadFirstList', 'start_game', start_game_req, methods=['POST'])
    web_app.add_url_rule('/v1/uploadGameList', 'update_game', update_game_req, methods=['POST'])
    web_app.add_url_rule('/v1/finishGame', 'finish_game', finish_game_req, methods=['POST'])
    web_app.add_url_rule('/v1/game_started_pin', 'game_started_pin', game_started_pin, methods=['POST'])
    web_app.add_url_rule('/lu/afkUser', 'lupine_afk_user', afk_request, methods=['POST'])
    # rs_bot.start()
    updater.start_polling(clean=True)
    print('Role Saver Is Up')
    # updater.idle()
    return web_app
