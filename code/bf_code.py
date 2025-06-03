import filter
import re
import os
import af_code
import re_refactor






def find_patch_code(func_name_list,cve_id):
    b_code_path=af_code.find_files_with_prefix("CVE/" + cve_id,"bf#")
    file_lines = af_code.read_file_lines("CVE/" + cve_id + "/" + b_code_path[0])
    if file_lines is None:
        print("文件不存在")
        return False
    code_list = []
    for func in func_name_list:
        # print(func)
        a, b = af_code.find_target_function(file_lines, func)
        #print(a,b)
        code_list.append(af_code.extract_lines_from_file("CVE/" + cve_id + "/" + b_code_path[0], a, b - 1).strip())
        #print(extract_lines_from_file("CVE/"+cve_id+"/"+a_code_path[0], a, b-1).strip())
    return code_list






def main(CVE_id):
    list1 = filter.main(CVE_id)

    # for diff in list1:
    #     for i in diff:
    #         print(i)

    # 根据补丁找到发生变化的函数
    func_name_list = af_code.find_patch_func(list1)

    flag=False
    flag,a_name,b_name=re_refactor.old_and_new_func(CVE_id)
    if flag:
        func_name_list = [b_name[0] if x == a_name[0] else x for x in func_name_list]

    # for i in func_name_list:
    #     print(i)



    #找到对应的函数代码
    patch_code_list = find_patch_code(func_name_list, CVE_id)
    # 去掉注释和空行
    new_patch_code_list,count = af_code.code_filter(patch_code_list)

    # for i in new_patch_code_list:
    #     print(i)

    return new_patch_code_list,count

if __name__ == "__main__":
    CVE_id="CVE-2023-1075"
    main(CVE_id)