[![Static Badge](https://img.shields.io/badge/github-repo-blue?logo=github)](https://github.com/MeowPerth/IP-Monitor)
[![GitHub Issues](https://img.shields.io/github/issues/MeowPerth/IP-Monitor)](https://github.com/MeowPerth/IP-Monitor/issues)
![Last Commit](https://img.shields.io/github/last-commit/MeowPerth/IP-Monitor)
![GitHub License](https://img.shields.io/github/license/MeowPerth/IP-Monitor)

# 功能简介
基于Python脚本编写，用于监测 IP 是否发生变化，若 IP 变更 即发送邮件进行通知收件人
<br> 支持 多API，API 失效按顺序使用下一个 API 获取 IP
<br> 支持 IPv4、IPv6
<br> 支持 多收件人
<br> 支持 自定义发件人昵称、邮件标题、正文内容
# Docker运行参数
```
docker run -d \
--name IP-Monitor \
-e API="https://api-ipv4.ip.sb/ip,https://v4.ident.me,https://ddns.oray.com/checkip,https://ip.3322.net" \
-e API_V6="https://api-ipv6.ip.sb/ip,https://v6.ident.me,https://ipv6.icanhazip.com" \
-e IPV6_ENABLE=false \
-e TZ="Asia/Shanghai" \
-e FROM_EMAIL="xxx@qq.com" \
-e FROM_EMAIL_PASSWORD="xxx" \
-e TO_EMAIL="xxx@qq.com" \
-e SMTP_SERVER="smtp.qq.com" \
-e SMTP_PORT=465 \
-e INTERVAL=60 \
--restart=always \
1114788662/ip-monitor:latest
```
# 所有参数解释

| 变量 | 含义 | 
| --- | --- | 
| API | 可以返回IPv4地址的 api，支持多个地址，以半角逗号隔开，默认为https://api-ipv4.ip.sb/ip,https://v4.ident.me,https://ddns.oray.com/checkip,https://ip.3322.net | 
| API_V6 | 可以返回IPv6地址的 api，支持多个地址，以半角逗号隔开，默认为https://api-ipv6.ip.sb/ip,https://v6.ident.me,https://ipv6.icanhazip.com | 
| IPV6_ENABLE | 启用IPv6地址监测，默认：false | 
| TZ | 时区，默认：Asia/Shanghai | 
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
# 更新日志
<br> [20260415]
<br> 1、新增IPv6监测支持,启用后IPv6后，IPv4和IPv6都无法获取网络地址才会发送错误通知邮件，否则只会发送地址变更通知邮件。
<br> 2、修改IPv4默认API地址。
<br> [20260416]
<br> 1、调整邮件内容显示顺序，先显示 New IP 再显示 Old IP 。
# 注意事项 & 常见问题
<br> Q1：路由器开启代理（如：OpenClash）后，无法获取到正确的IPv4地址。
<br>  A：请检查代理路由规则，将API查询用的地址添加到直连规则中即可。
<br> Q2：路由器开启代理（如：OpenClash）后，无法获取到正确的IPv6地址。
<br>  A：请检查OpenClash是否使用了Fake-IP模式，这里推荐使用Redir-Host模式，并关闭IPv6代理，启用IPv6 DNS解析，Fake-IP会导致无法获取到正确的IP地址，若Redir-Host模式还是无法获取到正确IP请检查路由规则。
<br> Q3：容器使用bridge网络时无法获取到IPv6地址。
<br>  A：请检查bridge网络是否支持IPv6，或直接使用host网络。
