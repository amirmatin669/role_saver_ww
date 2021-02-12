title = 'fb'
from random import choices

start = "سلام کصخل! برای استفاده از قابلیتام منو تو اون گپای کیریت اد کن اینجا گهای زیادی ندارم ک بدم بخوری"
koses = ('کصمغز', 'کیری', 'کصخل', 'کصمشنگ', 'کصپرت', 'کص گلابی', 'کون گلابی', 'خواجه', 'کونی', 'جنده', 'کیر تو دهن',
         'جقی', 'لاشی', 'هزره', 'جنده پولی', 'بی عقل', 'کسخل', 'کون سفید', 'کون قشنگ', 'ساکر', 'جنده مجانی', 'جیندا',
         'کون تاغار', 'زاخار', 'کونکش', 'احمق', 'بیشعور', 'کصخل سه جانبه', 'حشری', 'کصمغز حشری', 'کص ندیده',
         'کصلیس', 'خایه مال', 'کیر پلاسیده', 'کون چروک', 'ممه جوشی', 'ممه خور', 'بیشرف', 'بی فرهنگ', 'جاکش',
         'آشغال', 'گنده گوز', 'دهن سرویس', 'اسکل', 'کله کیری')
get_fohsh_vst = lambda t: choices([t.format(i if i[-1] not in ['ه', 'ی'] else (i + ' ا')) for i in koses], k=6)
get_fohsh = lambda t: choices([t.format(i) for i in koses], k=6)
get_fohsh_jam = lambda t: choices([t.format(i if i[-1] != 'ه' else (i + ' ه')) for i in koses], k=6)


class Sn:
    admin_unblock = ('بلاکی کصخل:/ بمال تا یه ادمین آنبلاکت کنه', 'بلاکی کصخل:/ بلیس تا یه ادمین آنبلاکت کنه')
    inactive = ['این قابلیت اینجا خاموشه کیر شدی',
                'سیکتیر این قابلیت اینجا کار نمیکنه😐🖕 ', 'کصمغز اول ستینگ گپو چک کن الانم سیکتو بزن']
    dont_blow = (
    'کص نگو نقشتو بگو', 'کصکش نقش نداری دستورو خالی میزنی؟', 'کیری مگه من مسخرتم نقشتو بگو', 'کیرم توت نقش کوش')
    amitis_no_role = 'آمیتیس خنگ نقشی نگفتی:/💜'
    amitis_saved = 'نقشت ثبت شد آمیتیس خنگ:/💜'
    check_youre_dead = ('تو ک مردی پس کص نگو', 'مردی کص نگو', 'وقتی مردی تز نده', 'کیری خان مردی مث اینکه', 'پلشت مردی',
                        'مگه مرتضی پاشایی ای کیری؟')
    check_youre_dead_amitis = 'انگار مردی آمیتیس خنگ:/💜'
    not_in_game = ['تو بازی نیستی کصمغز', 'تو بازی نیستی احمق', 'تو بازی نیستی تز نده',
                   'تو بازی نیستی گه نخور', 'ناموسا یا تو کوری یا من:/ تو بازی ای؟'
                   ] + get_fohsh('{} تو بازی نیستی گه میخوری') + get_fohsh('تو بازی نیستی {}')
    not_in_game_amitis = 'توی بازی نیستی آمیتیس خنگ:/💜'
    start_a_game = ('نگا نگا کیرم تو مغزت احمق مگه تو بازی میبینی؟ کصخل ی وری استارت کن بازیو',
                    'چیزی میکشی؟ بازی در جریان نیس استارت کن بازیو کصمشنگ',
                    'کص نگو وقتی بازی در جریان نیست',
                    'ناموسا وقتی بازی در جریان نیست این چی گه میخوره')


class Up:
    rep_to_bot = ('کصخل خودتی رو لیست ربات ریپلای کن', 'برو باو این بات بازی نیس رو بات بازی ریپلای کن')
    used_list = ('برو خودتو کیر کن این لیست قبلا ثبت شده', 'کصکش نمیتونی منو کیر کنی این لیست قبلا ثبت شده')
    good_game = ('کیرم تو این بازی', 'ورولف خز شده ناموسا', 'کیرم تو این بازیتون', 'بازی کیری ای بود')
    list_updated = ('لیست آپدیت شد (بکیرتون)', 'لیست آپدیت شد (بتخمتون)', 'لیست آپدیت شد (به ممه هاتون)',
                    'اوکی ولی کیرم تو بازیکنای این لیست که آپدیت شد', 'خا لیست آپدیت شد', 'لیست کیری آپدیت شد',
                    'لیست کیر شد چیز ببخشید آپدیت شد')
    game_started = ('بازی شروع شد ( بکیرتون)', 'بازی شروع شد (کیرم تو این بازی)')


class List:
    ch = get_fohsh('شکارچی {} :')
    list_empty = get_fohsh_vst('هیچ {}ی نقش ثبت نکرده')
    dead_list = get_fohsh('💀لیست مرده های {}:\n\n')
    no_role = get_fohsh('🙃لیست {} های بدون نقش:\n\n')
    role_list = get_fohsh('🙂لیست نقش این {} ها:\n\n')


class Dl:
    ok = get_fohsh('باشه {}')


class Sv:
    inactive = Sn.inactive
    not_alive = get_fohsh('این {} زنده نیست')
    like_this = get_fohsh('مرتیکه {} برای ثبت رای باید بعد از دستور شخص مورد نظر رو بگی مانند زیر:\n /sv @username')
    vote_saved = 'بکیرم ولی اوکی رای ثبت شد!'
    only_ch = ('فقط شکارچی کیرش کلفته و میتونه رای ثبت کنه', 'واسه رای شکار نمال',
               'سیک مگه شکاری؟', 'تو کیرت اندازه شکار کلفت نیست', 'نمال دستور برای شکاره')
    no_ch = get_fohsh('کسی شکار نیس ک {}') + ['شکار نگاییدم (نمیبینم)', 'کی شکاره؟ :/', 'کیرم توتون ک نگفتین کی شکاره']


class Vt:
    inactive = Sn.inactive
    say_vote_ = get_fohsh_jam("""

مخالف رای شکار نباشه {}ا""")
    say_vote = ['رای {}' + i for i in say_vote_]
    vote_dead = ('این شکار هم ک کصخله رایش مرده', 'رای اون شکار کصخل مرده', 'این کیری ک مرده')
    whos_vote = "{} رای کیه مرتیکه؟"
    no_ch = Sv.no_ch
    no_vote = ('رای ثبت نشده باو', 'رای ثبت نشده گه نخور')
    ch_dead = ('شکار بگا رفته', 'شکار سیک شده', 'شکار کیر خورده(مرده)')


class Ev:
    eq_list = get_fohsh_jam('لیست مساوی کردن رای برای شما {}ا')
    no_game = Sn.start_a_game


class Block:
    ban_before = get_fohsh('این {} و قبلا یکی دیگه بنش کرده ازش بکش بیرون')
    banned = ('بگا رفت دیگه نمیتونه تو این گروه هیچ گهی بخوره', 'حله دست و پاش بسته شد حالا لختش کنین بکنیمش')
    go_admin = get_fohsh('برو به یه ادمین کیرکلفت بگو بیاد {}') + get_fohsh('سیکتیر باو {}') + get_fohsh('نمال {}') \
               + get_fohsh('گوه بزرگتر از دهنت نخور {}') + get_fohsh(
        ' متاسفانه  باید بگم کیر شدی چون فقط ادمینا میتونن از این دستور استفاده کنن {}')
    cant = get_fohsh('میخوای خودتو بلاک کنی {}؟') + ['بمولا ک تو کصخلی', 'کیرم تو مغزت']


class Unblock:
    unblocked = ('کیر از توش بیرون کشیده شد', 'با موفقیت کیر رو از تو کونش کشیدی بیرون')
    good_guy = ['کونیه مسدود نیس', 'مسدود نیس این ک'] + get_fohsh('مگه این مسدوده ک گو میخوری {}')
    only_admin = Block.go_admin


class Shekar:
    ch_set = '{} شکارچی این بازی کیری شد'
    rep_ch = get_fohsh("روی اون شکارچی {} باید این دستورو بزنی")
    only_admins = Block.go_admin


class Mystate:
    template = '''
‏┓ <b>نام کیری</b>
┃‏{name}
‏┫  <b>نوع کاربر کصکش</b> <a href="https://t.me/lupine_guys/32">❓</a>
┃‏<code>{type}</code>
‏┫  <b>مقام های کصشر</b>
┃‏<code>{ranks}</code>
‏┫  <b>تعداد کل نقش های تخمی ثبت کرده</b>
┃‏<code>{set}</code>
‏┫ <b>تعداد نقش های ثبت کرده در این گروه</b>
┃‏<code>{gp_set}</code>
‏┫ <b>تعداد گروه هایی که توشون نقش ثبت کرده</b>
┃‏<code>{gp_set_count}</code>
┛‏
ساخته شده در {gp}
            '''
    template_inline = '''
‏┓ <b>نام کیری</b>
┃‏{name}
‏┫  <b>نوع کاربر کصکش</b> <a href="https://t.me/lupine_guys/32">❓</a>
┃‏<code>{type}</code>
‏┫  <b>مقام های کصشر</b>
┃‏<code>{ranks}</code>
‏┫  <b>تعداد کل نقش های تخمی ثبت کرده</b>
┃‏<code>{set}</code>
‏┫ <b>تعداد گروه هایی که توشون نقش ثبت کرده</b>
┃‏<code>{gp_set_count}</code>
┛‏
ساخته شده در {gp}
            '''
    no_use = ['تا حالا واسم نمالیدی', 'تا حالا کیرمو نخوردی', 'نمیدونم تا حالا بهم کون ندادی',
              'کص نگو ازت آماری نیس تا حالا کونی ندادی', 'تا حالا ندیدم ک کونی بدی']


class Gpstate:
    template = '''
┓ نام چرت گروه
┃[{}](tg://user?id={})
┫ تعداد بازی ها
┃`{}`
┫ تعداد نقش های ثبت شده کصشر
┃`{}`
┫ تعداد بازیکنان خایه مال
┃`{}`
┛'''
    not_used = ['ب نظر میرسه تا حالا برام نمالیدین\nبا دستور /up میتونین تا دلتون میخواد برام بمالین',
                'تا حالا تو این گروه خایه هام مالیده نشده'] + get_fohsh_jam('شما {}ا تا حالا باهام ور نرفتین')


class Svu:
    inactive = Sn.inactive
    wur = "{} نقشت چیه؟"
    look_roles = ('ببین نقش این {} کصخل چیه', 'ببین نقش این {}‌ کله کیری چیه')
    good_guys = 'بچه های کونی ای دارید همشون نقشاشونو ثبت کردن'
    one_time = "شما تنها یک بار در هر روز میتوانید برای نقش بقیه بمالید"


class Mypanel:
    welcome_select = 'درسته کیرمم نیستی ولی به بخش پنل خوش اومدی!\n' + 'تیز یه بخشو انتخاب کن حوصله ندارم.\n'
    quit = 'سیک'
    sent_pv = get_fohsh('پنل به پیویت ارسال شد {}')
    start_pv = ('اول پیوی کیرمو استارت کن تا شق شه بکنمت', 'بیا پیوی لخت شو تا بتونم بکنمت',
                'بیا پیوی شورتتو دربیار تا بفرستم برات', 'اول نود بده پیوی ',
                'بیا پیوی بهم ممه بده تا برات بفرستم', 'کون لقت اول استارتم کن',
                'جاکش اول استارتم بکن بعد بیا بگو بکن منو')
    panel_close = 'پنل بگا رفت'
    group = 'گروهی'
    pub = 'عمومی'
    don = 'حامیان'
    back = 'بازگشت(پشت کردن)'
    panel_section = 'ضمن یاداوری این ک کیرمم نیستی به بخش ایموجی {} خوش اومدی.\nایموجی ای ک میخوای باهاش در بقیه بمالی رو انتخاب کن.'


class Mostroles:
    all_groups = 'تمامی گروه های کیری'
    most_header = 'بیشترین نقش ها در {} روز گذشته در {}\n'
    no_role = 'در {} روز گذشته ک جق میزدین هیچ نقش کصشری ثبت نشده'
    pv_most_header = 'بیشترین نقش های شما در بازی های کصشر ورولف در {} روز کیری گذشته:\n'
    which = get_fohsh('کدوم یکی از نقشها مد نظرته {}؟')
    panel_pv = get_fohsh('پنل به پیویت ارسال شد {}')
    start_first = Mypanel.start_pv
    no_role_pv = 'در {} فقط جق میزدی و هیچ نقشی ازت ثبت نشده!'
    no_role_det = 'در 7 روز گذشته ک جق میزدی هیچ نقش {} ثبت نشده!'
    most_header_det = 'بیشترین {} های کصخل در 7 روز گذشته در {}\n'
    back_list = 'بازگشت به لیست تخماتیک نقش ها'


class Mostvotes:
    in_the = ' در '
    voted = '<b>↲ بیشترین رای دادن به قصد کون توسط {mention} در {days} روز گذشته </b>'
    no_vote = '<b>↲ در {days} روز گذشته {mention} قصد کون هیچکسو {where} نکرده</b>\n\n'
    votes = '<b>↲ بیشترین کسانی به قصد کون در {days} روز گذشته {where} به {mention} رای دادند </b>\n'
    no_votes = '<b>↲ در {days} روز گذشته هیچ شخصی قصد کون {mention} {where} رو نکرده!</b>'


class Setnext:
    next_saved = 'پیام کصشر نکست شما ثبت شد!'
    rep = ('روی یه پیام ریپ بزن بی عقل', 'ناموسا ب عقل خودت نمیرسه این دستور رو ریپلای کنی رو یه پیامی کصشری چیزی؟')
    admin = Block.go_admin
    setst = '<b>کصخلا با دستور /set_next یه پیام نکست تنظیم کنین باهاش جق بزنیم</b>'


class Myafk:
    header = 'تعداد افک های {} به دلیل جق از {} روز پیش تاکنون\n'
    no_afk = 'هیچ افکی به دلیل جق در {} روز گذشته پیدا نشد!'


class SetLang:
    lang_set = 'زبان به فارسی بی ادبی🔞🇮🇷 تغییر یافت'
    not_admin = Block.go_admin
