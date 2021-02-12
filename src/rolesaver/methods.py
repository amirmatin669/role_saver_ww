"""
update list methods
"""
import html
import random
from random import choice
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.utils.helpers import mention_html as mention

from . import updater
from .RANK_STATEMENT import UserStatus
from .cache import save_mention_usable, save_list_message_id_, get_list_message_id, get_cached_user
from .db_cmd import delete_game, update_game_db, get_list_type, get_allow_players, get_shekarchi_db, get_role_list, \
    add_rank
from .db_cmd import get_group_rules, get_all_players, add_game
from .v3_4 import update_roles_dict, addusers
from .wording import get_from_db
from .multilanger import return_lang

bot = updater.bot


# ranks = ['🧊']

def give_rank(user):
    if user.id == 120500168:
        return ['🌙']
    res = get_cached_user(user)
    if not res:
        return ['🧊']
    res: UserStatus
    return res.get_emojies_rank()


def make_user_role_list_v0(chat_id):
    players = get_role_list(chat_id)
    allow_players = get_allow_players(chat_id)
    shekar = get_shekarchi_db(chat_id)
    texts = return_lang(chat_id).List
    shekar_saved = False
    msg = get_from_db('role_list_header')[0]
    role_list_footer = get_from_db('role_list_footer')[0]
    role_list_user = get_from_db('role_list_user')[0]
    if shekar in allow_players:
        u = bot.get_chat_member(chat_id, int(shekar))
        name = u.user.full_name
        ranks = give_rank(u.user)
        shekar_saved = True
        msg += role_list_user.format(name=f'<b>{mention(u.user.id, name)}</b>', ranks='|'.join(ranks),
                                     role=choice(texts.ch)) + '\n\n'

    saved_role_users = []
    not_saved_role_users = []

    for player in players:
        if player not in allow_players or player == shekar:
            continue
        t = bot.get_chat_member(chat_id=chat_id, user_id=int(player))
        name = t.user.full_name
        role = html.escape(players[player])
        ranks = give_rank(t.user)
        saved_role_users.append(role_list_user.format(name=name, ranks='|'.join(ranks), role=': ' + role))

    for player in allow_players:
        if player == shekar or player in players:
            continue
        t = bot.get_chat_member(chat_id=chat_id, user_id=int(player))
        name = t.user.full_name
        ranks = give_rank(t.user)
        not_saved_role_users.append(role_list_user.format(name=mention(player, name), ranks='|'.join(ranks), role=''))

    msg += '\n'.join(saved_role_users) + role_list_footer
    if not saved_role_users and not shekar_saved:
        msg = texts.list_empty
    return msg


def make_user_role_list_v1(chat_id):
    from .v3_4 import roles_v2
    all_saved = []
    all_death = []
    all_unsaved = []
    delimiter = '\n\n〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n'
    texts = return_lang(chat_id).List
    saved_roles = get_role_list(chat_id)
    all_players = get_all_players(chat_id)
    alive_players = get_allow_players(chat_id)
    shekar = get_shekarchi_db(chat_id)
    role_list_user_rank_less = get_from_db('role_list_user_rank_less')[0]
    role_list_footer = get_from_db('role_list_footer')[0]
    role_list_user = get_from_db('role_list_user')[0]
    for user in all_players:
        if user not in list(saved_roles.keys()) and user in alive_players:
            if user == shekar:
                continue
            u = bot.get_chat_member(chat_id, user)
            name = u.user.full_name
            ranks = give_rank(u.user)
            all_unsaved.append(role_list_user.format(name=mention(u.user.id, name), ranks='|'.join(ranks), role=''))

    if shekar in alive_players:
        u = bot.get_chat_member(chat_id, shekar)
        name = u.user.full_name
        ranks = give_rank(u.user)
        all_saved.append(role_list_user.format(name=f'<b>{mention(u.user.id, name)}</b>', ranks='|'.join(ranks),
                                               role=choice(texts.ch)))

    for key, value in saved_roles.items():
        if key == shekar or key not in alive_players:
            continue
        user = bot.get_chat_member(chat_id, key)
        name = user.user.full_name
        ranks = give_rank(user.user)
        all_saved.append(role_list_user.format(name=f'<b>{html.escape(name)}</b>', ranks='|'.join(ranks),
                                               role=': ' + value))
        f'<b>{html.escape(name)}</b> : {html.escape(value)}'

    for key, value in roles_v2[chat_id].items():
        if value['role']:
            all_death.append(role_list_user_rank_less.format(name=f'<s>{html.escape(key)}</s>',
                                                             role=': ' + value['role']))
    args = []
    args.append((texts.dead_list if isinstance(texts.dead_list, str) else choice(texts.dead_list)) + '\n'.join(
        all_death)) if all_death else None
    args.append((texts.no_role if isinstance(texts.no_role, str) else choice(texts.no_role)) + '\n'.join(
        all_unsaved)) if all_unsaved else None
    args.append((texts.role_list if isinstance(texts.role_list, str) else choice(texts.role_list)) + '\n'.join(
        all_saved)) if all_saved else None
    msg = delimiter.join(args) + role_list_footer
    return msg


def finish_game(chat_id, game_message_id) -> str:
    delete_game(chat_id, game_message_id)
    texts = return_lang(chat_id).Up
    msg = texts.good_game
    bot.send_message(chat_id, msg)
    return msg


def update_game(chat_id, users, game_message_id, text):
    try:

        update_game_db(chat_id, users, game_message_id)
        save_mention_usable(chat_id)

        update_roles_dict(text, chat_id)
        list_type = get_list_type(chat_id)

        if list_type == 0:
            message = make_user_role_list_v0(chat_id)
            msg = bot.send_message(chat_id, message, parse_mode='HTML', disable_web_page_preview=True)
        elif list_type == 1:
            message = make_user_role_list_v1(chat_id)
            msg = bot.send_message(chat_id, message, parse_mode='HTML', disable_web_page_preview=True)
        else:
            msg = None
        if not msg:
            return False
        previous_message_id = get_list_message_id(chat_id)
        if previous_message_id:
            try:
                bot.delete_message(chat_id=chat_id, message_id=previous_message_id)
            except Exception as e:
                print('on deleting previous list on start game - ', e)

        save_list_message_id_(chat_id, msg.message_id)
    except Exception as e:
        print(e)
        return False


def start_game(chat_id, users, game_message_id, text):
    try:
        previous_message_id = get_list_message_id(chat_id)
        if previous_message_id:
            try:
                bot.delete_message(chat_id=chat_id, message_id=previous_message_id)
            except Exception as e:
                print('on deleting previous list on start game - ', e)

        delete_game(chat_id, game_message_id)

        if chat_id in [-1001444185267, -1001410741415, -1001476763360]:
            for i in users:
                add_rank(i, 3)

        if chat_id in [-1001328443567]:
            for i in users:
                add_rank(i, 54)
        add_game(chat_id, users, game_message_id)

        save_mention_usable(chat_id)
        update_roles_dict(text, chat_id)

        rules = get_group_rules(chat_id)
        list_type = get_list_type(chat_id)

        if list_type == 0:
            message = make_user_role_list_v0(chat_id)
        elif list_type == 1:
            message = make_user_role_list_v1(chat_id)
        else:
            return

        options = []
        if rules:
            # options.append(InlineKeyboardButton("/saveYourRole ✅" if rules['saveyourrole'] else '/saveYourRole ❌',
            #                                     url='https://t.me/lupine_guys/134'))
            options.append(InlineKeyboardButton("/sn ✅" if rules['saverole'] else '/sn ❌',
                                                url='https://t.me/lupine_guys/134'))
            options.append(InlineKeyboardButton("/shekar ✅ " if rules['shekar'] else '/shekar ❌',
                                                url='https://t.me/lupine_guys/134'))
        else:
            # options.append(InlineKeyboardButton("/saveYourRole ✅",
            #                                     url='https://t.me/lupine_guys/134'))
            options.append(InlineKeyboardButton("/sn ✅",
                                                url='https://t.me/lupine_guys/134'))
            options.append(InlineKeyboardButton("/shekar ✅ ",
                                                url='https://t.me/lupine_guys/134'))
        strings = get_from_db('started_game_button_strings')
        urls = get_from_db('started_game_button_urls')

        buttons = random.choice(
            [[InlineKeyboardButton(button_str.strip(), url=button_url.strip())
              for button_str, button_url in zip(string.split('|-|'), url.split('|-|'))]
             for string, url in zip(strings.split('|@|'), urls.split('|@|'))]
        )
        try:
            texts = return_lang(chat_id).Up
            msg = """{game_started}
┣ {syr}
┣ {ch}
┗ {sn}"""
            ' '
            bot.send_message(chat_id, msg.format(
                syr="/saveYourRole ✅" if not rules or rules['saveyourrole'] else '<code>/saveYourRole ❌</code>',
                ch="/shekar ✅ " if not rules or rules['shekar'] else '<code>/shekar ❌</code>',
                sn="/sn ✅" if not rules or rules['saverole'] else '<code>/sn ❌</code>',
                game_started=(
                    texts.game_started if isinstance(texts.game_started, str) else choice(texts.game_started))),
                             reply_markup=InlineKeyboardMarkup(buttons), parse_mode='HTML')
        except Exception as e:
            print(e)
        msg = bot.send_message(chat_id, message,
                               # reply_markup=InlineKeyboardMarkup(buttons),
                               parse_mode='HTML', disable_web_page_preview=True)
        save_list_message_id_(chat_id, msg.message_id)
        addusers(users, chat_id)
    except Exception as e:
        print('start', e)
