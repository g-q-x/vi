import filter
import patch_label
import os
import traver
import af_code

def sort_by_second_element(data):
    # 使用sorted()函数，根据每个子列表的第二个元素（索引为1）进行排序
    sorted_data = sorted(data, key=lambda x: x[1])
    return sorted_data

def main(cve_id):
    # 筛选后的补丁内容
    list2 = filter.main(CVE_id)
    func_name_list = af_code.find_patch_func(list2)
    vuln_links = patch_label.main(cve_id)
    result = []
    for i in range(len(list2)):
        diff_line=vuln_links[i]
        sorted_data = sort_by_second_element(diff_line)
        for data in sorted_data:
            print(data[2])
        if sorted_data:
            func_name=sorted_data[0][0]
        else:
            continue
        print(func_name)
        name=traver.extract_function_name(func_name)
        #print(name)

        for filename in os.listdir("CVE/"+cve_id+"/change_low_version"):
            # 生成文件的完整路径
            file_path = os.path.join("CVE/"+cve_id+"/change_low_version", filename)
            #print(file_path)
            with open(file_path,"r") as file1:
                patchs=file1.readlines()
            file1.close()
            diffs=[]
            diff=[]
            for patch in patchs:
                if "@@" in patch:
                    #print(patch)
                    if diff==[]:
                        diff.append(patch)
                    else:
                        diffs.append(diff)
                        diff=[]
                        diff.append(patch)
                else:
                    diff.append(patch)
            diffs.append(diff)
            #print(diffs)
            for diff in diffs:
                for line in diff:
                    line=line.strip()
                    if line.startswith("+"):
                        #print(line)
                        for data in sorted_data:
                            ev_line=line.split("+",1)[1]
                            ev_line.strip()
                            #print(ev_line)
                            if data[2] in ev_line:
                                print(file_path)
                                result.append(file_path)

    if result==[]:
        for name in func_name_list:
            name=traver.extract_function_name(name)
            #print(name)
            for filename in os.listdir("CVE/" + cve_id + "/change_low_version"):
                # 生成文件的完整路径
                file_path = os.path.join("CVE/" + cve_id + "/change_low_version", filename)
                # print(file_path)
                with open(file_path, "r") as file1:
                    patchs = file1.readlines()
                file1.close()
                diffs = []
                diff = []
                for patch in patchs:
                    if "@@" in patch:
                        # print(patch)
                        if diff == []:
                            diff.append(patch)
                        else:
                            diffs.append(diff)
                            diff = []
                            diff.append(patch)
                    else:
                        diff.append(patch)
                diffs.append(diff)
                # print(diffs)
                name="sock_orphan(sk);"
                for diff in diffs:
                    for line in diff:
                        line = line.strip()
                        if line.startswith("+"):
                            if name in line:
                                print(file_path)




if __name__ == "__main__":
    CVE_id = "CVE-2023-46862"
    main(CVE_id)