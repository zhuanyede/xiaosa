#!/usr/bin/env python3
import json
import re
import time
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
                    verify=False,  # 禁用SSL验证
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
                time.sleep(1)  # 重试前等待
            except Exception as e:
                print(f"请求失败: {str(e)}")
                continue

        if 'response' in locals() and response.status_code == 200:
            # 使用更宽松的匹配模式找到当前使用的域名
            patterns = [
                r'(?:https?://)?([a-zA-Z0-9.-]+\.91muou\.icu)',
                r'(?:https?://)?([a-zA-Z0-9.-]+\.666291\.xyz)',
                r'(?:https?://)?([a-zA-Z0-9.-]+\.muouso\.fun)'
            ]
            
            domains = []
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                domains.extend(matches)
            
            # 去重处理
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
    """测试URL的延迟,返回延迟时间(秒)或None"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return time.time() - start_time
        return None
    except:
        return None

def get_wogg_url():
    """获取玩偶链接并测试延迟"""
    try:
        response = requests.get(WOGG_DEFAULT_URL)
        if response.status_code == 200:
            domains = []
            # 查找包含公告内容的div
            notice_pattern = r'<div class="popup-main">(.*?)</div>'
            notice_match = re.search(notice_pattern, response.text, re.DOTALL)
            
            if notice_match:
                # 提取域名和备用域名
                domain_patterns = [
                    r'域名\s+((?:www\.)?wogg\.[a-z.]+)',
                    r'备用\s+((?:www\.)?wogg\.[a-z.]+)'
                ]
                
                for pattern in domain_patterns:
                    matches = re.findall(pattern, notice_match.group(1))
                    for match in matches:
                        # 确保域名格式正确
                        domain = match.strip()
                        if domain not in domains:
                            domains.append(domain)

            # 确保默认域名在列表中
            fixed_domains = ['wogg.xxooo.cf']
            for domain in fixed_domains:
                if domain not in domains:
                    domains.append(domain)

            print("收集到的玩偶域名:", domains)

            # 测试所有域名的延迟并保存结果
            delay_results = []
            for domain in domains:
                url = f"https://{domain.strip('/')}"
                try:
                    delay = test_url_delay(url)
                    if delay:
                        delay_results.append((url, delay))
                        print(f"测试域名 {url} 延迟: {delay:.3f}秒")
                    else:
                        print(f"域名 {url} 测试失败")
                except Exception as e:
                    print(f"测试域名 {url} 时出错: {str(e)}")

            if delay_results:
                # 按延迟排序并显示结果
                delay_results.sort(key=lambda x: x[1])
                print("\n玩偶域名延迟测试结果（从低到高）:")
                for url, delay in delay_results:
                    print(f"域名: {url:30} 延迟: {delay:.3f}秒")
                
                best_url, best_delay = delay_results[0]
                print(f"\n选择延迟最低的域名: {best_url} ({best_delay:.3f}秒)")
                return best_url

    except Exception as e:
        print(f"获取玩偶链接失败: {str(e)}")
    
    return WOGG_DEFAULT_URL

def get_mogg_url():
    """获取木偶链接并测试延迟"""
    try:
        # 从Telegram获取域名列表
        domains = get_mogg_domains_from_telegram()
        
        if domains:
            # 测试所有域名的延迟并保存结果
            delay_results = []
            for domain in domains:
                url = f"https://{domain}" if not domain.startswith('http') else domain
                delay = test_url_delay(url)
                if delay:
                    delay_results.append((url.rstrip('/'), delay))
                    print(f"测试木偶域名 {url} 延迟: {delay:.3f}秒")

            if delay_results:
                # 按延迟排序
                delay_results.sort(key=lambda x: x[1])
                print("\n木偶域名延迟测试结果（从低到高）:")
                for url, delay in delay_results:
                    print(f"域名: {url:30} 延迟: {delay:.3f}秒")
                
                best_url, best_delay = delay_results[0]
                print(f"\n选择延迟最低的域名: {best_url} ({best_delay:.3f}秒)")
                return best_url
        else:
            print("未能从Telegram获取木偶域名")

    except Exception as e:
        print(f"获取木偶链接失败: {str(e)}")
    
    return None

def get_urls(api_content):
    """从API内容获取URL数据"""
    try:
        # 解析API内容
        api_data = json.loads(api_content)
        found_sites = []
        sites = api_data.get('sites', [])
        print(f"找到 {len(sites)} 个站点配置")

        # 获取玩偶链接和木偶链接
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
                display_name = None
                for key in site_mappings.keys():
                    if key in name and key not in ['木偶', '玩偶']:
                        display_name = key
                        break
                
                if display_name:
                    ext = site.get('ext', {})
                    site_url = ''
                    if isinstance(ext, dict):
                        site_url = ext.get('site', '')
                    elif isinstance(ext, str):
                        site_url = ext
                    
                    if site_url and site_url.startswith('http'):
                        print(f"找到匹配: {display_name} -> {site_url}")
                        found_sites.append(f"{display_name}：{site_url}")

        # 转换数据为字典格式
        url_data = {}
        for site in found_sites:
            cn_name, url = site.split('：')
            if cn_name in site_mappings:
                url_data[site_mappings[cn_name]] = url.strip()

        return url_data

    except Exception as e:
        print(f"处理URL数据时出错：{str(e)}")
        return None

if __name__ == "__main__":
    # 从标准输入读取API内容
    import sys
    api_content = sys.stdin.read()
    result = get_urls(api_content)
    if result:
        # 将结果输出到标准输出
        print(json.dumps(result, ensure_ascii=False, indent=2))
