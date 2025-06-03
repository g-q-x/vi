import requests
from lxml import etree


with open("out1.txt","r") as file:
    lines=file.readlines()
file.close()
flag=6918
def substring_from_position(input_string,start_position):
    return input_string[start_position:]
for line in lines[6919:]:
    line = line.strip()
    # print(line)
    flag+=1
    filename = substring_from_position(line, 33)

    inurl = line

    response = requests.get(inurl)
    root = etree.HTML(response.content)

    items = root.xpath(
        "//div[@id='vulnHyperlinksPanel']//table[@class='table table-striped table-condensed table-bordered detail-table']/tbody/tr")
    # print(items)

    for i in items:
        s = i.xpath('./td/a/@href')
        with open("out7.txt","a") as file:
            file.write(s[0])
            file.write("\n")
        file.close()
        print(s[0])
    print(flag)