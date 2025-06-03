#out out1.txt
import requests
from lxml import etree
headers = { 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,und;q=0.8,en;q=0.7',
            'Cache-Control': 'max-age=0', 'Connection': 'keep-alive',
            'If-Modified-Since': 'Sat, 23 Sep 2023 03:31:30 GMT', 'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '?1', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', }
params = { 'h': 'v5.17', }


inurl="https://nvd.nist.gov/vuln/search/results?isCpeNameSearch=false&query=OpenJPEG&results_type=overview&form_type=Basic&search_type=all&startIndex="
for num in range(1,6):
    print("================正在爬虫第"+str(num)+"页数据==================")
    num=(num-1)*20
    outurl=inurl+str(num)
    #print(outurl)

    response = requests.get( outurl,params=params, headers=headers, )
    root = etree.HTML(response.content)

    items = root.xpath("//div[@id='row']//table[@class='table table-striped table-hover']/tbody/tr")

    for i in items:
        s = i.xpath('./th/strong/a/@href')
        url = "https://nvd.nist.gov"
        with open("out13.txt", "a") as file:
            file.write(url+s[0])
            file.write("\n")
        file.close()

        print(url+s[0])

