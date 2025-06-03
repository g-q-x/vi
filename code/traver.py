import patch_label
import filter
import af_code
import re
import load_file

types = [
    'static ', 'struct ', 'int ', 'short ', 'long ', 'long long ', 'unsigned int ',
    'unsigned short ', 'unsigned long ', 'unsigned long long ', 'signed int ',
    'signed short ', 'signed long ', 'signed long long ', 'float ', 'double ',
    'long double ', 'char ', 'unsigned char ', 'signed char ', 'void ', 'enum ', 'union ', '__cold'
]


def extract_function_name(function_definition):
    # 使用正则表达式匹配函数名
    match = re.search(r'\w+\s+\*?\s*(\w+)\s*\(', function_definition)
    if match:
        return match.group(1)
    return None


def check_space_before_string(line, target):
    pattern = r'[ \*]+' + re.escape(target)
    match = re.search(pattern, line)

    # 如果找到匹配项且前面有空格或*，则返回True，否则返回False
    return match is not None

def load_change_file(cve_id, name, patch_list):
    file_num = 0
    for patch in patch_list[1:]:
        try:
            with open("CVE/" + cve_id + "/commit/" + patch.split("id=", 1)[1] + ".txt", "r") as file:
                diffs = file.readlines()

            flag = False
            for diff in diffs:
                diff = diff.strip()

                if diff.startswith("+"):
                    diff = diff.split("+", 1)[1]
                    diff = diff.strip()

                elif diff.startswith("-"):
                    diff = diff.split("-", 1)[1]
                    diff = diff.strip()
                elif diff.startswith("@@"):
                    pattern = r'^.*?@@.*?@@'
                    # 替换掉第二个@@之前的内容
                    diff = re.sub(pattern, '', diff, count=1, flags=re.DOTALL)
                    diff = diff.strip()


                # if name in diff:
                #     print(patch)
                #     print(diff)
                name1=name+"("
                for t in types:
                    if diff.startswith(t) and not diff.endswith(";") and name1 in diff and check_space_before_string(diff, name):
                        print(patch)
                        print(diff)
                        flag=True

                if diff.startswith(name1) and not diff.endswith(";"):
                    print(patch)
                    print(diff)
                    flag = True


            if flag:
                file_num += 1
                with open(f"CVE/{cve_id}/change_low_version/" + str(file_num) + "_" + patch.split("id=", 1)[1] + ".txt",
                          "w") as file:
                    for diff in diffs:
                        file.write(diff)

        except FileNotFoundError:
            # 文件不存在时，跳过该文件
            pass
        except UnicodeDecodeError:
            # 处理解码错误
            pass


def main(cve_id):
    # 筛选后的补丁内容
    list2 = filter.main(CVE_id)
    vuln_links = patch_label.main(cve_id)
    # for i in range(len(list2)):
    #     for links in vuln_links[i]:
    #         print(links)
    # 新建文件夹
    #load_file.create_folder("CVE/" + cve_id + "/change_low_version")

    with open("CVE/" + CVE_id + "/patch_list.txt", "r") as file:
        patch_list = file.readlines()
    file.close()
    for i in range(len(patch_list)):
        patch_list[i] = patch_list[i].strip()

    list1 = filter.main(cve_id)
    func_name_list = af_code.find_patch_func(list1)
    # for j in func_name_list:
    #     print(j)
    for i in func_name_list:
        name = "vmxnet3_rq_cleanup"
        print(name)
        load_change_file(cve_id, name, patch_list)


if __name__ == "__main__":
    CVE_id = "CVE-2023-4459"
    main(CVE_id)
