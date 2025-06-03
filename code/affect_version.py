import re
import requests
from lxml import etree
import os


def find_link(true_version,false_version):
    log_1_0 = []
    log_link = "https://mirrors.edge.kernel.org/pub/linux/kernel/v1.0/"
    # print(cve_link)
    response = requests.get(log_link)
    root = etree.HTML(response.content)
    items = root.xpath("//body/pre/a")
    for i in items:
        s = i.xpath('./@href')
        if "ChangeLog" in s[0] and "sign" not in s[0]:
            log_1_0.append(s[0])


    log_3 = []
    log_link="https://mirrors.edge.kernel.org/pub/linux/kernel/v3.x/"
    #print(cve_link)
    response = requests.get(log_link)
    root = etree.HTML(response.content)
    items = root.xpath("//body/pre/a")
    for i in items:
        s = i.xpath('./@href')
        if "ChangeLog" in s[0] and "sign" not in s[0]:
            log_3.append(s[0])

    log_4=[]
    log_link = "https://mirrors.edge.kernel.org/pub/linux/kernel/v4.x/"
    # print(cve_link)
    response = requests.get(log_link)
    root = etree.HTML(response.content)
    items = root.xpath("//body/pre/a")
    for i in items:
        s = i.xpath('./@href')
        if "ChangeLog" in s[0] and "sign" not in s[0]:
            log_4.append(s[0])

    log_5=[]
    log_link = "https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/"
    # print(cve_link)
    response = requests.get(log_link)
    root = etree.HTML(response.content)
    items = root.xpath("//body/pre/a")
    for i in items:
        s = i.xpath('./@href')
        if "ChangeLog" in s[0] and "sign" not in s[0]:
            log_5.append(s[0])

    log_6=[]
    log_link = "https://mirrors.edge.kernel.org/pub/linux/kernel/v6.x/"
    # print(cve_link)
    response = requests.get(log_link)
    root = etree.HTML(response.content)
    items = root.xpath("//body/pre/a")
    for i in items:
        s = i.xpath('./@href')
        if "ChangeLog" in s[0] and "sign" not in s[0]:
            log_6.append(s[0])





commit_id="734efb467b31e56c2f9430590a9aa867ecf3eea1"
find_link("2.8.16","2.8.33")