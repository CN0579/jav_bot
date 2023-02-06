import datetime
import logging
import sqlite3
from sqlite3 import OperationalError

from .models import Course, DownloadRecord, Teacher

_LOGGER = logging.getLogger(__name__)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class DB:
    db_name: str = 'study.db'
    db_path: str = f"/data/db/{db_name}"

    def create_database(self):
        conn = sqlite3.connect(self.db_path)
        conn.close()

    def create_table(self, table_name: str, sql: str):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        try:
            cur.execute(sql)
            _LOGGER.info(f"create {table_name} table success")
        except OperationalError as o:
            _LOGGER.error(str(o))
        except Exception as e:
            _LOGGER.error(str(e))
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = dict_factory
        return conn


class CourseDB:

    @staticmethod
    def create_table():
        create_sql: str = """CREATE TABLE course (
                                        id integer primary key autoincrement,
                                        code varchar(15) not null,
                                        overview varchar(255),
                                        tags varchar(255),
                                        poster_url varchar(255),
                                        banner_url varchar(255),
                                        status integer,
                                        create_time datetime,
                                        update_time datetime
                                    );"""
        DB.create_table('course', create_sql)

    @staticmethod
    def get_by_id(course_id: int):
        sql = f"select * from course where id = {course_id}"
        conn = DB.get_connect()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            row = cur.fetchone()
            course = Course(row)
            conn.commit()
            return course
        except Exception as e:
            _LOGGER.error(str(e))
            return None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def list(status: int = None):
        sql = f"select * from course"
        if status:
            sql = f"select * from course where status = {status}"
        conn = DB.get_connect()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            rows = cur.fetchall()
            courses = [Course(row) for row in rows]
            conn.commit()
            return courses
        except Exception as e:
            _LOGGER.error(str(e))
            return None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_by_code(code: str):
        sql = f"select * from course where code = '{code}'"
        conn = DB.get_connect()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            row = cur.fetchone()
            course = Course(row)
            conn.commit()
            return course
        except Exception as e:
            _LOGGER.error(str(e))
            return None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def update(course: Course):
        sql = f"""update course set 
              overview = '{course.overview}',
              tags = '{course.tags}',
              poster_url = '{course.poster_url}',
              banner_url = '{course.banner_url}',
              status = '{course.status}',
              update_time = '{course.update_time}'
              where id = {course.id}
              """
        conn = DB.get_connect()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            conn.commit()
            return True
        except Exception as e:
            _LOGGER.error(str(e))
            return False
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def insert(course: Course):
        create_time = datetime.datetime.now()
        sql = f"""insert into coursr(code,overview,tags,poster_url,banner_url,status,create_time) values 
                ('{course.code}','{course.overview}','{course.tags}','{course.poster_url}','{course.banner_url}',{course.status},'{create_time}')
                """
        conn = DB.get_connect()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            conn.commit()
            course = CourseDB.get_by_code(course.code)
            return course
        except Exception as e:
            _LOGGER.error(str(e))
            return None
        finally:
            cur.close()
            conn.close()


class TeacherDB:

    @staticmethod
    def create_table():
        create_sql: str = """CREATE TABLE teacher (
                                        id integer primary key autoincrement,
                                        name varchar(15) not null,
                                        code varchar(255) not null                              
                                    );"""
        DB.create_table('teacher', create_sql)

    @staticmethod
    def get_by_id(teacher_id: int):
        sql = f"select * from teacher where id = {teacher_id}"
        conn = DB.get_connect()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            row = cur.fetchone()
            teacher = Teacher(row)
            conn.commit()
            return teacher
        except Exception as e:
            _LOGGER.error(str(e))
            return None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def list(name: str = None):
        sql = f"select * from teacher"
        if name:
            sql = f"select * from teacher where name like '%{name}%'"
        conn = DB.get_connect()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            rows = cur.fetchall()
            teachers = [Teacher(row) for row in rows]
            conn.commit()
            return teachers
        except Exception as e:
            _LOGGER.error(str(e))
            return None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_by_code(code: str):
        sql = f"select * from teacher where webpage = '{code}'"
        conn = DB.get_connect()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            row = cur.fetchone()
            teacher = Teacher(row)
            conn.commit()
            return teacher
        except Exception as e:
            _LOGGER.error(str(e))
            return None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def update(teacher: Teacher):
        sql = f"""update teacher set 
              name = '{teacher.name}',
              code = '{teacher.code}'
              where id = {teacher.id}
              """
        conn = DB.get_connect()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            conn.commit()
            return True
        except Exception as e:
            _LOGGER.error(str(e))
            return False
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def insert(teacher: Teacher):
        sql = f"""insert into teacher(name,code) values 
                ('{teacher.name}','{teacher.code}')
                """
        conn = DB.get_connect()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            conn.commit()
            teacher = TeacherDB.get_by_code(teacher.code)
            return teacher
        except Exception as e:
            _LOGGER.error(str(e))
            return None
        finally:
            cur.close()
            conn.close()


class DownloadRecordDB:
    @staticmethod
    def create_table():
        create_sql: str = """CREATE TABLE download_record (
                                           id integer primary key autoincrement,
                                           course_id integer not null,
                                           torrent_name varchar(255),
                                           torrent_hash varchar(255),
                                           torrent_path varchar(255),
                                           content_path varchar(255),
                                           download_status integer,
                                           create_time datetime,
                                           completed_time datetime
                                       );"""
        DB.create_table('download_record', create_sql)

    @staticmethod
    def get_by_id(download_record_id: int):
        sql = f"select * from download_record where id = {download_record_id}"
        conn = DB.get_connect()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            row = cur.fetchone()
            download_record = DownloadRecord(row)
            conn.commit()
            return download_record
        except Exception as e:
            _LOGGER.error(str(e))
            return None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def list(download_status: int = None):
        sql = f"select * from download_record"
        if download_status:
            sql = f"select * from download_record where download_status = {download_status}"
        conn = DB.get_connect()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            rows = cur.fetchall()
            download_records = [DownloadRecord(row) for row in rows]
            conn.commit()
            return download_records
        except Exception as e:
            _LOGGER.error(str(e))
            return None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_by_course_id(course_id: int):
        sql = f"select * from download_record where course_id = {course_id}"
        conn = DB.get_connect()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            rows = cur.fetchall()
            download_records = [DownloadRecord(row) for row in rows]
            conn.commit()
            return download_records
        except Exception as e:
            _LOGGER.error(str(e))
            return None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_by_torrent_hash(torrent_hash: str):
        sql = f"select * from download_record where torrent_hash = '{torrent_hash}'"
        conn = DB.get_connect()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            row = cur.fetchone()
            download_record = DownloadRecord(row)
            conn.commit()
            return download_record
        except Exception as e:
            _LOGGER.error(str(e))
            return None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def update(download_record: DownloadRecord):
        sql = f"""update download_record set 
                 download_status = '{download_record.status}',
                 completed_time = '{download_record.completed_time}'
                 where id = {download_record.id}
                 """
        conn = DB.get_connect()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            conn.commit()
            return True
        except Exception as e:
            _LOGGER.error(str(e))
            return False
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def insert(download_record: DownloadRecord):
        create_time = datetime.datetime.now()
        sql = f"""insert into download_record(course_id,torrent_name,torrent_hash,torrent_path,content_path,download_status,create_time) values 
                   ({download_record.course_id},'{download_record.torrent_name}','{download_record.torrent_hash}',
                   '{download_record.torrent_path}','{download_record.content_path}',{download_record.download_status},'{create_time}')
                   """
        conn = DB.get_connect()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            conn.commit()
            download_record = DownloadRecordDB.get_by_torrent_hash(download_record.torrent_hash)
            return download_record
        except Exception as e:
            _LOGGER.error(str(e))
            return None
        finally:
            cur.close()
            conn.close()
