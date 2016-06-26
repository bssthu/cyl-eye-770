#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : interp_csv.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : 调整 csv 文档，按指定时间间隔重采样（0阶）
# 

import sys
import getopt
import time
from load_parser_config import *


def usage():
    print('Usage:')
    print('./interp_csv.py -i file.csv -t 10')
    print('-i, --input: input csv file (from attachment path)')
    print('-t, --interval: sample interval')


def get_filename_and_interval():
    """从命令行参数中读取csv文件名，以及重采样时间间隔"""
    input_filename = None
    interval = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:t:', ['input=', 'interval='])
    except getopt.GetoptError as e:
        print(e)
        usage()
        sys.exit(2)
    for o, a in opts:
        if o in ('-i', '--input'):
            input_filename = a
        elif o in ('-t', '--interval'):
            interval = int(a)

    if (input_filename is None) or (interval is None) or interval <= 0:
        usage()
        sys.exit(2)
    return input_filename, interval


def load_from_csv(filename):
    """从原始 csv 文件中读取数据并排序

    Args:
        filename: csv 文件路径
    """
    data = []
    fp = open(filename, 'rt')
    for line in fp.readlines():
        timestr, timeint, raw = [x.strip() for x in line.split(',', 2)]
        timeint = int(timeint)
        data.append((timeint, raw))
    data.sort(key=lambda x: x[0])
    return data


def save_to_csv(filename, data):
    """将数据写入回 csv 文件中

    Args:
        filename: csv 文件路径
        data: 要写入的 list， list 中每一项格式为 (timeint, raw)
    """
    with open(filename, 'wt') as fp:
        for timeint, raw in data:
            timestamp = time.strptime(time.ctime(timeint))
            timestr = time.strftime('%Y%m%d.%H%M%S', timestamp)
            line = '%s, %d, %s\n' % (timestr, timeint, raw)
            fp.writelines(line)


def resample_csv(filename, interval):
    """读取 csv 文件，重新采样，保存回原文件

    Args:
        filename: csv 文件路径
        interval: 重采样时间间隔 (s)
    """

    # load data from file
    print('loading data...')
    data_from_origin = load_from_csv(filename)
    print('load %d line(s).' % len(data_from_origin))
    if len(data_from_origin) == 0:
        return

    # resample
    print('resampling...')
    data_resample = [data_from_origin[0]]
    time_begin = data_from_origin[0][0]
    time_end = data_from_origin[-1][0]

    # 从第一个时刻开始，每过 interval 采一个点，该点的值取 origin 中当前时刻的值或当前以前最近一个时刻的值
    i_origin = 1
    t_resample = time_begin + interval
    while t_resample < time_end:
        while data_from_origin[i_origin][0] < t_resample:
            i_origin += 1
        raw_latest = data_from_origin[i_origin-1][1]
        data_resample.append((t_resample, raw_latest))
        t_resample += interval

    # write back
    print('saving %d lines...' % len(data_resample))
    save_to_csv(filename, data_resample)


def main():
    # opts
    filename, interval = get_filename_and_interval()

    # config
    configs = load_parser_config()
    if configs is None:
        return

    attachment_path = configs.get('attachmentPath', './')
    filename = os.path.join(attachment_path, filename)

    if not os.path.isdir(attachment_path):
        print('path not exists.')
        return
    if not os.path.isfile(filename):
        print('file not exists.')
        return

    # resample csv
    resample_csv(filename, interval)


if __name__ == '__main__':
    main()
