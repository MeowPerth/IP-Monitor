FROM python:3.7-alpine
 
RUN pip install requests
 
COPY ip-monitor.py /ip-monitor.py

ENV API="https://api-ipv4.ip.sb/ip,https://v4.ident.me,https://ddns.oray.com/checkip,https://ip.3322.net"
ENV API_V6="https://api-ipv6.ip.sb/ip,https://v6.ident.me,https://ipv6.icanhazip.com"
ENV IPV6_ENABLE="false"
ENV TZ=Asia/Shanghai
ENV FROM_NAME=
ENV FROM_EMAIL=
ENV FROM_EMAIL_PASSWORD=
ENV TO_EMAIL=
ENV SMTP_SERVER="smtp.qq.com"
ENV SMTP_PORT="465"
ENV INTERVAL="60"
ENV EMAIL_TITLE="IP 变更通知"
ENV EMAIL_HEADER="检测到当前 IP 地址已变更！"
ENV EMAIL_FOOTER="来自 IP-Monitor"
 
ENTRYPOINT ["python3", "-u","/ip-monitor.py"]
