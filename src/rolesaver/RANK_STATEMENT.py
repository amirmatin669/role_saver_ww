import psycopg2
import psycopg2.extensions
import telegram
from os import getenv
from dotenv import load_dotenv
from . import get_cur

load_dotenv()
channel_id = '@lupine_guys'
group_id = -1001461432821


class UserStatus:
    def __init__(self, user):
        self.user = user
        if type(user) == int:
            self.user_id = user
        else:
            self.user_id = user.id
        self.channel_status = self.get_channel_status()
        self.group_status = self.get_group_status()
        self.custom_rank = self.get_custom_rank()
        self.status = self.get_status()
        try:
            # if self.user_id == 120500168:
            #     self.emojis_rank = {0: {'id': 0, 'title': 'someone', 'emoji': '🌙', 'parent_id': -2}}
            #     return
            if self.group_status >= 2:
                self.emojis_rank = {12: {'id': 12, 'title': 'عضو مجموعه', 'emoji': '💜', 'parent_id': -1}}
                return
            elif self.channel_status == 1:
                self.emojis_rank = {2: {'id': 2, 'title': 'کاربر ویژه', 'emoji': '🔥', 'parent_id': -2}}
                return
            self.emojis_rank = self.emojis_rank = {1: {'id': 1, 'title': 'کاربر عادی', 'emoji': '🧊', 'parent_id': -2}}
            return
        except:
            self.emojis_rank = {1: {'id': 1, 'title': 'کاربر عادی', 'emoji': '🧊', 'parent_id': -2}}

    def get_channel_status(self):
        try:
            response = bot.get_chat_member(channel_id, self.user_id)
            if response['status'] == 'member':
                return 1
            elif response['status'] == 'administrator':
                return 2
            elif response['status'] == 'creator':
                return 3
            else:
                return 0
        except:
            return 0

    def get_group_status(self):
        try:
            response = bot.get_chat_member(group_id, self.user_id)
            if response['status'] == 'member':
                return 1
            elif response['status'] == 'administrator':
                return 2
            elif response['status'] == 'creator':
                return 3
            else:
                return 0
        except:
            return 0

    def get_custom_rank(self):
        query = """
        select rank
        from v1.users_custom_rank
        WHERE user_id = %s
        """
        conn, cur = get_cur()
        try:
            cur.execute(query, (self.user_id,))
            res = cur.fetchone()
            cur.close()
            if not res:
                return ''
            return res[0]

        except Exception as e:
            print(e)
            return ''

    def get_custom_emojis(self):
        query = """
        select group_emoji, main_emoji, donor_emoji
        from v2.selected_emojies_by_user
        WHERE user_id = %s 
        """
        conn, cur = get_cur()
        try:
            cur.execute(query, (self.user_id,))
            res = cur.fetchone()
            cur.close()
            if not res:
                return [None, None, None]
            return res

        except Exception as e:
            print(e)
            return [None, None, None]

    def get_status(self):
        if self.custom_rank:
            return self.custom_rank
        elif self.channel_status == 1 and self.group_status == 1:
            return 'کاربر ویژه🔥'
        elif self.channel_status == 2:
            return 'مدیر مجموعه ☢️'
        elif self.group_status == 2:
            return 'هدایتگر مجموعه 💠'
        elif self.channel_status == 3:
            return 'مالک مجموعه 🐾'
        else:
            return 'کاربر عادی'

    def set_emojies_rank(self, emojis: dict):
        self.emojis_rank = emojis

    def get_emojies_rank(self):
        """return [level emoji | main emoji | donor emoji]"""
        emojies = []
        level_emoji_dict = {emoji: self.emojis_rank[emoji] for emoji in self.emojis_rank if
                            self.emojis_rank[emoji]['parent_id'] == -1}
        main_emoji_dict = {emoji: self.emojis_rank[emoji] for emoji in self.emojis_rank if
                           self.emojis_rank[emoji]['parent_id'] == -2}
        donor_emoji_dict = {emoji: self.emojis_rank[emoji] for emoji in self.emojis_rank if
                            self.emojis_rank[emoji]['parent_id'] == -3}
        level, main, donor = self.get_custom_emojis()
        if level and level in level_emoji_dict:
            em = level_emoji_dict.get(level, level_emoji_dict[sorted(level_emoji_dict.keys())[-1]])
            emojies.append(em['emoji'])
        elif level_emoji_dict:
            em = sorted(level_emoji_dict.keys())[-1]
            emojies.append(level_emoji_dict[em]['emoji'])

        if main and main in main_emoji_dict:
            em = main_emoji_dict.get(main, main_emoji_dict[sorted(main_emoji_dict.keys())[-1]])
            emojies.append(em['emoji'])
        elif main_emoji_dict:
            em = sorted(main_emoji_dict.keys())[-1]
            emojies.append(main_emoji_dict[em]['emoji'])

        if donor and donor in donor_emoji_dict:
            em = donor_emoji_dict.get(donor, donor_emoji_dict[sorted(donor_emoji_dict.keys())[-1]])
            emojies.append(em['emoji'])
        elif donor_emoji_dict:
            em = sorted(donor_emoji_dict.keys())[-1]
            emojies.append(donor_emoji_dict[em]['emoji'])
        return emojies

    def get_all_emoji_ranks(self):
        """return a list of all emojies user had"""
        return [self.emojis_rank[em]['emoji'] for em in self.emojis_rank]


lupine_guy_bot_token = getenv("TG_LUPINE_GUY", '')
bot = telegram.Bot(token=lupine_guy_bot_token)

status = UserStatus(638994540)
print(status.__dict__)
# bot = u.bot
