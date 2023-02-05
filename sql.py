import datetime
import os
import sqlite3
from sqlite3 import OperationalError
import logging

_LOGGER = logging.getLogger(__name__)

plugin_folder = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
db_path = f'{plugin_folder}/jav_bot_db/jp_study.db'
db_folder = f'{plugin_folder}/jav_bot_db'


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def create_database():
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
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
        _LOGGER.info("create chapter table success")
        return True
    except OperationalError as o:
        _LOGGER.error(str(o))
        pass
        if str(o) == "table chapter already exists":
            return True
        return False
    except Exception as e:
        _LOGGER.error(str(e))
        return False
    finally:
        cur.close()
        conn.close()


def create_download_record_table():
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        sql = """CREATE TABLE download_record (
                    id integer primary key autoincrement,
                    torrent_name varchar(255) not null,
                    torrent_hash varchar(255) not null,
                    save_path varchar(255) not null,
                    content_path varchar(255) not null,
                    download_status integer not null ,
                    create_time integer,
                    update_time integer
                );"""
        cur.execute(sql)
        _LOGGER.info("create download_record table success")
        return True
    except OperationalError as o:
        _LOGGER.error(str(o))
        pass
        if str(o) == "table download_record already exists":
            return True
        return False
    except Exception as e:
        _LOGGER.error(str(e))
        return False
    finally:
        cur.close()
        conn.close()


def create_actor_table():
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        sql = """CREATE TABLE actor (
                    id integer primary key autoincrement,
                    actor_name varchar(255) not null,
                    actor_url varchar(255) not null,
                    start_date varchar(255) not null
                );"""
        cur.execute(sql)
        _LOGGER.info("create actor table success")
        return True
    except OperationalError as o:
        _LOGGER.error(str(o))
        pass
        if str(o) == "table actor already exists":
            return True
        return False
    except Exception as e:
        _LOGGER.error(str(e))
        return False
    finally:
        cur.close()
        conn.close()


def get_actor_by_url(actor_url):
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    chapter = None
    try:
        sql = f"select * from actor where actor_url = '{actor_url}'"
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


def update_actor(id, start_date):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        update_sql = f"update actor set start_date = '{start_date}' where id = {id}"
        cur.execute(update_sql)
        conn.commit()
    except Exception as e:
        _LOGGER.error(str(e))
    finally:
        cur.close()
        conn.close()


def list_actor():
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    chapters = []
    try:
        sql = f"select * from actor"
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


def save_actor(data):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    actor_name = data['actor_name']
    actor_url = data['actor_url']
    start_date = data['start_date']
    try:
        insert_sql = f"insert into actor(actor_name,actor_url,start_date) " \
                     f"values" \
                     f" ('{actor_name}','{actor_url}','{start_date}')"
        cur.execute(insert_sql)
        conn.commit()
    except Exception as e:
        _LOGGER.error(str(e))
    finally:
        cur.close()
        conn.close()


def delete_actor(ids):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        delete_sql = f"delete from  actor where id in ({ids})"
        cur.execute(delete_sql)
        conn.commit()
    except Exception as e:
        _LOGGER.error(str(e))
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


def delete_chapter(ids):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        delete_sql = f"delete from  chapter where id in ({ids})"
        cur.execute(delete_sql)
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


def list_downloading_record():
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    download_records = []
    try:
        sql = f"select * from download_record where download_status = 0"
        cur.execute(sql)
        download_records = cur.fetchall()
        conn.commit()
    except Exception as e:
        _LOGGER.error(str(e))
        return None
    finally:
        cur.close()
        conn.close()
        return download_records


def get_download_record_by(torrent_hash: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    download_record = None
    try:
        sql = f"select * from download_record where torrent_hash = '{torrent_hash}'"
        cur.execute(sql)
        download_record = cur.fetchone()
        conn.commit()
    except Exception as e:
        _LOGGER.error(str(e))
        return None
    finally:
        cur.close()
        conn.close()
        return download_record


def save_download_record(data):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    torrent_name = data.name
    torrent_hash = data.hash
    save_path = data.save_path
    content_path = data.content_path
    create_time = int(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    try:
        insert_sql = f"insert into download_record(torrent_name,torrent_hash,save_path,content_path,download_status,create_time) " \
                     f"values" \
                     f" ('{torrent_name}','{torrent_hash}','{save_path}','{content_path}',0,{create_time})"
        cur.execute(insert_sql)
        conn.commit()
    except Exception as e:
        _LOGGER.error(str(e))
    finally:
        cur.close()
        conn.close()


def update_download_record(torrent_hash):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    update_time = int(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    try:
        update_sql = f"update download_record set download_status=1,update_time = {update_time} where torrent_hash = '{torrent_hash}'"
        cur.execute(update_sql)
        conn.commit()
    except Exception as e:
        _LOGGER.error(str(e))
    finally:
        cur.close()
        conn.close()


create_database()
create_download_record_table()
create_actor_table()
