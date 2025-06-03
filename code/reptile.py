# -*-coding:utf-8-
#out source.txt
import requests
from lxml import etree
import os

count=0

def substring_from_position(input_string,start_position):
    return input_string[start_position:]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# with open("out8.txt","r")as file:
#     lines=file.readlines()
#     for line in lines:
line = "https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?id=000099d71648504fb9c7a4616f92c2b70c3e44ec"
# line=line.strip()
print("1")
print(line)

# filename=substring_from_position(line,33)
# print(filename)


inurl=line

response = requests.get(inurl,headers=headers)
print(response.text)
root = etree.HTML(response.content)

items = root.xpath("//div[@class='commit-subject']")
print(items)

        # for i in items:
        #     s = i.xpath('./td/a/@href')
        #     if "https://github.com/uclouvain/openjpeg/commit/" in s[0]:
        #         count+=1
        #         # with open("out4.txt","a") as file1:
        #         #     file1.write(filename)
        #         #     file1.write('\n')
        #         #     file1.write(s[0])
        #         #     file1.write('\n')
        #         # file1.close()
        #         print(s[0])
        #         print(count)
        #     # if "github.com" in s[0]:
        #     #     count += 1
        #     #     # with open("out4.txt","a") as file1:
        #     #     #     file1.write(filename)
        #     #     #     file1.write('\n')
        #     #     #     file1.write(s[0])
        #     #     #     file1.write('\n')
        #     #     # file1.close()
        #     #     print(s[0])
        #     #     print(count)



# file.close()

