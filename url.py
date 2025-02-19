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

# 原有的站点映射关系
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
    '玩偶': 'wogg',
    '星剧社': 'star2'
}

# 新的站点映射关系
buye_mappings = {
    '立播': 'libo',
    '闪电': 'sd',
    '欧哥': 'ouge',
    '小米': 'xmi',
    '多多': 'duo',
    '蜡笔': 'labi',
    '至臻': 'zhiz',
    '木偶': 'muo',
    '六趣': 'liuq',
    '虎斑': 'hub',
    '下饭': 'xiaf',
    '玩偶': 'wogg',
    '星剧社': 'star2'
}

def save_url_data(url_data, filename='url.json'):
    """保存 URL 数据到文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(url_data, f, ensure_ascii=False, indent=2)
        print(f"成功保存 {len(url_data)} 个链接到 {filename}")
        return True
    except Exception as e:
        print(f"保存 URL 数据失败: {str(e)}")
        return False

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

def get_best_url(urls):
    """从多个URL中选择最佳的一个"""
    if not isinstance(urls, list):
        urls = [urls]
    
    valid_urls = []
    for url in urls:
        delay = test_url_delay(url.strip())
        if delay is not None:
            valid_urls.append((url.strip(), delay))
    
    if valid_urls:
        # 按延迟时间排序，返回延迟最小的URL
        return sorted(valid_urls, key=lambda x: x[1])[0][0]
    return None

def get_xjs_url():
    """从源站获取星剧社链接"""
    try:
        response = requests.get(XJS_SOURCE_URL, verify=False)
        if response.status_code == 200:
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
            if domains:
                urls = [f"https://{domain.strip('/')}" for domain in domains]
                best_url = get_best_url(urls)
                if best_url:
                    return best_url

    except Exception as e:
        print(f"获取玩偶链接出错: {str(e)}")
        
    return get_best_url([initial_url, WOGG_DEFAULT_URL])

def get_mogg_url(original_url=None):
    """获取木偶链接"""
    try:
        response = requests.get(TELEGRAM_MOGG_URL, timeout=10, verify=False)
        if response.status_code == 200:
            domains = []
            patterns = [
                r'(?:https?://)?([a-zA-Z0-9.-]+\.91muou\.icu)',
                r'(?:https?://)?([a-zA-Z0-9.-]+\.666291\.xyz)',
                r'(?:https?://)?([a-zA-Z0-9.-]+\.muouso\.fun)'
            ]
            
            for pattern in patterns:
                domains.extend(re.findall(pattern, response.text, re.IGNORECASE))

            domains = list(dict.fromkeys(domains))
            if domains:
                urls = [f"https://{domain}" for domain in domains]
                best_url = get_best_url(urls)
                if best_url:
                    return best_url

    except Exception as e:
        print(f"获取木偶链接出错: {str(e)}")
    
    return original_url

def process_yuan_data(mapping):
    """从 yuan.json 处理站点信息"""
    url_data = {}
    try:
        if not os.path.exists('yuan.json'):
            print("警告: yuan.json 文件不存在")
            return url_data
            
        with open('yuan.json', 'r', encoding='utf-8') as f:
            yuan_data = json.load(f)
            
        for cn_name, en_name in mapping.items():
            if cn_name not in ['木偶', '玩偶', '星剧社'] and cn_name in yuan_data:
                urls = yuan_data[cn_name]
                if urls:  # 确保有数据
                    best_url = get_best_url(urls)
                    if best_url:
                        url_data[en_name] = best_url
                        print(f"从 yuan.json 添加 {cn_name} 链接 ({en_name}): {best_url}")
                    
    except Exception as e:
        print(f"处理 yuan.json 数据出错: {str(e)}")
        
    return url_data

def main():
    """主函数"""
    try:
        print("开始更新 URL...")
        
        # 读取现有的 url.json（如果存在）
        existing_urls = {}
        if os.path.exists('url.json'):
            try:
                with open('url.json', 'r', encoding='utf-8') as f:
                    existing_urls = json.load(f)
            except Exception as e:
                print(f"读取现有 url.json 失败: {str(e)}")

        # 为两种映射分别获取数据
        url_data = {}
        buye_data = {}
        
        # 获取星剧社链接
        xjs_url = get_xjs_url()
        if xjs_url:
            url_data['star2'] = xjs_url
            buye_data['star2'] = xjs_url
            print(f"添加星剧社链接: {xjs_url}")
        
        # 获取玩偶链接
        wogg_url = get_wogg_url()
        if wogg_url:
            url_data['wogg'] = wogg_url
            buye_data['wogg'] = wogg_url
            print(f"添加玩偶链接: {wogg_url}")
        
        # 获取木偶链接
        mogg_url = get_mogg_url(existing_urls.get('mogg'))
        if mogg_url:
            url_data['mogg'] = mogg_url
            buye_data['muo'] = mogg_url
            print(f"添加木偶链接: {mogg_url}")

        # 从 yuan.json 处理其他站点 - 使用不同的映射
        url_data.update(process_yuan_data(site_mappings))
        buye_data.update(process_yuan_data(buye_mappings))

        # 保存两个文件
        success = True
        if url_data:
            success &= save_url_data(url_data, 'url.json')
        if buye_data:
            success &= save_url_data(buye_data, 'buye.json')
            
        if not (url_data or buye_data):
            print("未找到任何有效链接")
            return False
            
        return success

    except Exception as e:
        print(f"更新过程出错: {str(e)}")
        return False

if __name__ == "__main__":
    main()
