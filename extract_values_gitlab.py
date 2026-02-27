import re
import requests

def extract_bash_content(html_content):
    """
    从网页内容中提取以bash\r\n开头、下一个\r\n结束的中间内容(+转义符)
    :param html_content: 网页原始文本内容（字符串）
    :return: 匹配到的所有目标内容列表（去重+过滤空内容）
    """
    # 关键修改：匹配bash//r//n开头、//r//n结束的内容
    pattern = r'bash\\r\\n(.*?)\\r\\n'
    matches = re.findall(pattern, html_content, re.DOTALL)
    # 清洗内容：去重 + 过滤空字符串/纯空格的内容
    clean_matches = []
    for content in set(matches):  # 去重
        stripped_content = content.strip()
        if stripped_content:  # 过滤空内容
            clean_matches.append(stripped_content)
    return clean_matches

def write_to_txt(content_list, file_path="extracted_bash.txt"):
    """
    仅将提取到的干净结果写入TXT（无任何冗余信息）
    :param content_list: 提取到的干净内容列表
    :param file_path: 输出的TXT文件路径（默认当前目录）
    """
    if not content_list:  # 无有效内容时不写入
        return
    try:
        # 以"追加模式"打开，UTF-8编码防乱码
        with open(file_path, "a", encoding="utf-8") as f:
            # 仅写入纯结果，每条结果单独一行
            for content in content_list:
                f.write(f"{content}\n")
        print(f"✅ 已将{len(content_list)}条结果写入TXT：{file_path}")
    except Exception as e:
        print(f"❌ 写入TXT失败：{str(e)}")

def extract_from_urls(url_list, timeout=10):
    """
    顺序执行一次提取多个URL的目标内容，仅输出纯结果到TXT
    :param url_list: 待提取的URL列表
    :param timeout: 单个URL请求超时时间（秒），默认10秒
    """
    # 模拟浏览器请求头（规避GitLab反爬）
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }

    print(f"===== 开始顺序提取 {len(url_list)} 个网页的纯结果 =====\n")
    
    # 顺序遍历所有URL，仅执行一次
    for idx, url in enumerate(url_list, 1):
        print(f"\n【第{idx}个网页】URL: {url}")
        try:
            response = requests.get(
                url, 
                headers=headers,
                timeout=timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # 提取并清洗内容
            content_list = extract_bash_content(response.text)
            
            # 输出控制台+写入纯结果到TXT
            if content_list:
                print(f"✅ 提取到 {len(content_list)} 条干净结果：")
                for i, content in enumerate(content_list, 1):
                    print(f"  {i}. {content}")
                # 仅写入纯结果到TXT
                write_to_txt(content_list)
            else:
                print("❌ 未提取到符合条件的有效内容")
        
        except requests.exceptions.Timeout:
            print(f"❌ 请求超时（超时时间：{timeout}秒）")
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP错误：{e}")
        except requests.exceptions.ConnectionError:
            print(f"❌ 连接失败（网址无法访问）")
        except Exception as e:
            print(f"❌ 未知错误：{str(e)}")
    
    print(f"\n===== 所有 {len(url_list)} 个网页提取完成，程序结束 ======")

if __name__ == "__main__":
    # -------------------------- 配置项（按需修改） --------------------------
    TARGET_URLS = [
        # GitHub抽风、改为gitlab
        "https://gitlab.com/zhifan999/fq/-/wikis/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7",
        "https://gitlab.com/zhifan999/fq/-/wikis/ss%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7",
    ]
    REQUEST_TIMEOUT = 10  # 单个URL请求超时时间（秒）
    OUTPUT_TXT_PATH = "gitlab.txt"  # 纯结果输出路径
    # -----------------------------------------------------------------------

    extract_from_urls(
        url_list=TARGET_URLS,
        timeout=REQUEST_TIMEOUT
    )