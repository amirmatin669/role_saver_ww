from .db_cmd import get_most_votes, get_username_from_id, check_player_ban
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import mention_html
from . import BotStats, check_channel_join


@check_channel_join
@check_player_ban
@run_async
def most_votes(update, context):
    reply = update.message.reply_to_message
    args = context.args
    chat_id = update.message.chat.id
    texts = update.chat_lang.Mostvotes
    days = 7
    for arg in args:
        if arg.isdigit() and 15 > len(arg) > 5:
            player = int(arg)
            try:
                mention = mention_html(player, context.bot.get_chat(player).first_name)
            except:
                mention = get_username_from_id(player)
                break
        elif arg.isdigit():
            arg = int(arg)
            if 1 <= arg <= 31:
                days = int(arg)
        elif '@' == arg[0] and 5 < len(args) < 32:
            try:
                player_info = context.bot.get_chat(args[0])
                player = player_info.id
                mention = mention_html(player, player_info.first_name)
                break
            except:
                player = update.message.from_user.id
                mention = update.message.from_user.mention_html()
                break
    else:
        if reply:
            player = reply.from_user.id
            mention = reply.from_user.mention_html()
        else:
            player = update.message.from_user.id
            mention = update.message.from_user.mention_html()
    if chat_id == -1001461432821:
        chat_id = player
    votes, voted = get_most_votes(player, chat_id if chat_id != player else None, days=days)
    text = ''
    where = texts.in_the + f"<b>{update.message.chat.title}</b>" if chat_id != player else ''
    if votes:
        text += texts.voted
        for _, voted_player, count in votes:
            try:
                text += '‎ {}: <i>{}</i>\n'.format(
                    mention_html(voted_player, rf"{context.bot.get_chat(voted_player).first_name}"), count)
            except:
                text += '‎ {}: <i>{}</i>\n'.format(get_username_from_id(voted_player), count)
        text += '\n'
    else:
        text += texts.no_vote
    if voted:
        text += texts.votes
        for voter_player, _, count in voted:
            try:
                text += '‎ {}: <i>{}</i>\n'.format(
                    mention_html(voter_player, rf"{context.bot.get_chat(voter_player).first_name}"), count)
            except:
                text += '‎ {}: <i>{}</i>\n'.format(get_username_from_id(voter_player), count)
        text += '\n'
    else:
        text += texts.no_votes
    update.message.reply_text(text.format(mention=mention, where=where, days=days), parse_mode='html')
    BotStats.most_votes += 1
