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
TELEGRAM_MOGG_URL = "https://t.me/ucpanpan/2014"
WOGG_DEFAULT_URL = "https://wogg.xxooo.cf"

# 站点映射关系
site_mappings = {
    '立播': 'libo',
    '闪电': 'feimao',
    '欧哥': 'ouge',
    '小米': 'xiaomi',
    '多多': 'duoduo',
    '蜡笔': 'labi',
    '至臻': 'mihdr',
    '木偶': 'mogg',
    '六趣': 'liuqu',
    '虎斑': 'huban',
    '下饭': 'texiafan',
    '玩偶': 'wogg'
}

def get_mogg_domains_from_telegram():
    """从Telegram频道获取木偶域名列表"""
    try:
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        session.headers.update(headers)

        # 关闭SSL验证，添加重试机制
        retry_count = 3
        for i in range(retry_count):
            try:
                response = session.get(
                    TELEGRAM_MOGG_URL,
                    timeout=10,
                    verify=False,
                    headers=headers
                )
                if response.status_code == 200:
                    content = response.text
                    print(f"成功获取到内容，长度: {len(content)}")
                    break
            except requests.exceptions.SSLError:
                print(f"SSL错误，尝试第 {i+1}/{retry_count} 次重试")
                if i == retry_count - 1:
                    print("所有重试失败，无法获取木偶域名")
                    return None
                time.sleep(1)
            except Exception as e:
                print(f"请求失败: {str(e)}")
                continue

        if 'response' in locals() and response.status_code == 200:
            patterns = [
                r'(?:https?://)?([a-zA-Z0-9.-]+\.91muou\.icu)',
                r'(?:https?://)?([a-zA-Z0-9.-]+\.666291\.xyz)',
                r'(?:https?://)?([a-zA-Z0-9.-]+\.muouso\.fun)'
            ]
            
            domains = []
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                domains.extend(matches)
            
            domains = list(dict.fromkeys(domains))
            
            if domains:
                print(f"从Telegram获取到木偶域名: {domains}")
                return domains
            else:
                print("未在消息中找到有效的木偶域名")
                return None
    except Exception as e:
        print(f"访问Telegram出错: {str(e)}")
    
    return None

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

def get_wogg_url():
    """获取玩偶链接并测试延迟"""
    try:
        response = requests.get(WOGG_DEFAULT_URL, verify=False)
        if response.status_code == 200:
            domains = []
            notice_pattern = r'<div class="popup-main">(.*?)</div>'
            notice_match = re.search(notice_pattern, response.text, re.DOTALL)
            
            if notice_match:
                domain_patterns = [
                    r'域名\s+((?:www\.)?wogg\.[a-z.]+)',
                    r'备用\s+((?:www\.)?wogg\.[a-z.]+)'
                ]
                
                for pattern in domain_patterns:
                    matches = re.findall(pattern, notice_match.group(1))
                    domains.extend([match.strip() for match in matches])

            domains = list(dict.fromkeys(domains))
            if 'wogg.xxooo.cf' not in domains:
                domains.append('wogg.xxooo.cf')

            print("收集到的玩偶域名:", domains)

            delay_results = []
            for domain in domains:
                url = f"https://{domain.strip('/')}"
                try:
                    delay = test_url_delay(url)
                    if delay:
                        delay_results.append((url, delay))
                        print(f"测试域名 {url} 延迟: {delay:.3f}秒")
                except Exception as e:
                    print(f"测试域名 {url} 时出错: {str(e)}")

            if delay_results:
                delay_results.sort(key=lambda x: x[1])
                best_url, best_delay = delay_results[0]
                print(f"\n选择延迟最低的域名: {best_url} ({best_delay:.3f}秒)")
                return best_url

    except Exception as e:
        print(f"获取玩偶链接失败: {str(e)}")
    
    return WOGG_DEFAULT_URL

def get_mogg_url():
    """获取木偶链接并测试延迟"""
    try:
        domains = get_mogg_domains_from_telegram()
        if domains:
            delay_results = []
            for domain in domains:
                url = f"https://{domain}" if not domain.startswith('http') else domain
                delay = test_url_delay(url)
                if delay:
                    delay_results.append((url.rstrip('/'), delay))
                    print(f"测试木偶域名 {url} 延迟: {delay:.3f}秒")

            if delay_results:
                delay_results.sort(key=lambda x: x[1])
                best_url, best_delay = delay_results[0]
                print(f"\n选择延迟最低的域名: {best_url} ({best_delay:.3f}秒)")
                return best_url

    except Exception as e:
        print(f"获取木偶链接失败: {str(e)}")
    
    return None

def main():
    """主函数：读取API并生成URL JSON"""
    try:
        # 确保工作目录正确
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        print(f"当前工作目录: {os.getcwd()}")
        
        # 读取API文件
        api_path = os.path.join('TVBoxOSC', 'tvbox', 'api.json')
        if not os.path.exists(api_path):
            print(f"错误: 找不到API文件: {api_path}")
            return False

        with open(api_path, 'r', encoding='utf-8') as f:
            api_data = json.load(f)

        # 获取站点信息
        found_sites = []
        sites = api_data.get('sites', [])
        print(f"找到 {len(sites)} 个站点配置")

        # 获取特殊站点链接
        wogg_url = get_wogg_url()
        mogg_url = get_mogg_url()
        
        if wogg_url:
            print(f"找到玩偶链接: {wogg_url}")
            found_sites.append(f"玩偶：{wogg_url}")
        
        if mogg_url:
            print(f"找到木偶链接: {mogg_url}")
            found_sites.append(f"木偶：{mogg_url}")

        # 处理其他站点
        for site in sites:
            name = site.get('name', '')
            if '弹幕' in name:
                for key in site_mappings:
                    if key in name and key not in ['木偶', '玩偶']:
                        ext = site.get('ext', {})
                        site_url = ext.get('site', '') if isinstance(ext, dict) else ext
                        
                        if site_url and site_url.startswith('http'):
                            print(f"找到匹配: {key} -> {site_url}")
                            found_sites.append(f"{key}：{site_url}")
                        break

        # 生成URL数据
        if found_sites:
            url_data = {}
            for site in found_sites:
                cn_name, url = site.split('：')
                if cn_name in site_mappings:
                    url_data[site_mappings[cn_name]] = url.strip()

            # 写入结果
            with open('url.json', 'w', encoding='utf-8') as f:
                json.dump(url_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n成功生成 url.json，包含 {len(url_data)} 个站点:")
            print(json.dumps(url_data, ensure_ascii=False, indent=2))
            return True

        print("未找到任何有效站点")
        return False

    except Exception as e:
        print(f"处理过程中出错: {str(e)}")
        return False

if __name__ == "__main__":
    main()
