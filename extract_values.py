import requests
import re
from bs4 import BeautifulSoup
import time

def extract_from_single_url(url, retry_on_invalid=True):
    """
    提取单个网页的目标属性值，仅返回符合「字母/数字+://」格式的列表
    :param url: 目标URL
    :param retry_on_invalid: 提取到无效值时是否重新获取
    :return: list - 符合格式的属性值列表
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://github.com/'
    }
    
    # 定义通用格式校验函数：匹配 字母/数字(至少1个) + :// 开头的格式
    # 正则说明：^[a-zA-Z0-9]+://  → 以大小写字母/数字开头，后跟://
    def is_valid_format(value):
        if not value:
            return False
        # 先去除首尾空白字符，再匹配正则
        cleaned_value = value.strip()
        return re.match(r'^[a-zA-Z0-9]+://', cleaned_value) is not None
    
    # 最大重试次数（包括初始获取+格式校验失败重试）
    max_total_tries = 3
    current_try = 0
    
    while current_try < max_total_tries:
        current_try += 1
        try:
            response = requests.get(
                url, 
                headers=headers, 
                timeout=15,
                allow_redirects=True
            )
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # 提取所有目标值并过滤空值
            raw_values = [
                elem.get('data-snippet-clipboard-copy-content')
                for elem in soup.find_all(True)
                if elem.get('data-snippet-clipboard-copy-content')
            ]
            # 格式校验：仅保留「字母/数字+://」开头的值
            valid_values = [v for v in raw_values if is_valid_format(v)]
            
            # 校验通过：返回有效结果
            if valid_values:
                print(f"✅ 第 {current_try} 次获取 {url}：提取到 {len(valid_values)} 个有效值（符合 vless:///vmess:///v2ray:///ss:// 等格式）")
                return valid_values
            # 校验失败：判断是否重试
            else:
                if retry_on_invalid and current_try < max_total_tries:
                    print(f"⚠️ 第 {current_try} 次获取 {url}：提取到 {len(raw_values)} 个值，但均不符合「字母/数字+://」格式，即将重试...")
                    time.sleep(3)  # 重试前等待3秒，避免高频请求
                else:
                    print(f"❌ 第 {current_try} 次获取 {url}：最终未提取到符合格式的值（共提取到 {len(raw_values)} 个无效值）")
                    return []
        
        except requests.exceptions.RequestException as e:
            if current_try < max_total_tries:
                print(f"⚠️ 第 {current_try} 次获取 {url} 失败（网络/请求错误）：{str(e)}，即将重试...")
                time.sleep(3)
            else:
                print(f"❌ 第 {current_try} 次获取 {url} 最终失败：{str(e)}")
                return []

def batch_extract_to_pure_txt(url_list, save_path="only_results.txt"):
    """批量提取多个网页的值，仅将符合格式的纯结果写入TXT（每行一个值）"""
    # 1. 清空文件（确保无旧数据）
    with open(save_path, 'w', encoding='utf-8') as f:
        pass  # 仅清空，不写入任何内容
    
    total_count = 0
    # 2. 遍历所有URL，提取符合格式的值并追加写入
    for url in url_list:
        valid_values = extract_from_single_url(url, retry_on_invalid=True)
        # 追加写入符合格式的结果
        with open(save_path, 'a', encoding='utf-8') as f:
            for value in valid_values:
                f.write(f"{value}\n")
        total_count += len(valid_values)
        # URL间间隔，避免反爬
        time.sleep(1)
    
    print(f"\n📁 最终结果已写入：{save_path}，总计提取到 {total_count} 个符合「字母/数字+://」格式的值")

# 示例使用
if __name__ == "__main__":
    # 目标URL列表（GitHub Wiki页面）
    target_urls = [
        "https://github.com/Alvin9999-newpac/fanqiang/wiki/ss%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7",
        "https://github.com/Alvin9999-newpac/fanqiang/wiki/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7",
        # 可继续添加更多URL...
    ]
    
    # 调用函数，自定义保存路径
    batch_extract_to_pure_txt(
        url_list=target_urls,
        save_path="only_results.txt"
    )