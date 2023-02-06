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
