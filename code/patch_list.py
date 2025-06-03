import load_file
import requests
from lxml import etree



def find_file_path(link):
    link_list=[]
    response = requests.get(link)
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
                    pathnext = path = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/" + s[0] + "?ofs=" + str(num)
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
                        pathnext = path = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/" + s[0] + "?ofs=" + str(num)
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
                    pathnext = path = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/" + s[0] + "?ofs=" + str(num)
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
                        pathnext = path = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/" + s[0] + "?ofs=" + str(num)
                        response2 = requests.get(pathnext)
                        root2 = etree.HTML(response2.content)
                        commits = root2.xpath("//div[@class='content']//table[@class='list nowrap']/tr")

                        for j in commits:
                            commit = j.xpath("./td[2]/a/@href")

                            if (commit != []):
                                link_list.append("https://git.kernel.org" + commit[0])

                        next1 = root2.xpath("//div[@class='content']//ul[@class='pager']/li[2]/a/text()")
    return link_list

def filter_patch(file_path,link):
    link_list=[]
    flag=False
    for path in file_path:
        if link in path:
            flag=True
        if flag==True:
            link_list.append(path)
    return link_list


def main(CVE_id):
    link=load_file.find_link(CVE_id)
    print(link)
    hyper_link = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=" + str(link)
    file_path=find_file_path(hyper_link)
    low_version=filter_patch(file_path,link)
    for i in low_version:
        with open("CVE/" + CVE_id + "/patch_list.txt", "a") as file:
            file.write(i)
            file.write("\n")
        file.close()

if __name__ == "__main__":
    CVE_id="CVE-2020-25284"
    main(CVE_id)