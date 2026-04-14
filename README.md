# IP-Monitor
[![Static Badge](https://img.shields.io/badge/github-repo-blue?logo=github)](https://github.com/MeowPerth/IP-Monitor)
[![GitHub Issues](https://img.shields.io/github/issues/MeowPerth/IP-Monitor)](https://github.com/MeowPerth/IP-Monitor/issues)
![Last Commit](https://img.shields.io/github/last-commit/MeowPerth/IP-Monitor)
![GitHub License](https://img.shields.io/github/license/MeowPerth/IP-Monitor)
# 功能简介
基于Python脚本编写，用于监测 IP 是否发生变化，若 IP 变更 即发送邮件进行通知收件人
<br> 支持 多API，API 失效按顺序使用下一个 API 获取 IP
<br> 支持 多收件人
<br> 支持 自定义发件人昵称、邮件标题、正文内容
# Docker运行参数
```
docker run -d \
--name IP-Monitor \
-e TZ="Asia/Shanghai" \
-e API="https://ddns.oray.com/checkip,https://ip.3322.net" \
-e FROM_EMAIL="xxx@qq.com" \
-e FROM_EMAIL_PASSWORD="xxx" \
-e TO_EMAIL="xxx@qq.com" \
-e SMTP_SERVER="smtp.qq.com" \
-e SMTP_PORT=465 \
-e INTERVAL=60 \
--restart=always \
1114788662/ip-monitor:latest
```
# 所有参数解释：

| 变量 | 含义 | 
| --- | --- | 
| TZ | 时区，默认：Asia/Shanghai | 
| API | 可以返回IP地址的 api，支持多个地址，以半角逗号隔开，默认为https://ddns.oray.com/checkip, https://ip.3322.net | 
| FROM_NAME | 自定义发送人名称 | 
| FROM_EMAIL | 发送人邮箱（必填） | 
| FROM_EMAIL_PASSWORD | 发送人邮箱授权码（必填） | 
| TO_EMAIL | 收件人邮箱，支持多个接收人，以半角逗号隔开，默认为发送人邮箱 | 
| SMTP_SERVER | smtp 服务器地址，默认为 smtp.qq.com | 
| SMTP_PORT | smtp 端口，默认为 465 | 
| INTERVAL | 检测间隔，默认为 60s | 
| EMAIL_TITLE | 自定义邮件标题，默认为 "IP 变更通知" | 
|  EMAIL_HEADER | 自定义邮件开头，默认为 "检测到当前 IP 地址已变更！" | 
| EMAIL_FOOTER | 自定义邮件结尾，默认为 "来自 IP-Monitor" | 
