#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# File          : check_weather_rp5.py
# Author        : bssthu
# Project       : cyl-eye-770
# Description   : 检查来自 rp5.ru 的天气数据，找出在 format_data 中对应的位置
# 

import sys
import time
import datetime
from load_parser_config import *


def check_weather_data(attachment_path, format_data_file):
    """处理目录中的所有数据

    Args:
        attachment_path: 数据存放路径
        format_data_file: format_data.csv，需要将天气数据的时间戳与该文件对应
    """

    # load weather history
    weather_path = os.path.join(attachment_path, 'weather_history_rp5.csv')
    temperature_record = []
    with open(weather_path, 'rt', encoding='utf-8') as fp:
        for line in fp.readlines()[7:]:
            if line.strip() != '':
                time_temperature = line.split(';')[:2]
                datetime_str = time_temperature[0].strip('"')
                datetime_line = datetime.datetime.strptime(datetime_str, '%d.%m.%Y %H:%M')
                stamp_seconds = int(time.mktime(datetime_line.timetuple()))
                temperature_record.append((datetime_line, stamp_seconds, time_temperature[1].strip('"')))
    temperature_record.sort(key=(lambda x: x[1]))       # 按时间升序排列
    len_temperature_record = len(temperature_record)

    # load & check format_data
    format_data_timestamp = []
    format_data_path = os.path.join(attachment_path, format_data_file)
    i = 0       # index of temperature_record
    line_no = 0     # index of fp.readlines()
    with open(format_data_path) as fp:
        for line in fp.readlines():
            stamp_format_data = int(line.split(',')[1])
            if stamp_format_data >= temperature_record[i][1]:   # 比较是否找到了这个温度记录在 format_data 中对应的时间
                new_line = '%s, %d, %s\n' % (temperature_record[i][0], line_no, temperature_record[i][2])
                format_data_timestamp.append(new_line)
                i += 1
                if i >= len_temperature_record:
                    break
            line_no += 1

    # save results
    result_file_path = os.path.join(attachment_path, 'format_weather.csv')
    with open(result_file_path, 'wt') as fp:
        fp.writelines(format_data_timestamp)


def main():
    # config
    configs = load_parser_config()
    if configs is None:
        return

    format_data_file = 'format_data.csv'
    if len(sys.argv) == 2:
        format_data_file = sys.argv[1]

    attachment_path = configs.get('attachmentPath', './')

    # check data
    if not os.path.isdir(attachment_path):
        print('path not exists.')
        return
    check_weather_data(attachment_path, format_data_file)


if __name__ == '__main__':
    main()
