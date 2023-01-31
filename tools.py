import os
import shutil


def hard_link(src, dst):
    if not os.path.exists(src):
        return None
    dst = dst.strip()
    dst = dst.rstrip("/")
    if not os.path.exists(dst):
        os.makedirs(dst)
    basename = os.path.basename(src)
    dst = f"{dst}/{basename}"
    if os.path.isdir(src):
        shutil.copytree(src, dst, copy_function=os.link)
    if os.path.isfile(src):
        os.link(src, dst)
