import datetime
from typing import Dict

from moviebotapi.core.utils import copy_value


class Course:
    id: int
    code: str
    overview: str
    tags: str
    poster_url: str
    banner_url: str
    status: int
    create_time: datetime.datetime
    update_time: datetime.datetime

    def __init__(self, data: Dict):
        copy_value(data, self)


class DownloadRecord:
    id: int
    course_id: int
    torrent_name: str
    torrent_hash: str
    torrent_path: str
    content_path: str
    download_status: int
    create_time: datetime.datetime
    completed_time: datetime.datetime

    def __init__(self, data: Dict):
        copy_value(data, self)


class Teacher:
    id: int
    name: str
    code: str

    def __init__(self, data: Dict):
        copy_value(data, self)
