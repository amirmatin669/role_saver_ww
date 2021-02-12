import telegram.ext

from . import get_cur


class EmojiManager:
    def validate_gift_code(self, code):
        """check the gift code is exists"""
        res = self.get_emoji_by_code(code)
        if res:
            return True
        return False

    def get_emoji_by_code(self, code):
        conn, cur = get_cur()
        cur.execute('''select emoji_id 
                from v2.emoji_codes 
                where code= %(code)s and emoji_type=1 and owner=0 and disabled_at is null''', {
            'code': code
        })
        res = cur.fetchone()
        if not res:
            return None
        return res[0]

    def assign_emoji_to_user(self, code, user_id):
        """assign emoji to user inside database"""
        emoji_id = self.get_emoji_by_code(code)
        if not emoji_id:
            return False
        try:
            conn, cur = get_cur()
            cur.execute("""insert into v2.members_ranks(user_id, rank_id) values (%(user_id)s, %(emoji_id)s)""", {
                'user_id': user_id,
                'emoji_id': emoji_id
            })
            conn.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def get_random_emoji(self, user_id):
        """ assign random emoji to user and return user emoji """


emoji_manager = EmojiManager()


def emoji_gift_start(update: telegram.Update, context: telegram.ext.CallbackContext):
    """  """
    chat = update.effective_message.chat
    user = update.effective_message.from_user
    args = context.args[0].split('___')
    code = args[1]
    res = emoji_manager.validate_gift_code(code)
    if not res:
        update.effective_message.reply_text('لینک نامعتبر بود =(')
        return
    res = emoji_manager.assign_emoji_to_user(code, user.id)
    if not res:
        update.effective_message.reply_text('مشکلی برای ثبت ایموجی برای شما پیش اومده، بعدا دوباره امتحان کنید')
        return
    update.effective_message.reply_text('با موفقیت ثبت شد، با دستور /mypanel ایموجی های خودتون رو مدیریت کنید')
