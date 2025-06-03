import re
from urllib.parse import urlparse
import requests
from lxml import etree

def extract_id(url):
    match = re.search(r'/([a-f0-9]+)$', url)
    if match:
        return match.group(1)
    return None

flag=386

with open("out9.txt","r")as file:
    lines=file.readlines()
file.close()
for line in lines[386:]:
    line=line.strip()
    #print(line)
    encoding = extract_id(line)
    if encoding:
        flag+=1
        encoding="https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id="+encoding
        response = requests.get(encoding)
        root = etree.HTML(response.content)
        items = root.xpath(
            "//div[@class='diffstat-summary']/text()")
        with open("out9_output.txt","a")as file:
            file.write(str(items))
            file.write("\n")
        file.close()
        print(items)
        print(flag)
    else:
        flag+=1
        print(flag)