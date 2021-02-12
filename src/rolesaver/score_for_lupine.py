from telegram.utils import helpers

from . import get_cur
from .werewolf_game_class import WWGame, roles_by_emoji
from json import dumps
from flask import request

score_power = False
# score of every role
score_table = {
    1: 10, 2: 60, 3: 11, 4: 32, 5: 53, 6: 20, 7: 15, 8: 19, 9: 50, 10: 33, 11: 34, 12: 27, 13: 40,
    14: 35, 15: 52, 16: 12, 17: 14, 18: 0, 19: 18, 20: 23, 21: 90, 22: 80, 23: 25, 24: 13,
    25: 55, 26: 10, 27: 24, 28: 70, 29: 65, 30: 20, 31: 12, 32: 11, 33: 68, 34: 20, 35: 21,
    36: 0, 37: 17, 38: 22, 39: 59, 40: 18, 41: 100, 42: 16}
# score of being winner
alive_winner_score = 5
# score of lovers
lovers = 85
# score of lovers win
lovers_win = 80
# score of vilg
vilager_scor = 10
# score of tanner win
tanner_win = 70
# score of sk win
skwin_scor = 90
# score of aso win
asowin_score = 100
# score of afk user beside game score
afk_score = -20


def add_score(game_message_id, user_id, score, role_id, is_alive, is_winner, all_data):
    conn, cur = get_cur()
    cur.execute("""
    INSERT INTO v2.lupine_score_table (user_id, score, role_id, alive, winner, extra_data, game_message_id)
     VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (user_id, score, role_id, is_alive, is_winner, all_data, game_message_id))
    conn.commit()


def get_bests(limit=10):
    conn, cur = get_cur()
    cur.execute("""
    select user_id, sum(score)
    from v2.lupine_score_table
    group by user_id
    order by 2 desc
    limit %s;
    """, (limit,))
    res = cur.fetchall()
    return res if res else []


def onscore(update, context):
    global score_power
    if not score_power:
        score_power = True
    update.message.reply_text('score is on')


def offscore(update, context):
    global score_power
    if score_power:
        score_power = False
        update.message.reply_text('score is off')


def detect_game_data(game_message_obj):
    game = WWGame(game_message_obj)
    for player in game.iter_players():
        role_emoji = player.role_emoji().replace('‍❤', '').strip()
        role_id = roles_by_emoji.get(role_emoji, {'role_id': 0})['role_id']
        player.role_id = role_id
        score = score_table.get(role_id, 0)
        if player.is_alive() & player.is_winner() & player.role_id:
            score += alive_winner_score
        if player.is_lover():
            score += lovers
        if player.is_lover() & player.is_winner():
            score += lovers_win
        if player.is_alive() & player.is_winner() & player.role_id == 1:
            score += vilager_scor
        if player.is_winner() & player.role_id == 22:
            score += tanner_win
        if player.is_alive() & player.is_winner() & player.role_id == 21:
            score += skwin_scor
        if player.is_alive() & player.is_winner() & player.role_id == 41:
            score += asowin_score

        player.score = score + 2

    return game


def check_list(update, context):
    if not score_power:
        update.message.reply_text('checklist is off')
        return
    message = update.message.reply_to_message
    try:
        game = detect_game_data(message)
    except Exception as e:
        update.message.reply_text(' '.join(e.args))
        return
    for player in game.iter_players():
        try:
            json_data = dumps(player.__dict__)
        except Exception as e:
            print(e)
            json_data = dumps({})
        add_score(message.message_id, player.user_id, player.score, player.role_id, player.is_alive(),
                  player.is_winner(), json_data)
    txt = '\n'.join(
        [f'[🐾] {player.player_name} | ᵖᵒⁱⁿᵗ {player.score}💎 | ' for player in game.iter_players()])
    update.message.reply_text(f'لــــیــــســــت امــــتــــیــــازات...📄📯\n{txt}')


def bests_list(update, context):
    bests = get_bests(15)
    msgs = []
    player_str = '⊰🐾⊱ {} | ᴘᴏɪɴᴛ {} |'
    page_str = '{header}\n\n{body}\n\n{footer}'
    header = '•| پــــنــــج نــــفــــر بــــرتــــر تــــورنــــمــــنـــت |•'
    footer = '༆𝒎𝒐𝒔𝒕 𝒃𝒆 𝒂 𝒍𝒖𝒑𝒊𝒏𝒆 𝒈𝒖𝒚 𝒕𝒐 𝒃𝒆 𝒂𝒍𝒊𝒗𝒆 💎'
    players = []

    for player in bests:

        player_name = 'ℒ𝓊𝓅𝒾𝓃 𝓅𝓁𝒶𝓎ℯ𝓇'
        try:
            best_player_id = context.bot.get_chat_member(update.effective_message.chat.id, player[0])
            player_name = best_player_id.user.first_name
        except Exception as e:
            print(e)

        players.append((helpers.mention_html(player[0], player_name), player[1]))
    if len(bests) < 30:
        msgs.append(page_str.format(
            header=header,
            footer=footer,
            body='\n'.join([player_str.format(player[0], player[1]) for player in players])))

    for msg in msgs:
        context.bot.send_message(update.message.chat.id, msg, parse_mode='HTML')


def afk_request():
    if not score_power:
        return '2'
    try:
        data = request.get_json(force=True)
    except Exception as e:
        return ' '.join(e.args)
    user_id = data.get('user_id')
    message_id = data.get('message_id')
    if not message_id or not user_id:
        return '201'
    add_score(message_id, user_id, afk_score, 0, False, False, dumps({'afk': True}))
    return '200'
