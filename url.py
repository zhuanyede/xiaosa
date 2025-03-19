#!/usr/bin/env python3
import json
import time
import os
import requests
import warnings
import re
from urllib3.exceptions import InsecureRequestWarning

warnings.simplefilter('ignore', InsecureRequestWarning)

site_mappings = {
    '立播': 'libo',
    '欧哥': 'ouge',
    '小米': 'xiaomi',
    '多多': 'duoduo',
    '蜡笔': 'labi',
    '至臻': 'zhizhen',
    '木偶': 'mogg',
    '虎斑': 'huban',
    '下饭': 'xiafan',
    '玩偶': 'wogg',
    '星剧社': 'star2',
    '二小': 'erxiao',
    '大玩ou': 'dawanou',
    '玩偶叔叔': 'woss',
    '百家影音': 'baijia',
    '闪电': 'shandian'
}

buye_mappings = {
    '立播': 'libo',
    '欧哥': 'ouge',
    '小米': 'xmi',
    '多多': 'duo',
    '蜡笔': 'labi',
    '至臻': 'zhiz',
    '木偶': 'muo',
    '虎斑': 'hub',
    '下饭': 'xiaf',
    '玩偶': 'wogg',
    '星剧社': 'star2',
    '二小': 'erxiao',
    '大玩ou': 'dawanou',
    '玩偶叔叔': 'woss',
    '百家影音': 'baijia',
    '闪电': 'sd'
}

def test_url(url):
    try:
        response = requests.get(url.strip(), timeout=5, verify=False)
        return response.status_code == 200
    except:
        return False

def get_best_url(urls):
    if not isinstance(urls, list):
        return urls.strip()
    
    if len(urls) == 1:
        return urls[0].strip()
    
    default_url = urls[0].strip()
    
    for i in range(0, len(urls), 2):
        test_urls = urls[i:i+2]
        for url in test_urls:
            if test_url(url):
                return url.strip()
    
    return default_url

def get_star2_real_url(source_url):
    try:
        response = requests.get(source_url, timeout=5, verify=False)
        if response.status_code == 200:
            match = re.search(r'https?://[^"\'\s<>]+?star2\.cn[^"\'\s<>]*', response.text)
            if match:
                real_url = match.group(0).strip()
                print(f"从源站获取到星剧社真实链接: {real_url}")
                return real_url
    except Exception as e:
        print(f"获取星剧社真实链接失败: {str(e)}")
    return None

def process_urls(existing_urls):
    url_data = {}
    buye_data = {}
    
    try:
        if not os.path.exists('yuan.json'):
            print("yuan.json 文件不存在")
            return False
            
        with open('yuan.json', 'r', encoding='utf-8') as f:
            yuan_data = json.load(f)
            
        base_data = {}
        for cn_name, urls in yuan_data.items():
            if urls:
                if cn_name == '星剧社':
                    source_url = get_best_url(urls if isinstance(urls, list) else [urls])
                    if source_url:
                        real_url = get_star2_real_url(source_url)
                        if real_url:
                            base_data[cn_name] = real_url
                            print(f"添加 {cn_name} 链接: {real_url}")
                        elif cn_name in site_mappings and site_mappings[cn_name] in existing_urls:
                            base_data[cn_name] = existing_urls[site_mappings[cn_name]]
                            print(f"保持 {cn_name} 原有链接")
                else:
                    best_url = get_best_url(urls if isinstance(urls, list) else [urls])
                    if best_url:
                        base_data[cn_name] = best_url
                        print(f"添加 {cn_name} 链接: {best_url}")
                    elif cn_name in site_mappings and site_mappings[cn_name] in existing_urls:
                        base_data[cn_name] = existing_urls[site_mappings[cn_name]]
                        print(f"保持 {cn_name} 原有链接")
        
        for cn_name, url in base_data.items():
            if cn_name in site_mappings:
                url_data[site_mappings[cn_name]] = url
            if cn_name in buye_mappings:
                buye_data[buye_mappings[cn_name]] = url
        
        if url_data:
            with open('url.json', 'w', encoding='utf-8') as f:
                json.dump(url_data, f, ensure_ascii=False, indent=2)
            with open('buye.json', 'w', encoding='utf-8') as f:
                json.dump(buye_data, f, ensure_ascii=False, indent=2)
            print(f"成功更新 url.json 和 buye.json")
            return True
        
        print("没有新的有效数据")
        return False
        
    except Exception as e:
        print(f"处理出错: {str(e)}")
        return False

def main():
    print("开始更新 URL...")
    
    existing_urls = {}
    try:
        if os.path.exists('url.json'):
            with open('url.json', 'r', encoding='utf-8') as f:
                existing_urls = json.load(f)
    except Exception as e:
        print(f"读取 url.json 失败: {str(e)}")

    if process_urls(existing_urls):
        print("更新完成")
    else:
        print("更新失败，保持文件不变")

if __name__ == "__main__":
    main()
