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


def collect_videos(path):
    videos = []
    if os.path.isdir(path):
        for file in os.listdir(path):
            videos.extend(collect_videos(os.path.join(path, file)))
        return videos
    elif os.path.splitext(path)[1].lower() in [
        ".mp4",
        ".avi",
        ".rmvb",
        ".wmv",
        ".mov",
        ".mkv",
        ".webm",
        ".iso",
        ".mpg",
        ".m4v",
    ]:
        return [path]
    else:
        return []


def get_max_size_video(videos):
    max_size = 0
    max_size_video = None
    for path in videos:
        size = os.path.getsize(path)
        if size > max_size:
            max_size = size
            max_size_video = path
    return max_size_video


# 将输入不规范的番号规范化返回
def get_true_code(input_code: str):
    code_list = input_code.split('-')
    code = ''.join(code_list)
    length = len(code)
    index = length - 1
    num = ''
    all_number = '0123456789'
    while index > -1:
        s = code[index]
        if s not in all_number:
            break
        num = s + num
        index = index - 1
    prefix = code[0:index + 1]
    return (prefix + '-' + num).upper()
