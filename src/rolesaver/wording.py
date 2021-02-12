from . import get_cur
from cachetools import TTLCache, cached

cache = TTLCache(1024, 0)


@cached(cache)
def get_from_db(key):
    query = """ select content, send_type  from v2.contents where key = %(key)s """
    conn, cur = get_cur()
    cur.execute(query, {'key': key})
    res = cur.fetchone()
    return res if res else (None, None)
