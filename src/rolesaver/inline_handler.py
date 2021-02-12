from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.utils.helpers import mention_html as mention, mention_markdown, escape
from .RANK_STATEMENT import UserStatus
from .cache import get_cached_user
from .db_cmd import get_player_info_no_chat, get_most_votes, get_username_from_id, get_user_afks


def inline_handler(update, context):
    texts = update.user_lang
    user = update.effective_user
    info = get_player_info_no_chat(user.id)
    if info:
        my_stats_text = texts.Mystate.template_inline.format(
            name=mention(user.id, user.first_name),
            type=UserStatus(user).status,
            set=info['role_count'],
            gp_set_count=info['group_count'],
            ranks='|'.join(get_cached_user(user).get_all_emoji_ranks()),
            gp='Inline'
        )
    else:
        my_stats_text = texts.Mystate.no_use
    player = user.id
    votes, voted = get_most_votes(player)

    my_votes_text = ''
    if votes:
        my_votes_text += texts.Mostvotes.voted
        for _, voted_player, count in votes:
            try:
                my_votes_text += '‎ {} <i>{}</i>\n'.format(
                    mention(voted_player, context.bot.get_chat(voted_player).first_name), count)
            except:
                my_votes_text += '‎ {} <i>{}</i>\n'.format(get_username_from_id(voted_player), count)
        my_votes_text += '\n'
    else:
        my_votes_text += texts.Mostvotes.no_vote
    if voted:
        my_votes_text += texts.Mostvotes.votes
        for voter_player, _, count in voted:
            try:
                my_votes_text += '‎ {} <i>{}</i>\n'.format(
                    mention(voter_player, context.bot.get_chat(voter_player).first_name), count)
            except:
                my_votes_text += ' {} <i>{}</i>\n'.format(get_username_from_id(voter_player), count)
        my_votes_text += '\n'
    else:
        my_votes_text += texts.Mostvotes.no_votes
    my_votes_text = my_votes_text.format(mention=mention(player, user.full_name), days=7, where='')
    days = 7
    afks = get_user_afks(user.id, days)
    afks_text = texts.Myafk.header.format(mention_markdown(user.id, 'شما'), days)
    afk_count = 0
    for gap, afk in afks.items():
        afks_text += f'\n‎{gap} - {afk}'
        afk_count += afk
    if afk_count > 5:
        afks_text += '\n\nDon\'t ruin the games...'
    else:
        afks_text = texts.Myafk.no_afk.format(days)

    res = [InlineQueryResultArticle(id='mystate',
                                    title='آمار من',
                                    description='به نظر میرسه ازم استفاده نکردی!' if not info else None,
                                    input_message_content=InputTextMessageContent(
                                        my_stats_text, parse_mode='html', disable_web_page_preview=True
                                    )),
           InlineQueryResultArticle(id='myvotes',
                                    title='رای های من',
                                    description='هیچ رای ای یافت نشد!' if not votes and not voted else None,
                                    input_message_content=InputTextMessageContent(
                                        my_votes_text, parse_mode='html', disable_web_page_preview=True
                                    )),
           InlineQueryResultArticle(id='myafks',
                                    title='افک های من',
                                    description=afks_text[:40] + ('...' if afks else ''),
                                    input_message_content=InputTextMessageContent(
                                        afks_text, parse_mode='markdown', disable_web_page_preview=True
                                    ))
           ]
    update.inline_query.answer(res, is_personal=True, cache_time=100)
