#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : merge_backup_txt.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : 处理 txt 表格格式的备份数据
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
            if file_abs_path.endswith('.txt') and os.path.isfile(file_abs_path):
                try:
                    int(file_name[:-4])     # file name without ext should be an int
                except ValueError:
                    continue    # skip other txt files
                try:
                    print('parsing file %s ...' % file_name)
                    data_from_file = format_data_file(file_abs_path)
                    data.extend(data_from_file)
                except Exception as e:
                    print('failed to parse file %s: %s' % (file_name, e))

    # sort by time. 记录文件时，文件名靠人工更新，有可能乱序
    print('sorting data...')
    data.sort(key=lambda x: x[1])   # sort by time

    # save results
    print('saving data...')
    result_file_path = os.path.join(attachment_path, 'format_data_bak.csv')
    with open(result_file_path, 'wt') as fp:
        data_lines = [', '.join(data_line) + '\n' for data_line in data]
        fp.writelines(data_lines)


def format_data_file(file_path):
    """处理一个文件

    文件每 7 行一组。
    前 6 行是用 '\t' 分隔的数据，每行的前 4 项是需要的通道数据。
    第 7 行是该组的采样时间。

    Args:
        file_path: 文件路径

    Returns:
        list of lines. each line is a list too.
    """

    with open(file_path, 'rt') as fp:
        lines = fp.readlines()

    data_in_file = []
    table_num = int(len(lines) / 7)
    for i in range(0, table_num):
        # 第 7 行，时间
        datetime_str = lines[i*7 + 6].split('\t')[0]
        datetime_str = datetime_str[:26]

        datetime_of_line = datetime.datetime.strptime(datetime_str, '%Y/%m/%d %H:%M:%S')

        stamp_str = datetime_of_line.strftime('%Y-%m-%d %H:%M:%S')     # 时间戳
        stamp_seconds = str(int(time.mktime(datetime_of_line.timetuple())))    # 时间戳，秒数
        data_in_line = [stamp_str, stamp_seconds]

        # 前 6 行，数据
        # 如果是 NaN，就用上一次的
        if 'NaN' == lines[i*7][:3]:
            if len(data_in_file) > 0:
                data_in_last_line = data_in_file[-1]
                data_in_line.extend(data_in_last_line[2:])
            else:
                # 跳过一开始的 NaN
                # NaN 的情况是从最后一个文件才开始出现的，所以不做跨文件的处理
                continue
        else:
            for j in range(0, 6):
                data_in_line.extend(lines[i*7 + j].split('\t')[0:4])

        # add this line to list
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
