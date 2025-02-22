#!/usr/bin/env python3
import json
import time
import os
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning

warnings.simplefilter('ignore', InsecureRequestWarning)

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
    '玩偶': 'wogg',
    '星剧社': 'star2'
}

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

def test_url(url):
    """测试URL是否可用"""
    try:
        # 仅发送HEAD请求检查可访问性，超时设置为3秒
        response = requests.head(
            url.strip(),
            timeout=3,
            verify=False,
            allow_redirects=True  # 允许重定向
        )
        
        # 检查状态码，2xx表示成功
        if 200 <= response.status_code < 300:
            print(f"URL {url} 可用 (状态码: {response.status_code})")
            return True
        else:
            print(f"URL {url} 不可用 (状态码: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"URL {url} 访问失败: {str(e)}")
        return False

def get_best_url(urls):
    """从多个URL中选择可用的URL"""
    if not isinstance(urls, list):
        urls = [urls]
    
    for url in urls:
        print(f"\n测试URL: {url}")
        if test_url(url):
            return url.strip()
    
    return None

def process_urls(existing_urls):
    """处理所有URL数据"""
    try:
        if not os.path.exists('yuan.json'):
            print("yuan.json 文件不存在")
            return False
            
        with open('yuan.json', 'r', encoding='utf-8') as f:
            yuan_data = json.load(f)
            
        # 存储结果
        url_data = {}
        buye_data = {}
        base_data = {}
        
        # 处理每个站点
        for cn_name, urls in yuan_data.items():
            print(f"\n处理 {cn_name} 的URL...")
            if not urls:
                continue
                
            # 获取可用URL
            best_url = get_best_url(urls if isinstance(urls, list) else [urls])
            
            if best_url:
                base_data[cn_name] = best_url
                print(f"使用新URL: {best_url}")
            elif cn_name in site_mappings and site_mappings[cn_name] in existing_urls:
                # 测试现有URL
                existing_url = existing_urls[site_mappings[cn_name]]
                print(f"测试现有URL: {existing_url}")
                if test_url(existing_url):
                    base_data[cn_name] = existing_url
                    print(f"保留现有URL: {existing_url}")
                else:
                    print(f"现有URL已失效，跳过 {cn_name}")
            else:
                print(f"没有可用URL，跳过 {cn_name}")
        
        # 映射到两种格式
        for cn_name, url in base_data.items():
            if cn_name in site_mappings:
                url_data[site_mappings[cn_name]] = url
            if cn_name in buye_mappings:
                buye_data[buye_mappings[cn_name]] = url
        
        if url_data:
            # 显示将要保存的内容
            print("\n将要保存的 url.json 内容:")
            print(json.dumps(url_data, ensure_ascii=False, indent=2))
            
            # 保存文件
            with open('url.json', 'w', encoding='utf-8') as f:
                json.dump(url_data, f, ensure_ascii=False, indent=2)
            with open('buye.json', 'w', encoding='utf-8') as f:
                json.dump(buye_data, f, ensure_ascii=False, indent=2)
            print("文件更新成功")
            return True
        
        print("没有可用的URL数据")
        return False
        
    except Exception as e:
        print(f"处理出错: {str(e)}")
        return False

def main():
    """主函数"""
    print("开始更新 URL...")
    
    # 读取现有的 url.json
    existing_urls = {}
    try:
        if os.path.exists('url.json'):
            with open('url.json', 'r', encoding='utf-8') as f:
                existing_urls = json.load(f)
                print("\n当前的 url.json 内容:")
                print(json.dumps(existing_urls, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"读取 url.json 失败: {str(e)}")

    # 处理并保存URL
    if process_urls(existing_urls):
        print("更新完成")
    else:
        print("更新失败")

if __name__ == "__main__":
    main()
