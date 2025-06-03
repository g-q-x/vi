import re
import requests
from lxml import etree
import os

#找到commit-id
def extract_commit_hash(url):
    # 定义一个正则表达式来匹配提交号
    pattern = r'/commit(?:/\?id=|/)([0-9a-fA-F]{40})'
    # 使用正则表达式搜索URL
    match = re.search(pattern, url)
    if match==None:
        pattern = r'id=([a-f0-9]+)$'
        match = re.search(pattern, url)
    if match==None:
        match = re.search(r'/([0-9a-fA-F]+)$', url)
    if match==None:
        match = re.search(r'[^/]+$', url)
    # 如果匹配成功，返回提交号
    if match:
        return match.group(1)
    else:
        return None

#找到commit-id
def find_link(CVE_id):
    cve_link="https://nvd.nist.gov/vuln/detail/"+CVE_id
    #print(cve_link)
    response = requests.get(cve_link)
    root = etree.HTML(response.content)
    items = root.xpath("//div[@id='vulnHyperlinksPanel']//table[@class='table table-striped table-condensed table-bordered detail-table']/tbody/tr")
    for i in items:
        s = i.xpath('./td/a/@href')
        if "https://git.kernel.org" in s[0] or "https://github.com" in s[0]:
            commit=extract_commit_hash(s[0])
            return commit

#创建文件夹
def create_folder(path):
    try:
        # 使用os.makedirs创建文件夹
        os.makedirs(path, exist_ok=True)
        print(f"文件夹 '{path}' 创建成功。")
    except Exception as e:
        print(f"创建文件夹时发生错误: {e}")

#创建补丁前后的ab文件
def ab_file(hyper_link,CVE_id):
    response = requests.get(hyper_link)
    root = etree.HTML(response.content)
    file_ab = root.xpath("//table[@class='diff']/tr/td//div[@class='head']")
    for i in file_ab:
        #找到修改之前的文件
        s_a_name = i.xpath("./a[1]/text()")
        s_a_name[0]=s_a_name[0].replace('/','#')
        s_a = i.xpath("./a[1]/@href")
        response1 = requests.get("https://git.kernel.org"+s_a[0])
        root1 = etree.HTML(response1.content)
        plain = root1.xpath("//div[@class='content']/a/@href")
        response2 = requests.get("https://git.kernel.org"+plain[0])
        with open( "CVE/"+CVE_id+"/af#" + str(s_a_name[0]), "w") as file:
            file.write(response2.text)
        file.close()

        #找到修改之后的文件
        s_b_name = i.xpath("./a[2]/text()")
        s_b_name[0] = s_b_name[0].replace('/', '#')
        s_b = i.xpath("./a[2]/@href")
        response1 = requests.get("https://git.kernel.org" + s_b[0])
        root1 = etree.HTML(response1.content)
        plain = root1.xpath("//div[@class='content']/a/@href")
        response2 = requests.get("https://git.kernel.org" + plain[0])

        with open("CVE/"+CVE_id+"/bf#" + str(s_b_name[0]), "w") as file:
            file.write(response2.text)
        file.close()

def get_patch(link,cve_id):
    response = requests.get(link)
    root = etree.HTML(response.content)
    diffs = root.xpath("//table[@class='diff']/tr/td//div")
    for diff in diffs:
        if diff.xpath("@class") == ['hunk']:
            with open("CVE/" + cve_id + "/patch.txt", "a") as file:
                file.write(diff.xpath("text()")[0])
                file.write("\n")
            file.close()

        if diff.xpath("@class") == ['add']:
            with open("CVE/" + cve_id + "/patch.txt", "a") as file:
                file.write(diff.xpath("text()")[0])
                file.write("\n")
            file.close()

        if diff.xpath("@class") == ['del']:
            with open("CVE/" + cve_id + "/patch.txt", "a") as file:
                file.write(diff.xpath("text()")[0])
                file.write("\n")
            file.close()

        if diff.xpath("@class") == ['ctx']:
            with open("CVE/" + cve_id + "/patch.txt", "a") as file:
                file.write(diff.xpath("text()")[0])
                file.write("\n")
            file.close()






#下载文件
def load_file(cve_id):
    # 找到对应的patch提交链接
    link = find_link(cve_id)
    hyper_link = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=" + str(link)
    #创建CVE-id文件夹
    #create_folder("CVE/"+cve_id)
    #下载补丁前后文件
    #ab_file(hyper_link,cve_id)
    #下载补丁
    #get_patch(hyper_link,cve_id)


def main():
    # 指定CVE_id
    CVE_id = "CVE-2020-25284"
    load_file(CVE_id)
    #get_patch("https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/net/netfilter/nf_tables_api.c?id=4a9e12ea7e70223555ec010bec9f711089ce96f6","test")

if __name__ == "__main__":
    main()

