from datetime import datetime
from telegram.utils.helpers import escape_markdown
from cachetools import cached, TTLCache
from pytz import timezone
from threading import Timer
from . import get_cur

iran = timezone('Asia/Tehran')


def now():
    sa_time = datetime.now(iran)
    return sa_time.strftime('%Y-%m-%d %H:%M:%S')


def use_message(chat_id, message_id):
    conn, cur = get_cur()
    try:
        query = f"""
        insert into v1.rulesaver_message_used(group_id, message_id, created_at) 
        values ({chat_id}, {message_id}, '{now()}')
        """
        cur.execute(query)
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        use_message(chat_id, message_id)


def add_game(chat_id, players_data, message_id):
    conn, cur = get_cur()
    try:
        players = players_data
        query = f"""
        insert into v1.rulesaver_games1(group_id, created_at, all_players, allow_players) 
        values({chat_id}, '{now()}', '{players}', '{players}')
        """
        # conn, cur=get_cur()
        cur.execute(query)
        conn.commit()
        cur.close()
        use_message(chat_id, message_id)
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        add_game(chat_id, players_data, message_id)


def add_rule(chat_id, user_data):
    conn, cur = get_cur()
    try:
        print('adding')
        user_id = user_data['id']
        delete_rule(chat_id, user_data)
        rule = user_data['role']
        # username = user_data['username']
        query = f"""
        insert into v1.rulesaver_roles(group_id, user_id, rule, created_at)
         values(%s,%s,%s,%s)
        """
        # conn, cur=get_cur()
        cur.execute(query, (chat_id, user_id, rule, now()))
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        add_rule(chat_id, user_data)


def update_game_db(chat_id, players_data, message_id):
    conn, cur = get_cur()
    try:
        allow_players = players_data
        query = f"""
        update v1.rulesaver_games1 
        set allow_players = '{allow_players}'
        where group_id ={chat_id} and deleted_at is null
        """
        # conn, cur=get_cur()
        cur.execute(query)
        conn.commit()
        cur.close()
        use_message(chat_id, message_id)
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        update_game_db(chat_id, players_data, message_id)


def delete_rule(chat_id, user_data):
    conn, cur = get_cur()
    try:
        user_id = user_data['id']
        query = f"""
        update v1.rulesaver_roles
        set deleted_at ='{now()}'
        where group_id = {chat_id} and user_id = {user_id} and deleted_at is null
        """
        # conn, cur=get_cur()
        cur.execute(query)
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        delete_rule(chat_id, user_data)


def delete_game(chat_id, message_id):
    conn, cur = get_cur()
    try:
        query = f"""
        update v1.rulesaver_games1
        set deleted_at = '{now()}'
        where group_id = {chat_id} and deleted_at is null
        """
        query2 = f"""
        update v1.rulesaver_roles
        set deleted_at ='{now()}'
        where group_id = {chat_id} and deleted_at is null
        """
        # conn, cur=get_cur()
        cur.execute(query)
        cur.execute(query2)
        conn.commit()
        cur.close()
        use_message(chat_id, message_id)
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        delete_game(chat_id, message_id)


def ban_user(chat_id, user_data, ban_data):
    conn, cur = get_cur()
    try:
        user_id = user_data['id']
        banner_id = ban_data['id']
        query = f"""
        insert into v1.rulesaver_bad_players(group_id, user_id, baned_by, created_at)
         VALUES ({chat_id}, {user_id}, {banner_id}, '{now()}')
        """
        # conn, cur=get_cur()
        cur.execute(query)
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        ban_user(chat_id, user_data, ban_data)


def unban_user(chat_id, user_data, unban_data):
    conn, cur = get_cur()
    try:
        user_id = user_data['id']
        unbanner_id = unban_data['id']
        query = f"""
        update v1.rulesaver_bad_players
        set unbaned_by = {unbanner_id} , deleted_at = '{now()}'
        where group_id = {chat_id} and user_id = {user_id} and deleted_at is null
        """
        # conn, cur=get_cur()
        cur.execute(query)
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


def get_allow_players(chat_id):
    conn, cur = get_cur()
    try:
        query = f"""
        select allow_players
        from v1.rulesaver_games1
        where group_id = {chat_id} and deleted_at is null  
        """
        # conn, cur=get_cur()
        cur.execute(query)
        res = cur.fetchone()
        cur.close()
        try:
            if res:
                res = res[0].replace('[', '').replace(']', '')
                res = res.split(',')
                res = [int(i) for i in res]
        except:
            return False
        return res
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        return get_allow_players(chat_id)


def get_all_players(chat_id):
    conn, cur = get_cur()
    try:
        query = f"""
        select all_players
        from v1.rulesaver_games1
        where group_id = {chat_id} and deleted_at is null  
        """
        # conn, cur=get_cur()
        cur.execute(query)
        res = cur.fetchone()
        cur.close()
        if res:
            res = res[0].replace('[', '').replace(']', '')
            res = res.split(',')
            res = [int(i) for i in res]
        return res
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        return get_all_players(chat_id)


def get_all_roleseted_players(chat_id):
    conn, cur = get_cur()
    try:
        query = f"""
        select distinct user_id
        from v1.rulesaver_roles
        where group_id = {chat_id} and deleted_at is null  
        """
        # conn, cur=get_cur()
        cur.execute(query)
        res = cur.fetchall()
        cur.close()
        return [i[0] for i in res]
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        return get_all_roleseted_players(chat_id)


def get_player_info(chat_id, user_id):
    conn, cur = get_cur()
    try:
        query = f"""
    with t as (select count(user_id) as c_games
        from v1.rulesaver_roles
        where group_id = {chat_id} and user_id = {user_id})
    select count(rule) as trule, count(distinct group_id) as gps, t.c_games
    from v1.rulesaver_roles , t
    WHERE user_id = {user_id}
    group by c_games
        """
        # conn, cur=get_cur()
        cur.execute(query)
        res = cur.fetchone()
        cur.close()
        if res:
            return {
                'role_count': res[0],
                'group_count': res[1],
                'group_role': res[2]
            }
        if not res:
            return res
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        return get_player_info(chat_id, user_id)


def get_player_info_no_chat(user_id):
    conn, cur = get_cur()
    try:
        query = f"""
    select count(rule) as trule, count(distinct group_id) as gps
    from v1.rulesaver_roles
    WHERE user_id = {user_id}
        """
        cur.execute(query)
        res = cur.fetchone()
        cur.close()
        if res:
            return {
                'role_count': res[0],
                'group_count': res[1]
            }
        return res
    except Exception as e:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        return get_player_info_no_chat(user_id)


@cached(cache=TTLCache(maxsize=1024, ttl=1800))
def get_self_data():
    conn, cur = get_cur()
    try:
        query = f"""

with data1 as (
select count(distinct group_id) d
from v1.all_group_helper
),data2 as (

select count(*) t
from v1.rulesaver_roles
), data3 as(
select count(*)h
from v1.rulesaver_users
), data4 as(
select count(*)
from v1.manager_delete_message
), data5 as(
select count(*)
from v2.users_activity_log
), data6 as(
select count(*)
from v2.all_games
)
select *
from data1,data2,data3,data4,data5,data6;
"""
        # conn, cur=get_cur()
        cur.execute(query)
        res = cur.fetchone()
        cur.close()
        if res:
            return {
                'groups': res[0],
                'roles': res[1],
                'users': res[2],
                'deleted_msg': res[3],
                'confirmed_plays': res[4],
                'confirmed_games': res[5]
            }
        if not res:
            return res
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        return get_self_data()


def get_player_status(chat_id, user_id):
    conn, cur = get_cur()
    try:
        query = f"""
        select baned_by ,created_at
        from v1.rulesaver_bad_players
        where group_id = {chat_id} and user_id = {user_id} and deleted_at is null
        """
        # conn, cur=get_cur()
        cur.execute(query)
        res = cur.fetchone()
        cur.close()
        if res:
            return True
        if not res:
            return False
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        return get_player_status(chat_id, user_id)


def check_player_ban(func):
    def wrapper(update, context):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        if chat_id != user_id:
            if get_player_status(chat_id, user_id):
                return
        return func(update, context)

    return wrapper


def get_group_info(chat_id):
    conn, cur = get_cur()
    try:
        query = f"""
    with a(res)  as(
    select  count(group_id)
    from v1.rulesaver_games1
    where group_id= {chat_id})
    select  a.res ,count(rule) ,count(distinct user_id)
    from v1.rulesaver_roles, a
    where group_id= {chat_id}
    group by a.res
        """
        # conn, cur=get_cur()
        cur.execute(query)
        res = cur.fetchone()
        cur.close()
        if res:
            return {
                'all_games_count': res[0],
                'role_count': res[1],
                'player_count': res[2]
            }
        if not res:
            return res
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        return get_group_info(chat_id)


def get_used_message(chat_id):
    conn, cur = get_cur()
    try:
        query = f"""
        select message_id
        from v1.rulesaver_message_used
        where group_id = {chat_id}
        """
        # conn, cur=get_cur()
        cur.execute(query)
        res = cur.fetchall()
        cur.close()
        return set([i[0] for i in res])
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        return get_used_message(chat_id)


def get_role_list(chat_id):
    conn, cur = get_cur()
    try:
        query = f"""
        select user_id, rule
        from v1.rulesaver_roles
        where  group_id = {chat_id} and deleted_at is null
        """
        # conn, cur=get_cur()
        cur.execute(query)
        res = cur.fetchall()
        cur.close()
        return {i[0]: i[1] for i in res}
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        return get_role_list(chat_id)


def set_shekarchi_db(chat_id, user_id):
    conn, cur = get_cur()
    try:
        query = f"""
            update v1.rulesaver_games1
            set shekarchi = %s
            where group_id = %s and deleted_at is null
            """
        # conn, cur=get_cur()
        cur.execute(query, (user_id, chat_id))
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


def set_nazer_db(chat_id, user_id):
    conn, cur = get_cur()
    try:
        query = f"""
            update v1.rulesaver_games1
            set nazer = {user_id}
            where group_id = {chat_id} and deleted_at is null
            """
        # conn, cur=get_cur()
        cur.execute(query)
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


def set_vote_db(chat_id, vote):
    conn, cur = get_cur()
    try:
        query = f"""
            update v1.rulesaver_games1
            set vote = %(vote)s
            where group_id = %(chat_id)s and deleted_at is null
            """
        # conn, cur=get_cur()
        cur.execute(query, {'chat_id': chat_id, 'vote': vote})
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        set_vote_db(chat_id, vote)


def get_shekarchi_db(chat_id):
    conn, cur = get_cur()
    try:
        query = f"""
        select shekarchi
        from v1.rulesaver_games1
        where group_id = {chat_id} and deleted_at is null
        """
        # conn, cur=get_cur()
        cur.execute(query)
        res = cur.fetchone()
        cur.close()
        if res:
            return res[0]
        elif not res:
            return res
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        return get_shekarchi_db(chat_id)


def get_nazer_db(chat_id):
    conn, cur = get_cur()
    try:
        query = f"""
        select shekarchi
        from v1.rulesaver_games1
        where group_id = {chat_id} and deleted_at is null
        """
        # conn, cur=get_cur()
        cur.execute(query)
        res = cur.fetchone()
        cur.close()
        if res:
            return res[0]
        elif not res:
            return res
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        return get_nazer_db(chat_id)


def get_vote_db(chat_id):
    conn, cur = get_cur()
    try:
        query = f'''
        select vote
        from v1.rulesaver_games1
        where group_id = {chat_id} and deleted_at is null
        '''
        # conn, cur=get_cur()
        cur.execute(query)
        res = cur.fetchone()
        cur.close()
        if res:
            return res[0]
        elif not res:
            return res
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        return get_vote_db(chat_id)


def get_user_id_from_username(username):
    conn, cur = get_cur()
    try:
        query = f"""
        select user_id
        from v1.rulesaver_users
        where username = '{username}'
        """
        cur.execute(query)
        res = cur.fetchone()
        cur.close()
        if res:
            return res[0]
        elif not res:
            return res
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        return get_user_id_from_username(username)


def update_user(data):
    conn, cur = get_cur()
    try:
        query = f"""
UPDATE v1.rulesaver_users SET username= %(username)s , updated_at= %(time)s WHERE user_id= %(user_id)s ;
INSERT INTO v1.rulesaver_users(user_id, username, created_at)
       SELECT %(user_id)s, %(username)s, %(time)s
       WHERE NOT EXISTS (SELECT 1 FROM v1.rulesaver_users WHERE user_id= %(user_id)s );
        """
        # conn, cur=get_cur()
        cur.executemany(query, data)
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


def get_all_users_with_username():
    conn, cur = get_cur()
    try:
        query = f"""
        select user_id , username
        from v1.rulesaver_users
        """
        cur.execute(query)
        res = cur.fetchall()
        cur.close()
        if res:
            users = {}
            for i in res:
                if i[1] == 'None':
                    username = None
                else:
                    username = i[1]
                users.update(
                    {
                        i[0]: username
                    }
                )
            return users
        elif not res:
            return res
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        return get_all_users_with_username()


# todo
def setup(chat_id):
    conn, cur = get_cur()
    try:
        query = f"""
        insert into v1.all_groups(group_id,created_at)
        values (%s,%s)
        """
        # conn, cur=get_cur()
        cur.execute(query, (chat_id, now()))
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


def set_saveYourRole(chat_id, state):
    conn, cur = get_cur()
    try:
        query = f"""
    update v1.all_groups
    set is_saveyourrole_allow = %s
    where group_id = %s
    """
        # conn, cur=get_cur()
        cur.execute(query, (state, chat_id))
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


def set_saveRole(chat_id, state):
    conn, cur = get_cur()
    try:
        query = f"""
    update v1.all_groups
    set is_saverole_allow = %s
    where group_id = %s
    """
        # conn, cur=get_cur()
        cur.execute(query, (state, chat_id))
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


def set_shekar(chat_id, state):
    conn, cur = get_cur()
    try:
        query = f"""
    update v1.all_groups
    set is_setshekar_allow = %s
    where group_id = %s
    """
        # conn, cur=get_cur()
        cur.execute(query, (state, chat_id))
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


def get_group_rules(chat_id):
    """

    :param chat_id:
    :return: saveyour ,shekar,saverole
    """
    conn, cur = get_cur()
    try:
        query = f"""
    select is_saveyourrole_allow  saveyourrole, is_setshekar_allow shekar, is_saverole_allow saverole, cult_option
    from v1.all_groups
    where group_id = %s"""
        # conn, cur=get_cur()
        cur.execute(query, (chat_id,))
        res = cur.fetchone()
        cur.close()
        if res:
            return {
                'saveyourrole': res[0],
                'shekar': res[1],
                'saverole': res[2],
                'cult_option': res[3]
            }
        return res
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


def get_group_setting(group_id):
    conn, cur = get_cur()
    try:
        query = f"""
select jointime_pin as jtp,
       game_started_pin as stp,
       is_confirm_tsww_enable as cts,
       is_confirm_score_enable as cs,
       is_startnewgame_enable as stn,
       start_mode as stm,
       disabled_by
from v1.all_group_helper
where group_id = %s
        """
        # conn, cur=get_cur()
        cur.execute(query, (group_id,))
        res = cur.fetchone()
        cur.close()
        if res:
            return dict(
                jointime_pin=res[0],
                game_started_pin=res[1],
                is_confirm_tsww_enable=res[2],
                is_confirm_score_enable=res[3],
                is_startnewgame_enable=res[4],
                start_mode=res[5],
                role_saver=res[6]
            )
        if not res: return res
    except:
        cur.close()
        return False


def set_pin_players(chat_id, state):
    conn, cur = get_cur()
    try:
        query = f"""
    update v1.all_group_helper
    set jointime_pin = %s
    where group_id = %s
    """
        # conn, cur=get_cur()
        cur.execute(query, (state, chat_id))
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


def set_next_pin(chat_id, state):
    conn, cur = get_cur()
    try:
        query = f"""
    update v1.all_group_helper
    set game_started_pin = %s
    where group_id = %s
    """
        # conn, cur=get_cur()
        cur.execute(query, (state, chat_id))
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


def set_tsww(chat_id, state):
    conn, cur = get_cur()
    try:
        query = f"""
    update v1.all_group_helper
    set is_confirm_tsww_enable = %s
    where group_id = %s
    """
        # conn, cur=get_cur()
        cur.execute(query, (state, chat_id))
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


def set_fillIt(chat_id, state):
    conn, cur = get_cur()
    try:
        query = f"""
    update v1.all_group_helper
    set is_confirm_score_enable = %s
    where group_id = %s
    """
        # conn, cur=get_cur()
        cur.execute(query, (state, chat_id))
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


def set_startNewGame(chat_id, state):
    conn, cur = get_cur()
    try:
        query = f"""
    update v1.all_group_helper
    set is_startnewgame_enable = %s
    where group_id = %s
    """
        # conn, cur=get_cur()
        cur.execute(query, (state, chat_id))
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


def set_startmode(chat_id, state):
    conn, cur = get_cur()
    try:
        query = f"""
    update v1.all_group_helper
    set start_mode = %s
    where group_id = %s
    """
        # conn, cur=get_cur()
        cur.execute(query, (state, chat_id))
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


def set_roleSaver(chat_id, state):
    conn, cur = get_cur()
    try:
        query = f"""
    update v1.all_group_helper
    set disabled_by = %s
    where group_id = %s
    """
        # conn, cur=get_cur()
        cur.execute(query, (state, chat_id))
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


def black_get_group_setting(group_id):
    conn, cur = get_cur()
    try:
        query = f"""
select jointime_pin as jtp,
       game_started_pin as stp,
       is_confirm_tsww_enable as cts,
       is_startnewgame_enable as stn,
       start_mode as stm,
       role_save_mode
from v1.all_group_helper_black_werewolf
where group_id = %s
        """
        # conn, cur=get_cur()
        cur.execute(query, (group_id,))
        res = cur.fetchone()
        cur.close()
        if res:
            return dict(
                jointime_pin=res[0],
                game_started_pin=res[1],
                is_confirm_tsww_enable=res[2],
                is_startnewgame_enable=res[3],
                start_mode=res[4],
                role_saver=res[5]
            )
        if not res: return res
    except Exception as e:
        print(e)
        cur.close()
        return False


def black_set_pin_players(chat_id, state):
    conn, cur = get_cur()
    try:
        query = f"""
    update v1.all_group_helper
    set jointime_pin = %s
    where group_id = %s
    """
        # conn, cur=get_cur()
        cur.execute(query, (state, chat_id))
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


def black_set_next_pin(chat_id, state):
    conn, cur = get_cur()
    try:
        query = f"""
    update v1.all_group_helper
    set game_started_pin = %s
    where group_id = %s
    """
        # conn, cur=get_cur()
        cur.execute(query, (state, chat_id))
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


# def black_set_tsww(chat_id, state):
#     conn, cur=get_cur()
#     try:
#         query = f"""
#     update v1.all_group_helper
#     set is_confirm_tsww_enable = %s
#     where group_id = %s
#     """
#         # conn, cur=get_cur()
#         cur.execute(query, (state, chat_id))
#         conn.commit()
#         cur.close()
#     except:
#         cur.execute("rollback")
#         conn.commit()
#         cur.close()
#
#
# def black_set_fillIt(chat_id, state):
#     conn, cur=get_cur()
#     try:
#         query = f"""
#     update v1.all_group_helper_black_werewolf
#     set is_confirm_score_enable = %s
#     where group_id = %s
#     """
#         # conn, cur=get_cur()
#         cur.execute(query, (state, chat_id))
#         conn.commit()
#         cur.close()
#     except:
#         cur.execute("rollback")
#         conn.commit()
#         cur.close()
#

def black_set_startNewGame(chat_id, state):
    conn, cur = get_cur()
    try:
        query = f"""
    update v1.all_group_helper_black_werewolf
    set is_startnewgame_enable = %s
    where group_id = %s
    """
        # conn, cur=get_cur()
        cur.execute(query, (state, chat_id))
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


def black_set_startmode(chat_id, state):
    conn, cur = get_cur()
    try:
        query = f"""
    update v1.all_group_helper_black_werewolf
    set start_mode = %s
    where group_id = %s
    """
        # conn, cur=get_cur()
        cur.execute(query, (state, chat_id))
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


def black_set_roleSaver(chat_id, state):
    conn, cur = get_cur()
    try:
        query = f"""
    update v1.all_group_helper_black_werewolf
    set role_save_mode = %s
    where group_id = %s
    """
        # conn, cur=get_cur()
        cur.execute(query, (state, chat_id))
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


def get_last_game_time(group_id):
    conn, cur = get_cur()
    try:
        query = """
select created_at
from v1.rulesaver_games1
where group_id = %s
order by created_at desc
limit 1
        """
        cur.execute(query, (group_id,))
        res = cur.fetchone()
        cur.close()
        if res:
            datetime_object = datetime.strptime(res[0], '%Y-%m-%d %H:%M:%S')
            return datetime_object
        return datetime.now()
    except:
        cur.close()
        return datetime.now()


def set_list_type(chat_id, list_type):
    conn, cur = get_cur()
    chat_id = int(chat_id)
    try:
        query = """
UPDATE v1.rulesaver_list_setting SET list_type=%(list_type)s WHERE chat_id=%(chat_id)s;
INSERT into v1.rulesaver_list_setting (chat_id, list_type)
SELECT %(chat_id)s, %(list_type)s
WHERE NOT EXISTS (SELECT 1 from v1.rulesaver_list_setting WHERE chat_id=%(chat_id)s)
        """
        cur.execute(query, {'chat_id': chat_id, 'list_type': list_type})
        conn.commit()
        cur.close()
        return
    except Exception as e:
        print(e)
        cur.close()
        return


def set_cult_option(chat_id, cult_option):
    conn, cur = get_cur()
    try:
        query = f"""
        update v1.all_groups
        set cult_option = %s
        where group_id = %s
        """
        # conn, cur=get_cur()
        cur.execute(query, (cult_option, chat_id))
        conn.commit()
        cur.close()
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()


def get_list_type(chat_id):
    conn, cur = get_cur()
    try:
        query = """
SELECT list_type FROM v1.rulesaver_list_setting
WHERE chat_id=%(chat_id)s
            """
        cur.execute(query, {'chat_id': chat_id})
        res = cur.fetchone()
        cur.close()
        if res:
            return res[0]
        else:
            return 0
    except:
        cur.close()
        return


def get_ranks():
    conn, cur = get_cur()
    query = """
    select user_id, array_agg(rank_id)
    from v2.members_ranks
    where disabled_at is null
group by user_id
"""
    cur.execute(query)
    res = cur.fetchall()
    if res:
        return {i[0]: i[1] for i in res}
    return {}


def get_ranks_v2():
    conn, cur = get_cur()
    query = """
    select user_id, rank_emoji,global_emoji,special_emoji
    from v2.selected_emojies_by_user em 
    """
    cur.execute(query)
    res = cur.fetchall()
    if res:
        return {i[0]: i[2] for i in res}
    return {}


def get_all_ranks():
    conn, cur = get_cur()
    query = """
    select id, emoji, title
    from v2.ranks 
    """
    cur.execute(query)
    res = cur.fetchall()
    if res:
        return {i[0]: {'emoji': i[1], 'title': i[2]} for i in res}
    return {}


def add_rank(user_id, rank_id):
    conn, cur = get_cur()
    query = """
INSERT INTO v2.members_ranks (user_id, rank_id)
       SELECT %(user_id)s, %(rank_id)s
       WHERE NOT EXISTS (SELECT 1 FROM v2.members_ranks WHERE user_id=%(user_id)s and rank_id=%(rank_id)s); 
        """
    cur.execute(query, {
        'user_id': user_id,
        'rank_id': rank_id
    })
    conn.commit()


@cached(cache=TTLCache(maxsize=1024, ttl=180))
def get_ranks_data():
    conn, cur = get_cur()
    try:
        query = f"""
select id,title,emoji,parent_id
from v2.ranks
"""
        cur.execute(query)
        res = cur.fetchall()
        cur.close()
        if res:
            return {i[0]: {'id': i[0], 'title': i[1], 'emoji': i[2], 'parent_id': i[3]} for i in res}
        return {}

    except Exception as e:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        return get_ranks_data()


@cached(cache=TTLCache(maxsize=1024, ttl=60))
def get_top_roles(group_id, days, all_groups=False, role=False):
    if all_groups:
        query = """SELECT user_id, role_id, count(role_id) as c FROM v2.users_activity_log_v2
                   WHERE created_at::timestamp > %(now)s::timestamp - interval '%(days)s days'
                   GROUP BY user_id, role_id
                   ORDER By c desc
                   LIMIT 10"""
    else:
        query = """SELECT user_id, role_id, count(role_id) as c FROM v2.users_activity_log_v2
                   WHERE group_id = %(group_id)s AND created_at::timestamp > %(now)s::timestamp - interval '%(days)s days'
                   GROUP BY user_id, role_id
                   ORDER By c desc
                   LIMIT 10"""
    conn, cur = get_cur()
    cur.execute(query, {'group_id': group_id, 'now': now(), 'days': days})
    return cur.fetchall()


@cached(cache=TTLCache(maxsize=1024, ttl=60))
def get_user_roles(user_id, days):
    query = """SELECT role_id, count(role_id) as c FROM v2.users_activity_log_v2
            WHERE user_id = %(user_id)s AND created_at::timestamp > %(now)s::timestamp - interval '%(days)s days'
            GROUP BY user_id, role_id
            ORDER By c desc
            LIMIT 5"""
    conn, cur = get_cur()
    cur.execute(query, {'user_id': user_id, 'now': now(), 'days': days})
    return cur.fetchall()


@cached(cache=TTLCache(maxsize=1024, ttl=60))
def get_top_roles_detailed(group_id, days, role_id, all_groups=False):
    if all_groups:
        query = """SELECT user_id, count(role_id) as c FROM v2.users_activity_log_v2
                   WHERE created_at::timestamp > %(now)s::timestamp - interval '%(days)s days' AND role_id = %(role_id)s
                   GROUP BY user_id, role_id
                   ORDER By c desc
                   LIMIT 10"""
    else:
        query = """SELECT user_id, count(role_id) as c FROM v2.users_activity_log_v2
                   WHERE group_id = %(group_id)s AND created_at::timestamp > %(now)s::timestamp - interval '%(days)s days' AND role_id = %(role_id)s
                   GROUP BY user_id, role_id
                   ORDER By c desc
                   LIMIT 10"""
    conn, cur = get_cur()
    cur.execute(query, {'group_id': group_id, 'now': now(), 'days': days, 'role_id': role_id})
    return cur.fetchall()


def get_most_votes(player: int, chat_id=None, days=7):
    query = """(SELECT voter, voted, count(*) as c from v1.player_votes
               WHERE voter = %(player)s and vote_at > %(now)s::timestamp - interval '{1} days' {0}
               GROUP BY voter, voted
               ORDER BY c DESC
               LIMIT 5)
               UNION ALL
               (SELECT voter, voted, count(*) as c from v1.player_votes
               WHERE voted = %(player)s and vote_at > %(now)s::timestamp - interval '{1} days' {0}
               GROUP BY voter, voted
               ORDER BY c DESC
               LIMIT 5)
               """.format(f" and chat_id = {chat_id}" if chat_id else "", days)
    conn, cur = get_cur()
    cur.execute(query, {'player': player, 'now': now()})
    res = cur.fetchall()
    votes = [i for i in res if i[0] == player]
    voted = [i for i in res if i[1] == player]
    return votes, voted


def set_next(chat_id, next_text, next_media_id, next_type):
    query = """UPDATE v1.group_nexts SET next_text=%(next_text)s , next_media_id=%(next_media_id)s, next_type=%(next_type)s, created_at=%(now)s WHERE chat_id=%(chat_id)s;
INSERT INTO v1.group_nexts (chat_id, next_text, next_media_id, next_type, created_at)
       SELECT %(chat_id)s, %(next_text)s, %(next_media_id)s, %(next_type)s, %(now)s
       WHERE NOT EXISTS (SELECT 1 FROM v1.group_nexts WHERE chat_id=%(chat_id)s);"""
    conn, cur = get_cur()
    cur.execute(query,
                {'chat_id': chat_id, 'next_text': next_text, 'next_media_id': next_media_id, 'next_type': next_type,
                 'now': now()})
    conn.commit()


def get_next(chat_id):
    query = """SELECT next_text, next_media_id, next_type FROM v1.group_nexts
               WHERE chat_id=%s"""
    conn, cur = get_cur()
    cur.execute(query, (chat_id,))
    return cur.fetchone()


def get_username_from_id(user_id):
    conn, cur = get_cur()
    try:
        user_id = int(user_id)
        query = f"""
        select username
        from v1.rulesaver_users
        where user_id = {user_id}
        """
        cur.execute(query)
        res = cur.fetchone()
        cur.close()
        if res:
            if res[0]:
                return '@' + res[0]
        return user_id
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        return get_username_from_id(user_id)


def update_gp_url(group_id, link):
    conn, cur = get_cur()
    try:
        query = f"""
        update v1.all_group_helper
        set link = %s
        where group_id= %s
        """
        # cur = conn.cursor()
        cur.execute(query, (link, group_id))
        conn.commit()
        cur.close()
        return True
    except:
        cur.execute("rollback")
        conn.commit()
        cur.close()
        return False


def get_user_afks(user_id, days=7):
    query = """select title ,link ,count(*) as c from v2.users_afks
               join v1.all_group_helper on group_id=chat_id
               where user_id=%(user_id)s and afk_at::timestamp > %(now)s::timestamp - interval '%(days)s days'
               group by title ,link
               order by c desc"""
    conn, cur = get_cur()
    cur.execute(query, {'now': now(), 'days': days, 'user_id': user_id})
    res = cur.fetchall()
    return {f'[{escape_markdown(i[0])}]({i[1]})': i[2] for i in res}


chat_langs = {}
recent_langs = {}


def get_chat_langs():
    query = """select * from v2.chat_langs where chat_id < 0"""
    conn, cur = get_cur()
    cur.execute(query)
    res = cur.fetchall()
    global chat_langs
    chat_langs = {i[0]: i[1] for i in res}


@cached(cache=TTLCache(maxsize=1024, ttl=120))
def get_user_lang_db(user_id):
    query = """select lang from v2.chat_langs where chat_id=%s"""
    conn, cur = get_cur()
    cur.execute(query, (user_id,))
    res = cur.fetchone()
    if res:
        return res[0]
    else:
        return 'fa'


def get_chat_lang(chat_id):
    if chat_id < 0:
        return chat_langs.get(chat_id, 'fa')
    else:
        if chat_id in recent_langs:
            return recent_langs[chat_id]
        return get_user_lang_db(chat_id)


def remove_lang_cache(user_id):
    global recent_langs
    try:
        recent_langs.pop(user_id)
    except:
        pass


def change_chat_lang(chat_id, lang):
    query = """UPDATE v2.chat_langs SET lang=%(lang)s where chat_id=%(chat_id)s;
               INSERT INTO v2.chat_langs(chat_id, lang)
               SELECT %(chat_id)s, %(lang)s WHERE NOT EXISTS (SELECT 1 FROM v2.chat_langs WHERE chat_id=%(chat_id)s)"""
    conn, cur = get_cur()
    cur.execute(query, {'chat_id': chat_id, 'lang': lang})
    conn.commit()
    if chat_id < 0:
        global chat_langs
        chat_langs[chat_id] = lang
    else:
        global recent_langs
        recent_langs[chat_id] = lang
        Timer(125, remove_lang_cache, args=(chat_id,)).start()


def get_bi_adab_chats():
    query = """select title, link from v2.chat_langs
        join v1.all_group_helper on group_id=chat_id
        where lang='fb' """
    conn, cur = get_cur()
    cur.execute(query)
    return [f'[{i[0]}]({i[1]})' for i in cur.fetchall()]


get_chat_langs()


@cached(cache=TTLCache(maxsize=1024, ttl=120))
def get_from_permission(permission_id):
    conn, cur = get_cur()
    query = """
    select array_agg(user_id) 
    from v2.permissions
    where permission_id= %(permission_id)s and deleted_at is null
    """
    cur.execute(query, {'permission_id': permission_id})
    res = cur.fetchone()
    if not res:
        return []
    return res[0]


get_admins_id = lambda: get_from_permission(3)
get_game_bots_id = lambda: get_from_permission(1)
get_helpers_id = lambda: get_from_permission(2)
