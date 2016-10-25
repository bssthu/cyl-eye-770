## watcher 说明

- 定期用邮件上传特定本地文件
- 检查本地文件中的报警和心跳，向服务器汇报


## 使用方法

### 配置

```
cp ./docs/watcher_config.json.example ./conf/watcher_config.json
```
并按需修改。

### watcher_config 说明

- `"httpServer"` 配置 http 服务端信息，本地的心跳、警报等数据向此服务器上报。
- `"email"` 配置邮箱登录信息及要监视的文件。
- `"watchPath"` 指要监视的路径。
- `"fileExt"` 和 `"fileNum"` 指要监视并打包发邮件的文件扩展名、最多打包的文件数量。
文件在 `"watchPath"` 路径内。
- `"extraWatchFiles"` 指其他要打包用邮件发送的文件。
不受 `"fileExt"` 和 `"fileNum"` 制约。
- `"files"` 配置了报警和心跳文件的信息，将读取这些信息并以 http 方式上报。

### 启动
```
cd scripts/
python3 watcher.py
```


## License
LGPLv3
