import datetime
import sqlite3
from sqlite3 import OperationalError
import logging

_LOGGER = logging.getLogger(__name__)

db_path = '/data/plugins/jav_bot/db/jp_study.db'


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def create_database():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        sql = """CREATE TABLE chapter (
                    id integer primary key autoincrement,
                    chapter_code varchar(15) not null,
                    overview varchar(255),
                    status integer,
                    size varchar(15),
                    download_url varchar(55),
                    download_path varchar(55),
                    create_time integer,
                    update_time integer,
                    img_url varchar(255)
                );"""
        cur.execute(sql)
        print("create table success")
        return True
    except OperationalError as o:
        print(str(o))
        pass
        if str(o) == "table chapter already exists":
            return True
        return False
    except Exception as e:
        print(e)
        return False
    finally:
        cur.close()
        conn.close()


def save_chapter(data):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    code = data['code']
    overview = data['overview']
    img = data['img']
    create_time = int(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    try:
        insert_sql = f"insert into chapter(chapter_code,overview,img_url,status,create_time) " \
                     f"values" \
                     f" ('{code}','{overview}','{img}',0,{create_time})"
        cur.execute(insert_sql)
        conn.commit()
    except Exception as e:
        _LOGGER.error(str(e))
    finally:
        cur.close()
        conn.close()


def get_chapter(code):
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    chapter = None
    try:
        sql = f"select * from chapter where chapter_code = '{code}'"
        cur.execute(sql)
        chapter = cur.fetchone()
        conn.commit()
    except Exception as e:
        _LOGGER.error(str(e))
        return None
    finally:
        cur.close()
        conn.close()
        return chapter


def update_chapter(data):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    id = data['id']
    size = data['size']
    download_url = data['download_url']
    download_path = data['download_path']
    update_time = int(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    try:
        update_sql = f"update chapter set status=1,size = '{size}',download_url = '{download_url}'," \
                     f"download_path = '{download_path}',update_time = {update_time} where id = {id}"
        cur.execute(update_sql)
        conn.commit()
    except Exception as e:
        _LOGGER.error(str(e))
    finally:
        cur.close()
        conn.close()


def list_un_download_chapter():
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    chapters = []
    try:
        sql = f"select * from chapter where status = 0"
        cur.execute(sql)
        chapters = cur.fetchall()
        conn.commit()
    except Exception as e:
        _LOGGER.error(str(e))
        return []
    finally:
        cur.close()
        conn.close()
        return chapters


if __name__ == '__main__':
    chapter = get_chapter('ABW-311')
    print(chapter)