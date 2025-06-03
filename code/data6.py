import requests
from lxml import etree


with open("out11.txt","r") as file:
    lines=file.readlines()
file.close()
flag=93

for line in lines[93:]:
    line = line.strip()
    # print(line)
    flag+=1

    inurl = line

    response = requests.get(inurl)
    root = etree.HTML(response.content)
    items = root.xpath(
        "//table[@class='commit-info']/tr[3]//td[@class='oid']/a/text()")

    print(items)
    print(flag)


