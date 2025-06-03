# -*-coding:utf-8-
#out source.txt
import requests
from lxml import etree
import os



def substring_from_position(input_string,start_position):
    return input_string[start_position:]

with open("out4.txt","r")as file:
    lines=file.readlines()
    current_id=None
    for line in lines[6536:]:
        line=line.strip()
        if line.startswith("CVE"):
            current_id=line
            #print(line)
            continue
        if line.startswith("https://github.com") :
            if "commit/" in line:
                id=line.split("commit/",1)[1]
            link="https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id="+id
            response = requests.get(link)
            root = etree.HTML(response.content)
            i = root.xpath("//table[@summary='diffstat' and @class='diffstat']")
            for j in i:
                p=j.xpath("//tr/td[@class='mode']/text()")
            if len(p)==1:
                with open("out5.txt","a")as file1:
                    file1.write(current_id)
                    file1.write("\n")
                    file1.write(id)
                    file1.write("\n")
                file1.close()
                print(current_id)
                print(id)


        if line.startswith("https://git.kernel.org") or line.startswith("http://git.kernel.org"):
            if "id=" in line:
                id=line.split("id=",1)[1]
            elif "%3Bh=" in line:
                id=line.split("%3Bh=",1)[1]
            link = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=" + id
            response = requests.get(link)
            root = etree.HTML(response.content)
            i = root.xpath("//table[@summary='diffstat' and @class='diffstat']")
            for j in i:
                p = j.xpath("//tr/td[@class='mode']/text()")
            if len(p) == 1:
                with open("out5.txt","a")as file1:
                    file1.write(current_id)
                    file1.write("\n")
                    file1.write(id)
                    file1.write("\n")
                file1.close()
                print(current_id)
                print(id)










file.close()

