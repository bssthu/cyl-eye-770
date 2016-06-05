#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : format_lvm.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : 把 lvm 数据文件处理成 csv 格式
# 

import time
import datetime
from load_parser_config import *


def format_data_in_path(attachment_path):
    """处理目录中的所有数据

    Args:
        attachment_path: 数据存放路径
    """

    # merge data from files
    data = []
    for dir_path, dir_names, file_names in os.walk(attachment_path):
        file_names.sort()
        for file_name in file_names:
            file_abs_path = os.path.join(dir_path, file_name)
            if file_abs_path.endswith('.lvm') and os.path.isfile(file_abs_path):
                try:
                    data_from_file = format_data_file(file_abs_path)
                    data.extend(data_from_file)
                except Exception as e:
                    print('failed to parse file %s: %s' % (file_name, e))

    # save results
    result_file_path = os.path.join(attachment_path, 'format_data.csv')
    with open(result_file_path, 'wt') as fp:
        data_lines = [', '.join(data_line) + '\n' for data_line in data]
        fp.writelines(data_lines)


def format_data_file(file_path):
    """处理一个文件

    Args:
        file_path: 文件路径
    """
    data_in_file = []
    date_str = None
    time_str = None
    datetime_file = None
    status = 0
    with open(file_path, 'rt') as fp:
        for line in fp.readlines():
            if status == 0 and line.startswith('Channels'):
                status = 1
            elif status == 1:
                if line.startswith('Date'):
                    date_str = line.split('\t')[1]
                if line.startswith('Time'):
                    time_str = line.split('\t')[1]
                if line.startswith('X_Value'):
                    datetime_str = '%s %s' % (date_str, time_str)
                    datetime_str = datetime_str[:26]
                    datetime_file = datetime.datetime.strptime(datetime_str, '%Y/%m/%d %H:%M:%S.%f')
                    status = 2
            elif status == 2:
                stamp_str = datetime_file.strftime('%Y-%m-%d %H:%M:%S')     # 时间戳
                stamp_seconds = str(int(time.mktime(datetime_file.timetuple())))    # 时间戳，秒数
                data_in_line = [stamp_str, stamp_seconds]
                datetime_file += datetime.timedelta(seconds=1)

                data_raw = line.split()
                data_in_line.extend(data_raw[1::2])     # 跳过每个数据自带的时间戳
                data_in_file.append(data_in_line)

    return data_in_file


def main():
    # config
    configs = load_parser_config()
    if configs is None:
        return

    attachment_path = configs.get('attachmentPath', './')

    # format data
    if not os.path.isdir(attachment_path):
        print('path not exists.')
        return
    format_data_in_path(attachment_path)


if __name__ == '__main__':
    main()
