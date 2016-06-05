#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : unzip_all.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : 按顺序解压数据文件
# 

import zipfile
from load_parser_config import *


def unzip_files_in_path(zip_path):
    """按时间顺序解压目录中的所有压缩包

    Args:
        zip_path: 数据压缩包存放路径
    """

    unzipped_count = 0

    for dir_path, dir_names, file_names in os.walk(zip_path):
        file_names.sort()
        for file_name in file_names:
            file_abs_path = os.path.join(dir_path, file_name)
            if file_abs_path.endswith('.zip') and os.path.isfile(file_abs_path):
                try:
                    unzip_file(file_abs_path, zip_path)
                    unzipped_count += 1
                except Exception as e:
                    print('failed to unzip file %s: %s' % (file_name, e))

    print('unzip %d file(s).' % unzipped_count)


def unzip_file(zipfile_path, target_path):
    """按时间顺序解压目录中的所有压缩包

    Args:
        zipfile_path: 压缩包路径
        target_path: 解压到的路径
    """
    zf = zipfile.ZipFile(zipfile_path)
    for member in zf.infolist():
        zf.extract(member, target_path)


def main():
    # config
    configs = load_parser_config()
    if configs is None:
        return

    attachment_path = configs.get('attachmentPath', './')

    # unzip all
    if not os.path.isdir(attachment_path):
        print('path not exists.')
        return
    unzip_files_in_path(attachment_path)


if __name__ == '__main__':
    main()
