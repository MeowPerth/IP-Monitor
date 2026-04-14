import os
import requests
import re
import time
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from email.header import Header
import logging
import sys

# Docker环境日志配置 - 仅控制台输出
def setup_logging():
    ## 配置日志系统 - 仅控制台输出，适合Docker环境
    # 创建logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # 清除已有的handler
    logger.handlers.clear()
    
    # 创建控制台handler - 确保Docker日志可以显示
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # 设置日志格式 - 简洁格式，适合Docker日志
    formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(formatter)
    
    # 添加控制台handler
    logger.addHandler(console_handler)
    
    return logger

# 初始化日志
logger = setup_logging()

class ENV:
    ## 环境变量配置类
    def __init__(self):
        # 检查必需的环境变量
        required_vars = {
            "FROM_EMAIL": "发送邮箱账户",
            "FROM_EMAIL_PASSWORD": "发送邮箱授权密码"
        }
        
        missing_vars = []
        for var, desc in required_vars.items():
            if not os.environ.get(var):
                missing_vars.append(f"{var}({desc})")
        
        if missing_vars:
            error_msg = f"请配置以下环境变量: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # 解析API列表 - 支持多种分隔符（逗号或空格）
        api_env = os.environ.get("API", "")
        if api_env:
            # 支持逗号和空格分隔
            api_env = api_env.replace(' ', ',')
            self.api_list = [api.strip() for api in api_env.split(",") if api.strip()]
        else:
            self.api_list = ["https://ddns.oray.com/checkip", "https://ip.3322.net"]
            logger.info(f"使用默认API列表: {self.api_list}")
        
        self.from_name = os.environ.get("FROM_NAME", "IP监控")
        self.from_email = os.environ.get("FROM_EMAIL")
        self.from_email_password = os.environ.get("FROM_EMAIL_PASSWORD")
        
        to_emails = os.environ.get("TO_EMAIL", self.from_email)
        self.to_email_list = [email.strip() for email in to_emails.split(",") if email.strip()]
        
        self.smtp_server = os.environ.get("SMTP_SERVER", "smtp.qq.com")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "465"))
        self.interval = int(os.environ.get("INTERVAL", "60"))
        self.email_title = os.environ.get("EMAIL_TITLE", "IP 变更通知")
        self.email_header = os.environ.get("EMAIL_HEADER", "检测到当前 IP 地址已变更！")
        self.email_footer = os.environ.get("EMAIL_FOOTER", "来自 IP-Monitor")
        
        logger.info("=" * 50)
        logger.info("环境变量配置完成")
        logger.info(f"API列表: {self.api_list}")
        logger.info(f"发件邮箱: {self.from_email}")
        logger.info(f"收件邮箱: {self.to_email_list}")
        logger.info(f"检查间隔: {self.interval}秒")
        logger.info("=" * 50)

def current_ip(api_list):
    ## 获取当前公网IP地址
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"
    }
    
    for api in api_list:
        try:
            # logger.info(f"尝试从 {api} 获取IP...")
            # 添加超时设置
            
            response = requests.get(api, headers=headers, timeout=10)
            if response.status_code == 200:
                ip_matches = re.findall(r'[0-9]+(?:\.[0-9]+){3}', response.text)
                if ip_matches:
                    ip = ip_matches[0]
                    logger.info(f"[成功] {api} 返回IP: {ip}")
                    return ip
                else:
                    logger.warning(f"[失败] {api} 返回的内容中没有找到IP地址")
            else:
                logger.warning(f"[失败] {api} 返回状态码: {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.warning(f"[失败] 请求 {api} 超时")
        except requests.exceptions.ConnectionError:
            logger.warning(f"[失败] 连接 {api} 失败，请检查网络")
        except requests.exceptions.RequestException as e:
            logger.warning(f"[失败] 请求 {api} 失败: {str(e)}")
        except Exception as e:
            logger.error(f"[错误] 处理 {api} 时发生未知错误: {str(e)}")
            continue
    
    logger.error("[错误] 所有获取公网的API均不可用")
    return None

def sendmail(old_ip, current_ip, env, is_error=False):
	## 发送文本邮件
    # 发信方的信息
    from_name = env.from_name
    from_addr = env.from_email
    password = env.from_email_password
    
    # 发信服务器
    smtp_server = env.smtp_server
    smtp_port = env.smtp_port
    
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    if is_error:
        subject = f"【警告】{env.email_title} - 服务异常"
        content = f"""
{env.email_header}

【警告】IP检测服务异常
无法获取公网IP地址，请检查网络连接或API服务。

最后记录的IP地址: {old_ip}
异常时间: {current_time}

{env.email_footer}
        """
    else:
        subject = env.email_title
        content = f"""
{env.email_header}

原IP地址: {old_ip}
现IP地址: {current_ip}
变更时间: {current_time}

{env.email_footer}
        """
    
    # 创建纯文本邮件
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = formataddr((from_name, from_addr))
    msg['To'] = ','.join(env.to_email_list)
    msg['Subject'] = Header(subject, 'utf-8')
    
    smtpobj = None
    try:
        logger.info(f"[邮件] 发送邮件到: {env.to_email_list}")
        smtpobj = smtplib.SMTP_SSL(smtp_server, timeout=30)
        smtpobj.connect(smtp_server, smtp_port)
        smtpobj.login(from_addr, password)
        
        # 批量发送
        smtpobj.sendmail(from_addr, env.to_email_list, msg.as_string())
        logger.info("[邮件] 发送成功")
        return True
        
    except smtplib.SMTPAuthenticationError:
        logger.error("[错误] 邮箱认证失败，请检查账号和授权码")
    except smtplib.SMTPException as e:
        logger.error(f"[错误] SMTP错误: {str(e)}")
    except Exception as e:
        logger.error(f"[错误] 发送邮件时发生未知错误: {str(e)}")
    finally:
        if smtpobj:
            try:
                smtpobj.quit()
            except:
                pass
    return False

def print_status(old_ip, current_ip, consecutive_failures):
    ## 打印状态信息
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    fail_info = f" [连续失败:{consecutive_failures}]" if consecutive_failures > 0 else ""
    ip_display = current_ip if current_ip else "获取失败"
    old_ip_display = old_ip if old_ip is not None else "未记录"
    logger.info(f"[{current_time}] 旧IP: {old_ip_display} | 当前IP: {ip_display}{fail_info}")

def main():
    ## 主函数
    # 初始化变量
    logger.info("=" * 50)
    logger.info("IP监控程序启动")
    logger.info("=" * 50)
    
    try:
        env = ENV()
    except Exception as e:
        logger.error(f"[错误] 环境变量配置失败: {str(e)}")
        sys.exit(1)
    
    # 初始旧IP设为空
    old_ip = None
    
    logger.info("开始IP监控 (首次运行将记录初始IP)")
    logger.info("=" * 50)
    
    # 添加重试计数
    consecutive_failures = 0
    max_consecutive_failures = 5
    error_email_sent = False
    
    while True:
        try:
            # 获取当前IP
            current_ip_addr = current_ip(env.api_list)
            
            # 打印状态
            print_status(old_ip, current_ip_addr, consecutive_failures)
            
            # 处理获取IP失败的情况
            if current_ip_addr is None:
                consecutive_failures += 1
                
                if consecutive_failures >= max_consecutive_failures and not error_email_sent:
                    # 发送告警邮件
                    logger.error("[警告] 连续多次获取IP失败，发送告警邮件")
                    sendmail(old_ip if old_ip else "未知", "获取失败", env, is_error=True)
                    error_email_sent = True
                
                time.sleep(env.interval)
                continue
            
            # 成功获取IP，重置失败计数和错误邮件标志
            consecutive_failures = 0
            error_email_sent = False
            
            # 如果是第一次获取到IP，记录下来
            if old_ip is None:
                old_ip = current_ip_addr
                # logger.info(f"[记录] 初始IP: {old_ip}")
            
            # IP发生变化 - 始终发送邮件
            elif old_ip != current_ip_addr:
                # logger.info(f"[变化] IP地址发生改变: {old_ip} -> {current_ip_addr}")
                
                # 发送邮件通知
                send_success = sendmail(old_ip, current_ip_addr, env)
                
                # 更新IP
                old_ip = current_ip_addr
                
                if not send_success:
                    logger.error("[警告] 邮件发送失败")
            
            # 等待下一次检查
            time.sleep(env.interval)
            
        except KeyboardInterrupt:
            logger.info("程序被用户中断")
            break
        except Exception as e:
            logger.error(f"[错误] 主循环发生未预期错误: {str(e)}")
            time.sleep(env.interval)

if __name__ == '__main__':
    main()