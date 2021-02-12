from emoji import UNICODE_EMOJI

'''
TGWerewolf python lib
Written by @Arminshhhh
ALL rights reserved :D
'''


class WWPlayer:
    def __init__(self, text_line, user_id=None):
        self._text_line = text_line
        self._name_split = self._text_line.split(':')
        self.player_name = ':'.join(self._name_split[:-1])
        self.user_id = user_id
        self.player_id = user_id
        self._player_info = self._name_split[-1]
        self._player_info_split = self._player_info.split('-')
        self.player_state = self._player_info_split[0][:-1]
        self.player_game_result = 'برنده' if 'برنده' in self._player_info_split[1] else 'بازنده'
        self.player_role = self._player_info_split[1].replace('برنده', '').replace('بازنده', '')

    def __repr__(self):
        return f'<{self.player_name if not self.user_id else self.user_id} WWPlayer Object>'

    def is_winner(self):
        return self.player_game_result == 'برنده'

    def is_loser(self):
        return not self.is_winner()

    def is_alive(self):
        return 'زنده' in self.player_state

    def is_dead(self):
        return not self.is_alive()

    def is_lover(self):
        return '❤️' in self.role_emoji()

    def state_emoji(self):
        return '‍'.join(c for c in self.player_state if c in UNICODE_EMOJI)

    def role_emoji(self):
        return '‍'.join(c for c in self.player_role if c in UNICODE_EMOJI)

    def role_without_emoji(self):
        return ''.join(c for c in self.player_role if c not in UNICODE_EMOJI)


class WWGame:
    message_objects = []
    try:
        from pyrogram import Message as pyrogram_Message
        message_objects.append(pyrogram_Message)
    except ImportError:
        pass
    try:
        from telegram import Message as telegram_Message
        message_objects.append(telegram_Message)
    except ImportError:
        pass
    try:
        from telebot import Message as telebot_Message
        message_objects.append(telebot_Message)
    except ImportError:
        pass

    def __init__(self, game_message):
        for message_object in self.message_objects:
            if isinstance(game_message, message_object):
                game_text = game_message.text
                players_ids = [ent.user.id for ent in game_message.entities if ent.user]
                break
        else:
            game_text = game_message
            players_ids = None

        self.__game_text = game_text
        self._game_text_split = game_text.split('\n')
        self._game_text_first_line = self._game_text_split[0].split()
        self.all_players_count = int(self._game_text_first_line[5])
        self.alive_players_count = int(self._game_text_first_line[3])
        self.dead_players_count = self.all_players_count - self.alive_players_count
        self._players = self._game_text_split[1:-3]
        if players_ids:
            self.players = [WWPlayer(line, players_ids[i]) for i, line in enumerate(self._players)]
        else:
            self.players = [WWPlayer(line) for line in self._players]

    def __repr__(self):
        return f'<{self.all_players_count} Players Werwolf Game Object>'

    def iter_players(self):
        for player in self.players:
            yield player

    def game_time(self, timestamp=True):
        if timestamp:
            return self._game_text_split[-1][-8:]
        else:
            from datetime import timedelta
            time = self._game_text_split[-1][-8:]
            hours, minutes, seconds = time.split(':')
            return timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds))

    def winner_team(self):
        roosta, ferghe, gorgs, ghatel, atish, monaf, bitim = [], [], [], [], [], [], []
        game_roles = {0: roosta, 1: ferghe, 2: gorgs, 3: ghatel, 4: atish, 5: monaf}
        all_winners = []
        for player in self.iter_players():
            role_indexes = {'فرقه': 1, 'قاتل': 3, 'آتش زن': 4, 'گرگ': 2, 'جادوگر': 2, 'منافق': 5, 'دزد': 6, 'همزاد': 6}
            for ww_role in role_indexes:
                if ww_role in player.player_role and 'نما' not in player.player_role:
                    game_roles[role_indexes[ww_role]].append(player.is_winner())
                    break
            else:
                game_roles[0].append(player.is_winner())
            if player.is_winner():
                all_winners.append(True)
        for team in game_roles:
            if all(game_roles[team]) and game_roles[team]:
                if not any([any(game_roles[i]) for i in game_roles if game_roles[i] != game_roles[team]]):
                    return {0: 'روستاییا👱', 1: 'فرقه گراها👤', 2: 'گرگ ها🐺', 3: 'قاتل زنجیره ای🔪', 4: 'آتش زن🔥',
                            5: 'منافق👺'}[team]
        else:
            if len(all_winners) == 2:
                return 'لاورا💞'
        return 'بدون برنده😞'

    def game_winners(self):
        return [player for player in self.iter_players() if player.is_winner()]

    def game_winners_count(self):
        return len(self.game_winners())

    def game_losers(self):
        return [player for player in self.iter_players() if player.is_loser()]

    def game_losers_count(self):
        return len(self.game_losers())

    def __lt__(self, other):
        return self.all_players_count < other.all_players_count


roles_by_emoji = {'👱': {'role_title': 'روستایی', 'role_id': 1}, '🐺': {'role_title': 'گرگینه', 'role_id': 2},
                  '🍻': {'role_title': 'مست', 'role_id': 3}, '👳': {'role_title': 'پیشگو', 'role_id': 4},
                  '😾': {'role_title': 'نفرین شده', 'role_id': 5}, '💋': {'role_title': 'فاحشه', 'role_id': 6},
                  '👁': {'role_title': 'ناظر', 'role_id': 7}, '🔫': {'role_title': 'تفنگدار', 'role_id': 8},
                  '🖕': {'role_title': 'خائن', 'role_id': 9}, '👼': {'role_title': 'فرشته نگهبان', 'role_id': 10},
                  '🕵️': {'role_title': 'کاراگاه', 'role_id': 11}, '🙇': {'role_title': 'پیشگوی رزرو', 'role_id': 12},
                  '👤': {'role_title': 'فرقه گرا', 'role_id': 13}, '💂': {'role_title': 'شکارچی', 'role_id': 14},
                  '👶': {'role_title': 'بچه وحشی', 'role_id': 15}, '🃏': {'role_title': 'احمق', 'role_id': 16},
                  '👷': {'role_title': 'فراماسون', 'role_id': 17}, '🎭': {'role_title': 'همزاد', 'role_id': 18},
                  '💘': {'role_title': 'الهه عشق', 'role_id': 19}, '🎯': {'role_title': 'کلانتر', 'role_id': 20},
                  '🔪': {'role_title': 'قاتل زنجیره ای', 'role_id': 21}, '👺': {'role_title': 'منافق', 'role_id': 22},
                  '🎖': {'role_title': 'کدخدا', 'role_id': 23}, '👑': {'role_title': 'شاهزاده', 'role_id': 24},
                  '🔮': {'role_title': 'جادوگر', 'role_id': 25}, '🤕': {'role_title': 'پسر گیج', 'role_id': 26},
                  '⚒': {'role_title': 'آهنگر', 'role_id': 27}, '⚡️': {'role_title': 'گرگ آلفا', 'role_id': 28},
                  '🐶': {'role_title': 'توله گرگ', 'role_id': 29}, '💤': {'role_title': 'خواب گذار', 'role_id': 30},
                  '🌀': {'role_title': 'پیشگوی نگاتیوی', 'role_id': 31},
                  '👱‍🌚': {'role_title': 'گرگ نما', 'role_id': 32}, '🐺🌝': {'role_title': 'گرگ ایکس', 'role_id': 33},
                  '☮️': {'role_title': 'صلح گرا', 'role_id': 34}, '📚': {'role_title': 'ریش سفید', 'role_id': 35},
                  '😈': {'role_title': 'دزد', 'role_id': 36}, '🤯': {'role_title': 'دردسرساز', 'role_id': 37},
                  '👨‍🔬': {'role_title': 'شیمیدان', 'role_id': 38},
                  '🐺☃️': {'role_title': 'گرگ برفی', 'role_id': 39}, '☠️': {'role_title': 'گورکن', 'role_id': 40},
                  '🔥': {'role_title': 'آتش زن', 'role_id': 41}, '🦅': {'role_title': 'رمال', 'role_id': 42}}
