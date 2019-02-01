#!/usr/bin/env python
# coding:utf-8
#By T00ls.Net
#
import re
import os
import ssl
import sys
import socket
import chardet
import requests
import argparse
import HTMLParser
from requests.adapters import HTTPAdapter


try:
    requests.packages.urllib3.disable_warnings()
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def out_format(url, information,serverinfo='NULL'):
    for char in ('\r', '\n', '\t'):
        information = information.replace(char, "")
    try:
        if serverinfo != 'NULL':
            message = "{target:50} {server:30} {information}".format(target=url,server=serverinfo.strip(), information=information.strip())
        else:
            message = "{target:50}  {information}".format(target=url, information=information.strip())
    except:
        try:
            message = "{target:50} {information}".format(target=url, information=information.strip())
        except:
            message = "{target:50} {information}".format(target=url, information="NoInformation")
    try:
        print(message)
    except UnicodeError:
        print("{target:50} {information}".format(target=url, information="PrintUnicodeError"))


def html_decoder(html_entries):
    try:
        hp = HTMLParser.HTMLParser()
        return hp.unescape(html_entries)
    except Exception as e:
        return html_entries


def match_title(content):
    title = re.findall("document\.title[\s]*=[\s]*['\"](.*?)['\"]", content, re.I | re.M | re.S)
    if title and len(title) >= 1:
        return title[0]
    else:
        title = re.findall("<title.*?>(.*?)</title>", content, re.I | re.M | re.S)
        if title and len(title) >= 1:
            return title[0]
        else:
            return False


def page_decode(url, html_content):
    raw_content = html_content
    try:
        detRes = chardet.detect(raw_content)
        charset = detRes["encoding"]
        raw_content = raw_content.decode(charset,"ignore")
        html_content = raw_content.encode("utf8",'ignore')
    except:
        return out_format(url, "DecodeHtmlError")
    return html_content


def get_title(url):
    origin = url
    if "://" not in url:
        url = "http://" + url.strip()
    url = url.rstrip("/") + "/"
    # First Try Obtain WebSite Title
    try:
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=1))
        s.mount('https://', HTTPAdapter(max_retries=1))
        req = s.get(url, headers=headers, verify=False, allow_redirects=True, timeout=20)
        html_content = req.content
        sinfo = req.headers['Server']
        req.close()
    except requests.ConnectionError:
        return out_format(origin, "ConnectError")
    except requests.Timeout:
        return out_format(origin, "RequestTimeout")
    except socket.timeout:
        return out_format(origin, "SocketTimeout")
    except requests.RequestException:
        return out_format(origin, "RequestException")
    except Exception as e:
        return out_format(origin, "OtherException")
    html_content = page_decode(url, html_content)
    if html_content:
        title = match_title(html_content)
    else:
        return
        exit(0)
    try:
        if title:
            if re.findall("\$#\d{3,};", title):
                title = html_decoder(title)
            return out_format(origin, title,sinfo)
    except Exception as e:
        return out_format(origin, "FirstTitleError")
    # Find Jump URL
    for pattern in patterns:
        jump = re.findall(pattern, html_content, re.I | re.M)
        if len(jump) == 1:
            if "://" in jump[0]:
                url = jump[0]
            else:
                url += jump[0]
            break
    # Second Try Obtain WebSite Title
    try:
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=1))
        s.mount('https://', HTTPAdapter(max_retries=1))
        req = s.get(url, headers=headers, verify=False, timeout=15)
        html_content = req.content
        sinfo = req.headers['Server']
        req.close()
    except requests.ConnectionError:
        return out_format(origin, "ConnectError")
    except requests.Timeout:
        return out_format(origin, "RequestTimeout")
    except socket.timeout:
        return out_format(origin, "SocketTimeout")
    except requests.RequestException:
        return out_format(origin, "RequestException")
    except Exception as e:
        return out_format(origin, "OtherException")
    html_content = page_decode(url, html_content)
    if html_content:
        title = match_title(html_content)
    else:
        return 
        exit(0)
    try:
        if title:
            if re.findall("[$#]\d{3,};", title):
                title = html_decoder(title)
            return out_format(origin, title,sinfo)
        else:
            return out_format(origin, "NoTitle",sinfo)
    except Exception as e:
        return out_format(origin, "SecondTitleError")


if __name__ == "__main__":
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "close",
    }

    patterns = (
        '<meta[\s]*http-equiv[\s]*=[\s]*[\'"]refresh[\'"][\s]*content[\s]*=[\s]*[\'"]\d+[\s]*;[\s]*url[\s]*=[\s]*(.*?)[\'"][\s]*/?>',
        'window.location[\s]*=[\s]*[\'"](.*?)[\'"][\s]*;',
        'window.location.href[\s]*=[\s]*[\'"](.*?)[\'"][\s]*;',
        'window.location.replace[\s]*\([\'"](.*?)[\'"]\)[\s]*;',
        'window.navigate[\s]*\([\'"](.*?)[\'"]\)',
        'location.href[\s]*=[\s]*[\'"](.*?)[\'"]',
    )

    urls = []
    results = []
    parser = argparse.ArgumentParser(prog='owt.py', description="Obtain WebSite Title")
    parser.add_argument("-t", dest='target', default='urls.txt', help="target with [file-path] or [single-url]")
    #parser.add_argument("-x", dest='threads', default=4, type=int, help="number of concurrent threads")
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    args = parser.parse_args()
    target = args.target
    #threads = args.threads
    if os.path.isfile(target):
        with open(target, 'r') as f:
            for line in f.readlines():
                urls.append(line.strip())
        for i in urls:
            get_title(i)
    else:
        if "://" not in target:
            target = "http://" + target
        get_title(target)
