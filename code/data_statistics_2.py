import re
import requests
from lxml import etree

from urllib.parse import urlparse, parse_qs

def remove_query_param(url):
    # 解析 URL
    parsed_url = urlparse(url)
    # 只保留路径部分，丢弃查询参数
    return parsed_url.path

def extract_id(url):
    match = re.search(r'=([a-f0-9]+)$', url)
    if match:
        return match.group(1)
    return None

flag=0

with open("out11.txt","r")as file:
    lines=file.readlines()
file.close()

for line in lines:
    line=line.strip()
    link_list = []
    encoding = extract_id(line)
    print(encoding)
    encoding = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=" + encoding
    if encoding:
        flag+=1
        response = requests.get(encoding)
        root = etree.HTML(response.content)
        filename = root.xpath("//table[@class='diffstat']/tr")
        for i in filename:
            s1 = i.xpath("./td[@class='upd']/a/text()")
            s2 = i.xpath("./td[@class='del']/a/text()")
            s3 = i.xpath("./td[@class='add']/a/text()")
            s4 = i.xpath("./td[@class='mov']/a/text()")
            if s1 == [] and s2 != [] or s3 != [] or s4 != []:
                if s2 == [] and s3 == []:
                    s = s4
                elif s3 == [] and s4 == []:
                    s = s2
                else:
                    s = s3

                path = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/" + s[0]
                response1 = requests.get(path)
                root1 = etree.HTML(response1.content)
                commits = root1.xpath("//div[@class='content']//table[@class='list nowrap']/tr")

                for j in commits:
                    commit = j.xpath("./td[2]/a/@href")

                    if (commit != []):
                        link_list.append("https://git.kernel.org" + commit[0])

                next = root1.xpath("//div[@class='content']//ul[@class='pager']/li[1]/a/text()")
                if next != []:
                    if next[0] == "[next]":
                        num = 200
                        pathnext = path = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/" + s[
                            0] + "?ofs=" + str(num)
                        response2 = requests.get(pathnext)
                        root2 = etree.HTML(response2.content)
                        commits = root2.xpath("//div[@class='content']//table[@class='list nowrap']/tr")

                        for j in commits:
                            commit = j.xpath("./td[2]/a/@href")

                            if (commit != []):
                                link_list.append("https://git.kernel.org" + commit[0])

                        next1 = root2.xpath("//div[@class='content']//ul[@class='pager']/li[2]/a/text()")
                        while next1 != [] and next1[0] == "[next]":
                            num = num + 200
                            pathnext = path = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/" + \
                                              s[0] + "?ofs=" + str(num)
                            response2 = requests.get(pathnext)
                            root2 = etree.HTML(response2.content)
                            commits = root2.xpath("//div[@class='content']//table[@class='list nowrap']/tr")

                            for j in commits:
                                commit = j.xpath("./td[2]/a/@href")

                                if (commit != []):
                                    link_list.append("https://git.kernel.org" + commit[0])

                            next1 = root2.xpath("//div[@class='content']//ul[@class='pager']/li[2]/a/text()")
            else:
                s = i.xpath("./td[@class='upd']/a/text()")
                path = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/" + s[0]
                response1 = requests.get(path)
                root1 = etree.HTML(response1.content)
                commits = root1.xpath("//div[@class='content']//table[@class='list nowrap']/tr")

                for j in commits:
                    commit = j.xpath("./td[2]/a/@href")

                    if (commit != []):
                        link_list.append("https://git.kernel.org" + commit[0])

                next = root1.xpath("//div[@class='content']//ul[@class='pager']/li[1]/a/text()")
                if next != []:
                    if next[0] == "[next]":
                        num = 200
                        pathnext = path = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/" + s[
                            0] + "?ofs=" + str(num)
                        response2 = requests.get(pathnext)
                        root2 = etree.HTML(response2.content)
                        commits = root2.xpath("//div[@class='content']//table[@class='list nowrap']/tr")

                        for j in commits:
                            commit = j.xpath("./td[2]/a/@href")

                            if (commit != []):
                                link_list.append("https://git.kernel.org" + commit[0])

                        next1 = root2.xpath("//div[@class='content']//ul[@class='pager']/li[2]/a/text()")
                        while next1 != [] and next1[0] == "[next]":
                            num = num + 200
                            pathnext = path = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/" + \
                                              s[0] + "?ofs=" + str(num)
                            response2 = requests.get(pathnext)
                            root2 = etree.HTML(response2.content)
                            commits = root2.xpath("//div[@class='content']//table[@class='list nowrap']/tr")

                            for j in commits:
                                commit = j.xpath("./td[2]/a/@href")

                                if (commit != []):
                                    link_list.append("https://git.kernel.org" + commit[0])

                            next1 = root2.xpath("//div[@class='content']//ul[@class='pager']/li[2]/a/text()")
        with open("out11_count.txt","a")as file:
            file.write(str(len(link_list)))
            file.write("\n")
        file.close()
        print(len(link_list))
        print("flag:",flag)

    else:
        flag+=1
