from apscheduler.schedulers.background import BackgroundScheduler

from .RANK_STATEMENT import UserStatus
from .db_cmd import get_ranks, get_ranks_data

mention_cache = {}
message_id_by_group = {}
cached_user_rank = {}


def save_mention_used(chat_id):
    global mention_cache
    mention_cache.update({chat_id: True})
    pass


def save_mention_usable(chat_id):
    global mention_cache
    mention_cache.update({chat_id: False})
    pass


def get_mention_use(chat_id):
    if chat_id not in mention_cache:
        save_mention_usable(chat_id)
    return mention_cache[chat_id]


def save_list_message_id_(chat_id, message_id):
    global message_id_by_group
    message_id_by_group.update({chat_id: message_id})
    pass


def get_list_message_id(chat_id):
    if chat_id not in message_id_by_group:
        return False
    return message_id_by_group[chat_id]


def cache_user(user: UserStatus):
    global cached_user_rank
    cached_user_rank.update({user.user.id: user})
    pass


def get_cached_user(user):
    if user.id not in cached_user_rank:
        try:
            ranks = get_ranks()
            ranks_data = get_ranks_data()
            user_ranks = ranks.get(user.id)
            res = UserStatus(user)
            if user_ranks:
                res.set_emojies_rank({rank: ranks_data[rank] for rank in user_ranks})
            cache_user(res)
        except Exception as e:
            print(e)
            return False
    return cached_user_rank[user.id]


def reset_cached_users():
    global cached_user_rank
    cached_user_rank = {}


scheduler = BackgroundScheduler()
scheduler.add_job(func=reset_cached_users, trigger="interval", seconds=500)
scheduler.start()
