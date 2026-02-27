import requests
from bs4 import BeautifulSoup

def extract_from_single_url(url):
    """提取单个网页的目标属性值，仅返回值列表"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # 提取目标值，过滤空值
        target_values = [
            elem.get('data-snippet-clipboard-copy-content')
            for elem in soup.find_all(True)
            if elem.get('data-snippet-clipboard-copy-content')
        ]
        
        print(f"✅ 成功提取 {url}：{len(target_values)} 个值")
        return target_values
    
    except requests.exceptions.RequestException as e:
        print(f"❌ 提取 {url} 失败：{str(e)}")
        return []

def batch_extract_to_pure_txt(url_list, save_path="pure_results.txt"):
    """批量提取多个网页的值，仅将纯结果写入TXT（每行一个值）"""
    # 1. 清空文件（确保无旧数据）
    with open(save_path, 'w', encoding='utf-8') as f:
        pass  # 仅清空，不写入任何内容
    
    total_count = 0
    # 2. 遍历所有URL，提取值并追加写入（仅写纯值）
    for url in url_list:
        values = extract_from_single_url(url)
        # 追加写入当前URL的纯结果（每行一个值）
        with open(save_path, 'a', encoding='utf-8') as f:
            for value in values:
                f.write(f"{value}\n")
        total_count += len(values)
    
    print(f"\n📁 纯结果已写入：{save_path}，总计提取到 {total_count} 个值")

# 示例使用
if __name__ == "__main__":
    # 替换为你要处理的多个URL
    target_urls = [
        "https://github.com/Alvin9999-newpac/fanqiang/wiki/ss%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7",
        "https://github.com/Alvin9999-newpac/fanqiang/wiki/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7",
        # 可继续添加更多URL...
        # wiki页面会间断消失TODO
    ]
    
    # 调用函数，自定义保存路径（可选）
    batch_extract_to_pure_txt(
        url_list=target_urls,
        save_path="only_results.txt"  # TXT仅包含纯结果
    )