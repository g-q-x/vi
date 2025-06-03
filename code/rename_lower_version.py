import os.path

import requests
from lxml import etree
import af_code
import filter
import re
import load_file
import re_refactor

types = [
    'static ', 'struct ', 'int ', 'short ', 'long ', 'long long ', 'unsigned int ',
    'unsigned short ', 'unsigned long ', 'unsigned long long ', 'signed int ',
    'signed short ', 'signed long ', 'signed long long ', 'float ', 'double ',
    'long double ', 'char ', 'unsigned char ', 'signed char ', 'void ', 'enum ', 'union ','__cold'
]


import os
import requests
from lxml import etree

import os
import requests
from lxml import etree

def load_patch(patch_list, cve_id):
    for patch in patch_list:
        commit_id = patch.split("id=", 1)[1]
        response = requests.get(patch)
        root = etree.HTML(response.content)
        diffs = root.xpath("//table[@class='diff']/tr/td//div")
        for diff in diffs:
            text_list = diff.xpath("text()")
            if text_list:  # 检查text_list是否为空
                text = text_list[0]
                if diff.xpath("@class") in [['hunk'], ['add'], ['del'], ['ctx']]:
                    # 确保目录存在
                    os.makedirs(f"CVE/{cve_id}/commit", exist_ok=True)
                    # 使用 'utf-8' 编码写入文件，并忽略无法编码的字符
                    with open(f"CVE/{cve_id}/commit/{commit_id}.txt", "a", encoding="utf-8", errors="ignore") as file:
                        file.write(text)
                        file.write("\n")





def find_new_func(diffs):
    new_name_list=[]
    for diff in diffs:
        for line in diff:
            # 忽略空行
            if not line.strip():
                continue

                # 检查行是否以+开头，这表示它可能是新增的行
            if line.startswith('+'):
                # 去除+前缀
                stripped_line = line[1:]

                    # 检查是否是函数定义的开始
                if any(stripped_line.startswith(t) for t in types) and '(' in stripped_line:
                    #print(stripped_line)
                    new_name_list.append(stripped_line)
    return new_name_list

def patch_to_list(diffs):
    list = []
    list1 = []
    for line in diffs:
        line = line.rstrip()
        if line.startswith('@@'):
            if list1 == []:
                list1.append(line)
                continue
            else:
                list.append(list1)
                list1 = []
                list1.append(line)
                continue
        list1.append(line)
    list.append(list1)
    return list

def find_old_name(new_name,diffs):

    pre_line=None
    for diff in diffs:
        for line in diff:
            if new_name==line[1:] :
                if pre_line.startswith("-"):
                    return pre_line[1:]
                else:
                    return None
            else:
                pre_line=line

#判断指定元素是不是列表中最后一个元素
def is_last_element(lst, element):
    # 检查列表是否为空
    if not lst:
        return False
    # 检查指定元素是否是最后一个元素
    return lst[-1] == element

def name_to_commit(cve_id,new_name,new_func_list,storage):
    flag = False
    for commit_id, func_name in new_func_list:

        for patch in func_name:
            if patch == new_name and flag==False:
                flag=True
                with open("CVE/" + cve_id + "/commit/" + commit_id + ".txt","r") as file:
                    diffs=file.readlines()
                file.close()
                list1 = patch_to_list(diffs)
                old_name=find_old_name(patch,list1)
                if old_name!=None:
                    storage.append((commit_id,new_name))
                    name_to_commit(cve_id,old_name,new_func_list,storage)
                else:
                    storage.append((commit_id, new_name))







def rename(cve_id,patch_list,patch_func_name):
    new_func=[]
    name_process_list=[]
    for patch in patch_list:
        #print(patch.split("id=",1)[1])
        with open("CVE/" + cve_id + "/commit/" + patch.split("id=",1)[1] + ".txt","r") as file:
            diffs=file.readlines()
        file.close()
        list1=patch_to_list(diffs)
        #查找新增函数
        list2=find_new_func(list1)

        if list2!=[]:
            # print(patch.split("id=",1)[1])
            # for i in list2:
            #     print(i)
            # print("\n")
            new_func.append((patch.split("id=",1)[1],list2))

    storages=[]
    for name in patch_func_name:
        storage=[]
        name_to_commit(cve_id,name,new_func,storage)
        storages.append((name,storage))
    return storages

def compare_name(commit,commits,patch_list):
    # print(commit)
    # print(commits)
    a=commit
    flag=0
    flag1=0

    for i in patch_list:
        flag=flag+1
        i = i.split("id=", 1)[1]
        if i == a:
            flag1=flag

    tem=None
    for patch_id,patch_name in commits:
        b=patch_id
        flag = 0
        for i in patch_list:
            flag=flag+1
            i=i.split("id=",1)[1]
            if i==b:
                if flag>=flag1:
                    return patch_name
    return None


def load_b_file(cve_id,file_name):
    print(file_name)
    with open("CVE/" + cve_id +  "/patch_list.txt","r") as file:
        diffs=file.readlines()
    file.close()
    for diff in diffs:
        diff=diff.strip()
        if file_name in diff:
            print(diff)
            response = requests.get(diff)
            root = etree.HTML(response.content)
            file_ab = root.xpath("//table[@class='diff']/tr/td//div[@class='head']")
            for i in file_ab:

                # 找到修改之后的文件

                s_b = i.xpath("./a[2]/@href")
                if s_b:
                    response1 = requests.get("https://git.kernel.org" + s_b[0])
                    root1 = etree.HTML(response1.content)
                    plain = root1.xpath("//div[@class='content']/a/@href")
                    response2 = requests.get("https://git.kernel.org" + plain[0])
                    if not os.path.exists("CVE/" + CVE_id + "/change_low_version/"+ file_name +".txt"):
                        with open("CVE/" + CVE_id + "/change_low_version/"+ file_name +".txt" , "w") as file:
                            file.write(response2.text)
                        file.close()
                else:
                    s_b = i.xpath("./a[1]/@href")
                    response1 = requests.get("https://git.kernel.org" + s_b[0])
                    root1 = etree.HTML(response1.content)
                    plain = root1.xpath("//div[@class='content']/a/@href")
                    response2 = requests.get("https://git.kernel.org" + plain[0])
                    if not os.path.exists("CVE/" + CVE_id + "/change_low_version/"+ file_name +".txt"):
                        with open("CVE/" + CVE_id + "/change_low_version/"+ file_name +".txt" , "w") as file:
                            file.write(response2.text)
                        file.close()



def change_commit(cve_id,patch_list,fun_name,commits):
    #print(fun_name)
    # print(commits)
    # print("ok")
    for patch in patch_list[1:]:
        # with open("CVE/" + cve_id + "/commit/" + patch.split("id=",1)[1] + ".txt","r") as file:
        #     diffs=file.readlines()
        # file.close()
        # list1=patch_to_list(diffs)
        list1=re_refactor.refactor_detect_extracted("CVE/" + cve_id + "/commit/" + patch.split("id=",1)[1] + ".txt")
        list2=re_refactor.delete_comment(list1)
        comp_name=compare_name(patch.split("id=",1)[1],commits,patch_list)
        #print(patch.split("id=",1)[1],comp_name)
        if comp_name!=None:
            for diff in list2:
                if comp_name in diff[0]:
                    #print(patch.split("id=",1)[1] )
                    #下载b文件
                    load_b_file(cve_id,patch.split("id=", 1)[1])

        for commit in commits:
            if patch.split("id=",1)[1]==commit[0]:
                load_b_file(cve_id, patch.split("id=", 1)[1])
            #下载b文件






def change(cve_id,patch_list,patch_func_name,storages):
    for i in patch_func_name:
        for storage in storages:
            # print(storage[0])
            # for name in storage[1]:
            #     print(name)
            if storage[0]==i:
                change_commit(cve_id,patch_list,storage[0],storage[1])





def main(cve_id):
    with open("CVE/" + CVE_id + "/patch_list.txt", "r") as file:
        patch_list=file.readlines()
    file.close()
    for i in range(len(patch_list)):
        patch_list[i]=patch_list[i].strip()
    # 创建文件夹
    load_file.create_folder("CVE/" + cve_id + "/commit")
    #下载所有低版本补丁
    load_patch(patch_list,cve_id)
    #漏洞函数
    list1 = filter.main(cve_id)
    func_name_list = af_code.find_patch_func(list1)
    #生成名字变化列表
    storages_names=rename(cve_id,patch_list,func_name_list)
    for storage_name in storages_names:
        print(storage_name[0])
        for i in storage_name[1]:
            print(i)
    #load_file.create_folder("CVE/" + cve_id + "/change_low_version")
    #change(cve_id,patch_list,func_name_list,storages_names)




if __name__ == "__main__":
    CVE_id="CVE-2023-4459"
    main(CVE_id)