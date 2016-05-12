# cyl-eye-770

Watch remote system.

## 模块简介
- 被监测系统: 将数据写入文件；将报警信息、心跳包写入文件
- server: 中转，提供 http 服务
- watcher: 定时将被监测系统的数据输出发送到邮箱；
将被监测系统的报警信息、心跳包汇报到 server
- android: 异常信息显示
- parser: 数据后处理

## License
LGPLv3
