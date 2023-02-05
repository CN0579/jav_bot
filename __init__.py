from .sql import *
from .upgrade import *
from .download import *
from .scraper import *
from .tools import *
from .event import *
from .command import *

create_database()
create_download_record_table()
create_actor_table()
if not os.path.exists(torrent_folder):
    os.mkdir(torrent_folder)
