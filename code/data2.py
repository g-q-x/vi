# -*-coding:utf-8-
#out source.txt
import requests
from lxml import etree
import os

count=0

def substring_from_position(input_string,start_position):
    return input_string[start_position:]

with open("out13.txt","r")as file:
    lines=file.readlines()
    for line in lines:
        line=line.strip()
        #print(line)

        filename=substring_from_position(line,33)
        print(filename)


        inurl=line

        response = requests.get(inurl)
        root = etree.HTML(response.content)

        items = root.xpath("//div[@id='vulnHyperlinksPanel']//table[@class='table table-striped table-condensed table-bordered detail-table']/tbody/tr")
        #print(items)

        for i in items:
            s = i.xpath('./td/a/@href')
            if "https://github.com/uclouvain/openjpeg/commit/" in s[0]:
                count+=1
                # with open("out4.txt","a") as file1:
                #     file1.write(filename)
                #     file1.write('\n')
                #     file1.write(s[0])
                #     file1.write('\n')
                # file1.close()
                print(s[0])
                print(count)
            # if "github.com" in s[0]:
            #     count += 1
            #     # with open("out4.txt","a") as file1:
            #     #     file1.write(filename)
            #     #     file1.write('\n')
            #     #     file1.write(s[0])
            #     #     file1.write('\n')
            #     # file1.close()
            #     print(s[0])
            #     print(count)



file.close()

print(count)