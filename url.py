#!/usr/bin/env python3
import json
import re
import time
import os
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning

# 禁用 SSL 警告
warnings.simplefilter('ignore', InsecureRequestWarning)

# URL配置
WOGG_SOURCE_URL = "https://www.xn--sss604efuw.com/"
WOGG_DEFAULT_URL = "https://wogg.xxooo.cf"
TELEGRAM_MOGG_URL = "https://t.me/ucpanpan/2014"
XJS_SOURCE_URL = "https://mlink.cc/520TV"

# 站点映射关系
site_mappings = {
    '立播': 'libo',
    '闪电': 'shandian',
    '欧哥': 'ouge',
    '小米': 'xiaomi',
    '多多': 'duoduo',
    '蜡笔': 'labi',
    '至臻': 'zhizhen',
    '木偶': 'mogg',
    '六趣': 'liuqu',
    '虎斑': 'huban',
    '下饭': 'xiafan',
    '玩偶': 'wanou',
    '星剧社': 'xjs'
}

def test_url_delay(url):
    """测试URL的延迟"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=5, verify=False)
        if response.status_code == 200:
            return time.time() - start_time
        return None
    except:
        return None

def get_xjs_url():
    """从源站获取星剧社链接"""
    try:
        response = requests.get(XJS_SOURCE_URL, verify=False)
        if response.status_code == 200:
            # 查找包含star2.cn的域名
            match = re.search(r'https?://[^"\'\s<>]+?star2\.cn[^"\'\s<>]*', response.text)
            if match:
                url = match.group(0)
                print(f"找到星剧社域名: {url}")
                return url.rstrip('/')
    except Exception as e:
        print(f"获取星剧社链接失败: {str(e)}")
    return None

def get_initial_wogg_url():
    """从源站获取玩偶初始链接"""
    try:
        response = requests.get(WOGG_SOURCE_URL, verify=False)
        if response.status_code == 200:
            match = re.search(r'href="(https://[^"]*?wogg[^"]*?)"', response.text)
            if match:
                initial_url = match.group(1).rstrip('/') 
                print(f"从源站获取到玩偶初始链接: {initial_url}")
                return initial_url
    except Exception as e:
        print(f"获取玩偶初始链接失败: {str(e)}")
    return WOGG_DEFAULT_URL

def get_wogg_url():
    """获取玩偶链接并测试延迟"""
    initial_url = get_initial_wogg_url()
    
    try:
        response = requests.get(initial_url, verify=False)
        if response.status_code == 200:
            domains = []
            notice_match = re.search(r'<div class="popup-main">(.*?)</div>', response.text, re.DOTALL)
            
            if notice_match:
                for pattern in [r'域名\s+((?:www\.)?wogg\.[a-z.]+)', r'备用\s+((?:www\.)?wogg\.[a-z.]+)']:
                    domains.extend(re.findall(pattern, notice_match.group(1)))

            domains = list(dict.fromkeys(domains))
            print("找到玩偶域名:", domains)

            best_delay = float('inf')
            best_url = initial_url

            if domains:  # 只有在找到其他域名时才进行测试
                for domain in domains:
                    url = f"https://{domain.strip('/')}"
                    delay = test_url_delay(url)
                    if delay and delay < best_delay:
                        best_delay = delay
                        best_url = url
                        print(f"更新最佳域名: {url} (延迟: {delay:.3f}秒)")

            return best_url

    except Exception as e:
        print(f"获取玩偶链接出错: {str(e)}")
        print("开始对比初始链接和默认链接的延迟...")
        
        initial_delay = test_url_delay(initial_url)
        default_delay = test_url_delay(WOGG_DEFAULT_URL)
        
        print(f"初始链接延迟: {initial_delay:.3f}秒" if initial_delay else "初始链接不可用")
        print(f"默认链接延迟: {default_delay:.3f}秒" if default_delay else "默认链接不可用")
        
        if initial_delay and default_delay:
            return initial_url if initial_delay < default_delay else WOGG_DEFAULT_URL
        elif initial_delay:
            return initial_url
        elif default_delay:
            return WOGG_DEFAULT_URL
            
    return WOGG_DEFAULT_URL  # 如果都失败，返回默认链接

def get_mogg_url():
    """获取木偶链接"""
    try:
        response = requests.get(TELEGRAM_MOGG_URL, timeout=10, verify=False)
        if response.status_code == 200:
            domains = []
            for pattern in [r'(?:https?://)?([a-zA-Z0-9.-]+\.91muou\.icu)', 
                          r'(?:https?://)?([a-zA-Z0-9.-]+\.666291\.xyz)',
                          r'(?:https?://)?([a-zA-Z0-9.-]+\.muouso\.fun)']:
                domains.extend(re.findall(pattern, response.text, re.IGNORECASE))

            domains = list(dict.fromkeys(domains))
            if domains:
                print("找到木偶域名:", domains)
                best_delay = float('inf')
                best_url = None

                for domain in domains:
                    url = f"https://{domain}"
                    delay = test_url_delay(url)
                    if delay and delay < best_delay:
                        best_delay = delay
                        best_url = url
                        print(f"更新最佳域名: {url} (延迟: {delay:.3f}秒)")

                return best_url

    except Exception as e:
        print(f"获取木偶链接出错: {str(e)}")
    return None

def main():
    """主函数"""
    try:
        print("开始更新 URL...")
        
        # 读取API文件
        with open('TVBoxOSC/tvbox/api.json', 'r', encoding='utf-8') as f:
            api_data = json.load(f)

        url_data = {}
        
        # 获取星剧社链接
        xjs_url = get_xjs_url()
        if xjs_url:
            url_data['xjs'] = xjs_url
            print(f"添加星剧社链接: {xjs_url}")
        
        # 获取玩偶和木偶链接
        wogg_url = get_wogg_url()
        if wogg_url:
            url_data['wogg'] = wogg_url
            
        mogg_url = get_mogg_url()
        if mogg_url:
            url_data['mogg'] = mogg_url

        # 处理其他站点
        for site in api_data.get('sites', []):
            name = site.get('name', '')
            if '弹幕' in name:
                for cn_name, en_name in site_mappings.items():
                    if cn_name in name and cn_name not in ['木偶', '玩偶', '星剧社']:
                        ext = site.get('ext', {})
                        site_url = ext.get('site', '') if isinstance(ext, dict) else ext
                        if site_url and site_url.startswith('http'):
                            url_data[en_name] = site_url.strip()
                            print(f"添加 {cn_name} 链接: {site_url}")
                        break

        # 保存结果
        if url_data:
            with open('url.json', 'w', encoding='utf-8') as f:
                json.dump(url_data, f, ensure_ascii=False, indent=2)
            print(f"成功更新 {len(url_data)} 个链接")
            return True
            
        print("未找到任何有效链接")
        return False

    except Exception as e:
        print(f"更新过程出错: {str(e)}")
        return False

if __name__ == "__main__":
    main()
