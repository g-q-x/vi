import filter
import re
import os

def extract_function_code(input_string, c_file_path):
    # 解析输入
    pattern = r'@@ -\d+,\d+ \+\d+,\d+ @@ (.*)$'
    matches = re.findall(pattern, input_string, re.MULTILINE)

    # 打开C文件读取内容
    with open(c_file_path, 'r') as file:
        c_code = file.read()

    # 找到并提取函数定义
    function_code = []
    for match in matches:
        function_signature = match.strip()
        if function_signature:
            # 构建正则表达式来匹配完整函数定义
            func_pattern = rf'{re.escape(function_signature)}\s*\(.*?\)\s*\{{[\s\S]*?\}}'
            func_match = re.search(func_pattern, c_code)
            if func_match:
                function_code.append(func_match.group(0))

    return function_code


def find_files_with_prefix(directory, prefix):
    matching_files = []

    # 遍历指定目录中的所有文件和文件夹
    for filename in os.listdir(directory):
        # 检查文件名是否以指定前缀开头
        if filename.startswith(prefix):
            matching_files.append(filename)

    return matching_files



def remove_location_info(input_str):
    # 匹配定位信息的正则表达式模式
    pattern = r'@@ -\d+,\d+ \+\d+,\d+ @@'
    # 替换定位信息为空字符串
    cleaned_str = re.sub(pattern, '', input_str).strip()
    return cleaned_str

def remove_duplicates(input_list):
    seen = set()
    output_list = []
    for item in input_list:
        if item not in seen:
            seen.add(item)
            output_list.append(item)
    return output_list

def find_patch_func(diffs):
    filename=[]
    for diff in diffs:
        for line in diff:
            if line.startswith("@@"):
                #print(line)
                file_name=remove_location_info(line)
                #print(file_name)
                filename.append(file_name)
    filename=remove_duplicates(filename)
    # for name in filename:
    #     print(name)
    return filename

def read_file_lines(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
        return None

def find_target_function(file_lines,func):
    FIND=False
    num = 0
    start_num = 0
    end_num = 0
    func=func.strip()
    for line in file_lines:
        num = num + 1
        if func in line and not line.split("\n",1)[0].endswith(";"):
            start_num = num

            FIND=True
            continue

        if FIND == True:
            keywords = ["int", "void", "char", "float", "double", "struct", "static","__cold"]
            pattern = re.compile(r'^(?:' + '|'.join(re.escape(keyword) for keyword in keywords) + r')\b')
            match = pattern.match(line)
            if match is not None and not line[0].isspace():
                end_num = num
                break
    if end_num==0:
        end_num=num
    # print("start:", start_num)
    # print("end:", end_num)
    while(file_lines[end_num-1]!="}\n" and end_num>-1 and end_num<=len(file_lines)):
        end_num=end_num-1

    return start_num,end_num+1

def extract_lines_from_file(filename, start_line, end_line):
    lines = []

    # 使用with语句打开文件，确保文件正确关闭
    with open(filename, 'r') as file:
        # 遍历文件中的每一行，记录当前行号
        for current_line_number, line in enumerate(file, start=1):
            # 如果当前行号在指定范围内，则添加到结果列表
            if start_line <= current_line_number <= end_line:
                lines.append(line)
            # 如果超过终止行，停止读取
            elif current_line_number > end_line:
                break

    # 将结果列表中的行连接成一个字符串并返回
    return ''.join(lines)


def find_patch_code(func_name_list,cve_id):
    a_code_path=find_files_with_prefix("CVE/" + cve_id,"af#")
    file_lines = read_file_lines("CVE/" + cve_id + "/" + a_code_path[0])
    if file_lines is None:
        print("文件不存在")
        return False
    code_list = []
    for func in func_name_list:
        # print(func)
        a, b = find_target_function(file_lines, func)
        #print(a,b)
        code_list.append(extract_lines_from_file("CVE/" + cve_id + "/" + a_code_path[0], a, b - 1).strip())
        #print(extract_lines_from_file("CVE/"+cve_id+"/"+a_code_path[0], a, b-1).strip())
    return code_list


def code_filter(codes):
    new_codes = []
    empty_lines_count = 0
    comment_lines_count = 0

    for code in codes:
        lines = code.splitlines()
        filtered_lines = []

        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                # 统计空行
                empty_lines_count += 1
            elif stripped_line.startswith('//') or stripped_line.startswith('/*') or stripped_line.startswith('*/') or stripped_line.startswith('* ') or stripped_line.startswith('*\t'):
                # 统计注释行
                comment_lines_count += 1
            else:
                # 不是空行也不是注释行的行，添加到过滤后的列表中
                filtered_lines.append(line)

        # 将过滤后的行重新组合成字符串
        new_codes.append('\n'.join(filtered_lines))
    count=empty_lines_count+comment_lines_count
    # 返回过滤后的代码以及空行和注释行的数量
    return new_codes,  count



def main(CVE_id):
    list1 = filter.main(CVE_id)

    # for diff in list1:
        # for i in diff:
        #     print(i)

    # 根据补丁找到发生变化的函数
    func_name_list = find_patch_func(list1)

    # for i in func_name_list:
    #     print(i)
    #找到对应的函数代码
    patch_code_list = find_patch_code(func_name_list, CVE_id)
    # for i in patch_code_list:
    #     print(i)

    #去掉注释和空行
    new_patch_code_list,count=code_filter(patch_code_list)

    # for i in new_patch_code_list:
    #     print(i)

    return new_patch_code_list,count

if __name__ == "__main__":
    CVE_id="CVE-2016-8650"
    main(CVE_id)