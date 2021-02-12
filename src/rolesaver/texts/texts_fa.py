title = 'fa'

start = "سلام! برای استفاده از بیشتر قابلیتام منو تو گروه ورولفیتون اد کنین"


class Sn:
    admin_unblock = 'از یه ادمین بخواه تا رفع مسدودیتت بکنه'
    inactive = 'امکان استفاده از این دستور در این گروه غیر فعال است'
    dont_blow = 'فوت نکن'
    amitis_no_role = 'آمیتیس عزیز نقشی نگفتی💜'
    amitis_saved = 'نقشت ثبت شد آمیتیس💜'
    check_youre_dead = 'چک کن ببین انگار مردی'
    check_youre_dead_amitis = 'انگار مردی آمیتیس💜'
    not_in_game = 'تو بازی نیستی ک'
    not_in_game_amitis = 'توی بازی نیستی آمیتیس💜'
    start_a_game = 'بازی ای در جریان نیست\n یدونه شروع کن'


class Up:
    rep_to_bot = 'به لیست بازی ربات ریپلای بزنید'
    used_list = 'این لیست قبلا ثبت شده است'
    good_game = 'بازی خوبی بود'
    list_updated = 'لیست آپدیت شد'
    game_started = 'بازی شروع شد'


class List:
    ch = ['شکارچی :']
    list_empty = 'لیست نقش خالیست'
    dead_list = '💀لیست مرده ها:\n\n'
    no_role = '🙃لیست کاربران بدون نقش:\n\n'
    role_list = '🙂لیست نقش ها:\n\n'


class Dl:
    ok = 'باش'


class Shekar:
    ch_set = '{} شکارچی بازی شد '
    rep_ch = "روی شکارچی این دستور رو باید بزنید"
    only_admins = 'تنها مدیران میتوانند از این دستور استفاده کنن'


class Sv:
    inactive = Sn.inactive
    not_alive = 'این شخص زنده نیست'
    like_this = 'برای ثبت رای باید بعد از دستور شخص مورد نظر رو بگی مانند زیر:\n /sv @username'
    vote_saved = 'رای ثبت شد!'
    only_ch = 'فقط شکارچی میتواند رای ثبت کند'
    no_ch = 'شکارچی ای یافت نشد'


class Vt:
    inactive = Sn.inactive
    say_vote = ["""
رای {}        
        
        
مخالف رای شکار نباشه
                """]
    vote_dead = 'رای ثبت شده مرده'
    whos_vote = "{} رای کیه؟"
    no_ch = Sv.no_ch
    no_vote = 'رای ثبت نشده'
    ch_dead = 'شکار متاسفانه مرده'


class Ev:
    eq_list = 'لیست مساوی کردن رای'
    no_game = ('بازی ای در جریان نیست!', 'کسی بازی نمیکنه که')


class Block:
    ban_before = 'این یتیم و قبلا یکی دیگه بنش کرده ولش کن:('
    banned = 'با موفقیت مسدود شد\n دیگه نمیتونه توی این گروه از هیچ دستوری استفاده کنه'
    go_admin = 'برو به ادمینت بگو بیاد'
    cant = 'میخوای خودتو بلاک کنی؟'


class Unblock:
    unblocked = 'از مسدودیت بیرون اومد'
    good_guy = 'بچه خوبیه مسدود نیسش'
    only_admin = 'من فقط به یه ادمین راجب این موضوع جواب میدم'


class Mystate:
    template = '''
‏┓ <b>نام</b>
┃‏{name}
‏┫  <b>نوع کاربر</b> <a href="https://t.me/lupine_guys/32">❓</a>
┃‏<code>{type}</code>
‏┫  <b>مقام ها</b>
┃‏<code>{ranks}</code>
‏┫  <b>تعداد کل نقش های ثبت کرده</b>
┃‏<code>{set}</code>
‏┫ <b>تعداد نقش های ثبت کرده در این گروه</b>
┃‏<code>{gp_set}</code>
‏┫ <b>تعداد گروه هایی که توشون نقش ثبت کرده</b>
┃‏<code>{gp_set_count}</code>
┛‏
ساخته شده در {gp}
            '''
    template_inline = '''
‏┓ <b>نام</b>
┃‏{name}
‏┫  <b>نوع کاربر</b> <a href="https://t.me/lupine_guys/32">❓</a>
┃‏<code>{type}</code>
‏┫  <b>مقام ها</b>
┃‏<code>{ranks}</code>
‏┫  <b>تعداد کل نقش های ثبت کرده</b>
┃‏<code>{set}</code>
‏┫ <b>تعداد گروه هایی که توشون نقش ثبت کرده</b>
┃‏<code>{gp_set_count}</code>
┛‏
ساخته شده در {gp}
            '''
    no_use = 'به نظر میرسه تاحالا استفاده ای ازم نکردی😐😂'


'‏┃'


class Gpstate:
    template = '''
┓‏ ‏نام گروه
‏┃[{}](tg://user?id={})
‏‏┫ تعداد بازی ها
┃‏`{}`
‏‏┫ تعداد نقش های ثبت شده
‏┃`{}`
‏‏┫ تعداد بازیکنان
‏┃`{}`
┛‏'''
    not_used = 'به نظر میرسه تاحالا بازی ای رو با من ثبت نکردید\n با دستور /up میتونید بازی هاتونو ثبت کنید🙂'


class Svu:
    inactive = Sn.inactive
    wur = "‏{} نقشت چیه؟"
    look_roles = 'ببین نقش این {} نفر چیه'
    good_guys = 'بچه های خوبی دارید همشون نقشاشونو ثبت کردن😅'
    one_time = "شما تنها یک بار در هر روز میتوانید درخواست نقش کنید"


class Mypanel:
    welcome_select = 'به بخش پنل خوش آمدید!\n' + 'لطفا یک بخش را انتخاب کنید.\n'
    quit = 'خروج'
    sent_pv = 'پنل به پیوی شما ارسال شد.'
    start_pv = 'اول من را در پیوی استارت کنید.'
    panel_close = 'پنل بسته شد.'
    group = 'گروهی'
    pub = 'عمومی'
    don = 'حامیان'
    back = 'بازگشت'
    panel_section = 'به بخش ایموجی {} خوش اومدید.\nایموجی مورد نظرتونو انتخاب کنید.'


class Mostroles:
    all_groups = 'تمامی گروه ها'
    most_header = 'بیشترین نقش ها در {} روز گذشته در {}\n'
    no_role = 'در {} روز گذشته هیچ نقشی ثبت نشده!'
    pv_most_header = 'بیشترین نقش های شما در بازی ها در {} روز گذشته:\n'
    which = 'کدوم یکی از نقشها مد نظرته؟'
    panel_pv = 'پنل به پیوی شما ارسال شد!'
    start_first = 'ابتدا بات رو استارت کنید و دوباره دستور رو ارسال کنید'
    no_role_pv = 'در {} روز گذشته هیچ نقشی از شما ثبت نشده!'
    no_role_det = 'در 7 روز گذشته هیچ نقش {} ثبت نشده!'
    most_header_det = 'بیشترین {} ها در 7 روز گذشته در {}\n'
    back_list = 'بازگشت به لیست نقش ها'


class Mostvotes:
    in_the = ' در '
    voted = '<b>↲ بیشترین رای های {mention} در {days} روز گذشته </b>'
    no_vote = '<b>↲ در {days} روز گذشته هیچ رای ای از {mention} {where} ثبت نشده </b>\n\n'
    votes = '<b>↲ بیشترین کسانی که در {days} روز گذشته {where} به {mention} رای دادند </b>\n'
    no_votes = '<b>↲ در {days} روز گذشته هیچ شخصی به {mention} {where} رای نداده!</b>'


class Setnext:
    next_saved = 'پیام نکست شما ثبت شد!'
    rep = 'روی یک پیام ریپلای کنید'
    admin = 'این دستور مخصوص ادمینه'
    setst = '<b>با استفاده از دستور /set_next پیام مورد نظر خودتون رو تنظیم کنید</b>'


class Myafk:
    header = 'تعداد افک های {} از {} روز پیش تاکنون\n'
    no_afk = 'هیچ افکی در {} روز گذشته پیدا نشد!'


class SetLang:
    lang_set = 'زبان به فارسی🇮🇷 تغییر یافت'
    not_admin = "شما ادمین نیستید!"
