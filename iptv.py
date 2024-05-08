#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from datetime import datetime
import requests
import tools
import concurrent.futures
from lxml import etree

engine_url = "http://tonkiang.us/"

# 初始化m3u集合数据
data_dict = {}
# 获取工具类
T = tools.Tools()

# 爬取直播源引擎
groups = ['CCTV1', "CCTV2", "CCTV3", "CCTV4", "CCTV5",
          "CCTV6", "CCTV7", "CCTV8", "CCTV9", "CCTV10",
          "CCTV11", "CCTV12", "CCTV13", "CCTV14", "CCTV15",
          "CCTV16", "CCTV17", "山东卫视", "山东齐鲁", "山东综艺", "山东影视", "山东体育", "山东农科","山东公共","山东生活",
          "河北卫视", "河南卫视", "吉林卫视", "辽宁卫视", "黑龙江卫视", "江苏卫视","浙江卫视","四川卫视",
          "江西卫视", "湖北卫视", "湖南卫视", "东南卫视", "安徽卫视", "云南卫视", "贵州卫视",
          "重庆卫视", "山西卫视", "陕西卫视", "甘肃卫视", "宁夏卫视", "新疆卫视", "内蒙古卫视","青海卫视",
          "西藏卫视", "广东卫视", "广西卫视", "深圳卫视", "东方卫视", "北京卫视", "天津卫视", "海南卫视"]

# 爬取CCTV频道资源
def spider_source():
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for group_addr in groups:
            executor.submit(jiexi_html,group_addr)
            # list(executor.map(jiexi_html, groups))
            time.sleep(3)
            print('等待3秒后执行')
    ss = dict(sorted(data_dict.items()))
    data_dict.update(ss)

    print(f'总计耗时{round(time.time() - start_time, 4)}秒')

def jiexi_html(group_addr):
    # 获取当前时间
    current_time = datetime.now()
    timeout_cnt = 0
    url = engine_url + "?page=1&ch=" + group_addr
    headers = {
        "User-Agent": 'Apifox/1.0.0 (https://apifox.com)',
        'Cookie': "_ga=GA1.1.1704509184.1707655763; HstCfa4835429=1707655763698; HstCmu4835429=1707655763698; HstCnv4835429=2; REFERER=7640374; HstCns4835429=4; ckip1=123.10.78.63%7C119.123.216.197%7C183.1.249.4%7C121.24.98.119%7C123.187.59.90%7C101.75.215.122%7C123.52.86.251%7C42.225.147.168; ckip2=183.133.106.81%7C123.118.48.158%7C183.185.65.222%7C183.185.12.166%7C61.240.56.100%7C171.116.114.212%7C222.129.32.251%7C60.223.72.251; HstCla4835429=1707697762750; HstPn4835429=14; HstPt4835429=15; _ga_8KY4MGK2FJ=GS1.1.1707695177.2.1.1707697765.0.0.0"
    }
    # 发起HTTP请求获取网页内容
    try:
        response = requests.get(url, timeout=15, headers=headers)
        # 处理响应
        response.raise_for_status()
        # 检查请求是否成功
        html_content = response.text
        iptv_html = etree.HTML(html_content)
        # result_titles = iptv_html.xpath('//*[@style="float: left;"]//text()')
        result_urls = iptv_html.xpath('//*[@style="padding-left: 6px;"]//text()')
        print(f"{current_time} 搜索频道直播源：{url}")

        # 初始化列表数据
        data_list = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(T.check_iptv_v2, result_urls))
        for url, status in results:
            # print(status, url)
            if status == 200:
                data_list.append(url)
        data_dict[f'{group_addr}'] = data_list
    except (requests.Timeout, requests.RequestException) as e:
        timeout_cnt += 1
        print(f"{current_time} 请求发生超时，异常次数：{timeout_cnt}")

# 拼接m3u方法
def format_title_url():
    m3u = '#EXTM3U\n'
    for key in groups:
        url_list = data_dict[key]
        for url in url_list:
            # 拼接字符串
            m3u += f'''#EXTINF:-1,tvg-id="{key}" tvg-name="{key}" tvg-logo="https://epg.112114.eu.org/logo/{key}.png" group-title="自用源",{key}\n{url}\n'''
        m3u_bytes = m3u.encode('utf-8')
        with open('m3u/iptv.m3u', 'wb') as f:
            f.write(m3u_bytes)
    print('文件写入成功')


# 执行主程序函数
if __name__ == '__main__':
    spider_source()
    format_title_url()
