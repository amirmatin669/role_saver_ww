title = 'en'

start = "Hi! Add me to your werewolf group to start using my features"


class Sn:
    admin_unblock = "Ask an admin to unblock you"
    inactive = "This feature is inactive in this group"
    dont_blow = "Don't blow"
    amitis_no_role = "You Didn't save a role Amitis💜"
    amitis_saved = "Role Saved Amitis💜"
    check_youre_dead = "It seems you're dead"
    check_youre_dead_amitis = "It seems you're dead Amitis💜"
    not_in_game = "You're not in the game"
    not_in_game_amitis = "You're not in game Amitis💜"
    start_a_game = "No game is running.\nStart one"


class Up:
    rep_to_bot = "Reply to a werewolf bot list"
    used_list = "This list has been used before"
    good_game = "Good Game"
    list_updated = "List Updated"
    game_started = "Game has been started"


class List:
    ch = ["Cult Hunter :"]
    list_empty = "Role list is empty"
    dead_list = "Dead List:💀\n\n"
    no_role = "Players without role:🙃\n\n"
    role_list = 'Role List:🙂\n\n'


class Dl:
    ok = "Ok"


class Shekar:
    ch_set = "{} is now the game Cult Hunter"
    rep_ch = "You should reply this command on Cult hunter"
    only_admins = "Only admin can use this command"


class Sv:
    inactive = Sn.inactive
    not_alive = "This player is not alive"
    like_this = "You should tell the target after the command. e.g:\n /sv @username"
    vote_saved = "Vote Set!"
    only_ch = "Only CH can set votes"
    no_ch = "No CH found"


class Vt:
    inactive = Sn.inactive
    say_vote = ["Lynch {} \n\n\n No one vote any other person"]
    vote_dead = "Setted vote has been dead"
    whos_vote = "{} who to lynch?"
    no_ch = Sv.no_ch
    no_vote = "Vote has not been setted"
    ch_dead = "Unfortunately CH is dead"

    #


class Ev:
    eq_list = "Equal Lynching list"
    no_game = "No game is on!"


class Block:
    ban_before = "This poor user has been blocked before :("
    banned = "Blocked successfuly!, This user can't use any commands in this group from now on"
    go_admin = "Go ask an admin to do that"
    cant = "Wanna block yourself?"


class Unblock:
    unblocked = "This user is not blocked anymore"
    good_guy = "He's a good guy he's not blocked"
    only_admin = "You're not admin in this group so do your own business"


class Mystate:
    template = '''
‎┏ <b>Name</b>
‎┃ {name}
‎┣ <b>User Type</b> <a href="https://t.me/lupine_guys/32">❓</a>
‎‎┃ <code>{type}</code>
‎┣ <b>Ranks</b>
‎‎┃ <code>{ranks}</code>
‎┣ <b>All roles set</b>
‎‎┃ <code>{set}</code>
‎┣ <b>All roles set in this group</b>
‎‎┃ ‏<code>{gp_set}</code>
‎┣ <b>All groups with role set count</b>
‎‎┃ ‏<code>{gp_set_count}</code>
┗
‏Made in {gp}
            '''
    template_inline = '''
‎┏ <b>Name</b>
‎┃ {name}
‎┣ <b>User Type</b> <a href="https://t.me/lupine_guys/32">❓</a>
‎‎┃ <code>{type}</code>
‎┣ <b>Ranks</b>
‎‎┃ <code>{ranks}</code>
‎┣ <b>All roles set</b>
‎‎┃ <code>{set}</code>
‎┣ <b>All roles set in this group</b>
‎‎┃ ‏<code>{gp_set}</code>
‎┣ <b>All groups with role set count</b>
‎‎┃ ‏<code>{gp_set_count}</code>
┗
‏Made in {gp}
            '''
    no_use = "It seems that you never used me😐😂"


class Gpstate:
    template = '''
┏ ɢʀᴏᴜᴘ ɴᴀᴍᴇ 
┃ [{}](tg://user?id={})
┣ ᴄᴏᴜɴᴛ ᴏғ ɢᴀᴍᴇs
┃‎ `{}`
┣ ᴄᴏᴜɴᴛ ᴏғ ʀᴏʟᴇs 
┃‎ `{}`
┣ ᴄᴏᴜɴᴛ ᴏғ ᴘʟᴀʏᴇʀs
┃‎ `{}`
┗'''
    not_used = "It seems that you never used me...\nYou can save your games with /up"


class Svu:
    inactive = Sn.inactive
    wur = "‎{} What's your role?"
    look_roles = "See Whats these {} players roles"
    good_guys = "Good Guys, all roles set😅"
    one_time = "You can ask for role once per night"


class Mypanel:
    welcome_select = 'Welcome to the emoji panel!\nPlease select a section\n'
    quit = "Exit"
    sent_pv = "Emoji was panel sent to your private chat"
    start_pv = "Start the bot in private first"
    panel_close = "Panel closed"
    group = "Group"
    pub = "Public"
    don = "Donator"
    back = "Back"
    panel_section = "Welcome to {} section.\nSelect your favourite emoji"


class Mostroles:
    all_groups = "All groups"
    most_header = "Most roles since {} days ago in {}\n"
    no_role = "No roles saved since {} days ago!"
    pv_most_header = "Your most roles since {} days ago:\n"
    which = "Which role are you interested in to see?"
    panel_pv = "Panel was sent to your PV!"
    start_first = "Start me in Pv first"
    no_role_pv = "No roles saved from you since {} days ago!"
    no_role_det = "No {} saved since 7 days ago!"
    most_header_det = "Most {} since 7 days ago in {}\n"
    back_list = "Return to role list"


class Mostvotes:
    in_the = "in "
    voted = "<b>↳ Most {mention} votes since {days} ago {where}\n</b>"
    no_vote = "<b>↳ No votes saved from {mention} since {days} ago {where}\n\n</b>"
    votes = "<b>↳ Most votes to {mention} since {days} ago {where}\n</b>"
    no_votes = "<b>↳ No one votes to {mention} since {days} ago {where}\n\n</b>"


class Setnext:
    next_saved = "Nextgame message saved!"
    rep = "Reply to message to set it as Nextgame message"
    admin = "This command is for admins"
    setst = "<b>Set your Nextgame message using /set_next command</b>"


class Myafk:
    header = "‎{} afks since {} days ago\n"
    no_afk = "‎No afks found from since {} days ago"


class SetLang:
    lang_set = "Language changed to English🇺🇸"
    not_admin = "You're not an admin"
