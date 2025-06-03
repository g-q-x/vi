import af_ast
import af_cfg
import af_code
import bf_ast
import bf_cfg
import bf_code
import select_path
import filter
import re
from pycparser import c_parser, c_ast
from collections import Counter


def find_impacting_lines_back(lines, target_line):
    impacting_lines = {}

    # 提取目标行中的依赖变量
    target_code = lines[target_line - 1].strip()
    dependencies = extract_variables_back(target_code)
    # print("target_code:", target_code)
    # print("dependencies:", dependencies)

    # 从指定行的下一行开始检查代码
    for lineno in range(target_line + 1, len(lines) + 1):
        line = lines[lineno-1].strip()

        # 提取当前行中的所有变量
        current_vars = extract_variables_back(line)
        #print(f"Line {lineno}: {line}")
        # print("current_vars:", current_vars)

        flag = False
        var = []
        for i in current_vars:
            for j in dependencies:
                if i == j.split("->", 1)[0] or j==i.split("->",1)[0]:
                    flag = True
                    var.append(j)
        if flag and var!=[]:
            impacting_lines[lineno] = line
            for i in var:
                dependencies.discard(i)  # 移除已处理的依赖

        # 检查当前行是否包含目标行的依赖变量
        if dependencies.intersection(current_vars):
            flag=dependencies.intersection(current_vars)
            impacting_lines[lineno] = line
            for i in flag:
                dependencies.discard(i)


            # 一旦找到影响的行，就可以停止进一步搜索

    return impacting_lines


def extract_variables_back(expression):
    # 删除行尾的分号和多余的空格
    expression = expression.strip().rstrip(';')

    # 去除函数调用名，并只提取括号内的内容
    expression = re.sub(r'\b\w+\s*\(', '(', expression)

    # 提取return语句中的变量
    if expression.startswith("return "):
        return set(re.findall(r'\b[a-zA-Z_]\w*(?:->\w+|\.\w+)?\b', expression[len("return "):]))

    # 提取括号内的内容（适用于函数调用等）
    variables_str = re.findall(r'\((.*?)\)', expression)

    if variables_str:
        # 提取逗号分隔的变量名，并支持提取带指针访问或点操作符的变量
        return {var.strip() for var in re.findall(r'\b[a-zA-Z_]\w*(?:->\w+|\.\w+)?\b', variables_str[0])}

    # 处理赋值语句，提取等号右边的变量名
    if "=" in expression:
        _, expression_right = expression.split("=", 1)
        return set(re.findall(r'\b[a-zA-Z_]\w*(?:->\w+|\.\w+)?\b', expression_right))

    # 默认提取所有符合条件的变量名
    return set()

def find_impacting_lines_front(lines, target_line):
    dependencies = set()
    impacting_lines = {}

    # 提取目标行中的依赖变量
    target_code = lines[target_line - 1].strip()
    dependencies = extract_variables_front(target_code)
    # print("target_code:",target_code)
    # print("dependencies:",dependencies)

    # 倒序检查目标行之前的代码行
    for lineno in range(target_line - 1, 0, -1):
        line = lines[lineno - 1].strip()

        # 检查赋值或指针访问
        if "=" in line:
            var_name, expression = extract_assignment(line)
            var_name = var_name.strip()
            #print("line:",line,"var_name:",var_name)
            flag_dep=False
            var=[]
            for i in dependencies:
                if var_name == i.split("->",1)[0]:
                    flag_dep=True
                    var.append(i)
            if flag_dep and var!=[]:
                impacting_lines[lineno] = line
                for i in var:
                    dependencies.discard(i)  # 移除已处理的依赖
            # 如果当前行的赋值变量在依赖中，则该行影响了目标行
            if var_name in dependencies :
                impacting_lines[lineno] = line
                dependencies.discard(var_name)  # 移除已处理的依赖

        # 检查是否是函数调用，并且函数调用中的参数包含依赖变量
        if is_function_call(line):
            func_call_vars = extract_variables_front(line)
            #print("line:",line,"func_call_vars:",func_call_vars)
            flag_dep = False
            var = []
            for i in dependencies:
                for j in func_call_vars:
                    if j==i.split("->",1)[0]:
                        flag_dep = True
                        var.append(i)
            if flag_dep and var!=[]:
                impacting_lines[lineno] = line
                for i in var:
                    dependencies.discard(i)  # 移除已处理的依赖
            if dependencies.intersection(func_call_vars):
                flag=dependencies.intersection(func_call_vars)
                impacting_lines[lineno] = line
                for i in flag:
                    dependencies.discard(i)  # 移除已处理的依赖

    # 按行号排序影响的行
    impacting_lines_sorted = dict(sorted(impacting_lines.items()))

    return impacting_lines_sorted


def extract_variables_front(expression):
    # 移除行尾的分号和多余的空格
    expression = expression.strip().rstrip(';')

    # 定义一个集合来存储提取的变量
    variables = set()

    # 移除类型转换，例如 (struct smb2_hdr *)
    expression = re.sub(r'\([^\(\)]*\*\)', '', expression)

    # 定义用于匹配变量的正则表达式，包括指针和结构体访问
    variable_pattern = re.compile(r'\b[a-zA-Z_]\w*(?:\s*->\s*[a-zA-Z_]\w*|\s*\.\s*[a-zA-Z_]\w*)*\b')

    # 定义排除关键字和宏定义的正则表达式（假设关键字和常量通常是全大写或保留字）
    exclude_pattern = re.compile(
        r'^(if|else|for|while|return|switch|case|default|break|continue|do|sizeof|typedef|enum|struct|union|static|extern|const|volatile|register|signed|unsigned|int|long|short|float|double|char|void|unsigned|static|inline|__inline|goto|restrict|_Bool|_Complex|_Imaginary|alignof|alignas|asm|auto|bool|complex|imaginary|noreturn|static_assert|thread_local|_Atomic|_Generic|_Noreturn|_Static_assert|_Thread_local|[A-Z_]+)$')

    # 递归解析表达式
    def parse_expression(expr):
        # 提取变量
        for var in variable_pattern.finditer(expr):
            var_name = var.group().strip()
            # 过滤掉保留字和全大写的常量
            if not exclude_pattern.match(var_name):
                variables.add(var_name)

    parse_expression(expression)

    return variables


def extract_assignment(line):
    # 去掉行首和行尾的空白符
    line = line.strip()

    # 处理赋值语句，返回左侧变量和右侧表达式
    if "=" in line:
        # 去掉等号左右的空白符，并返回左侧变量和右侧表达式
        left, right = line.split("=", 1)
        left = left.strip()  # 去除左侧变量前后的空白符
        right = right.strip()  # 去除右侧表达式前后的空白符

        # 如果左侧有指针或其他修饰符（如 const、struct），提取变量名
        var_name = left.split()[-1]  # 取左侧最后一个词作为变量名

        # 如果变量名前有指针符号'*'，去掉它
        if var_name.startswith('*'):
            var_name = var_name[1:]

        return var_name, right

    elif "->" in line:  # 处理指针访问
        # 去掉箭头左右的空白符，并返回左侧部分和右侧部分
        left, right = line.split("->", 1)
        left = left.strip()
        right = right.strip()
        return left, right

    # 如果不包含赋值或指针访问，返回空字符串和原始行
    return "", line



def is_function_call(line):
    # 去除行尾的注释和多余空白字符
    line = re.sub(r'\s*//.*$', '', line).strip()

    # 检测函数调用的正则表达式
    # 确保函数名后跟括号，括号内可以包含实际的参数或为空
    # 排除控制结构，如while、if等
    pattern = r'^\s*\w+\s*\([^)]*\)\s*(?:;|\s*$)'

    # 检测是否符合函数调用格式，但排除常见控制结构
    if re.search(pattern, line):
        # 确保函数名后的括号不在控制结构的上下文中
        return not any(keyword in line for keyword in ['while', 'if', 'for', 'switch', 'case', 'default', 'do'])
    return False

def b_to_a(target, code_b, code_a, bf_paths, diff):
    flag = False
    count = 0
    pre = None
    next = None
    target_line = None
    for line in code_b:
        count += 1
        if count == target:
            target_line = line
            flag = True
        if flag == False:
            flag_pre = False
            for bf_path in bf_paths:
                if line in bf_path[0] and bf_path[0].startswith("+"):
                    flag_pre = True
            if flag_pre == False:
                pre = line
        if flag == True and count != target:
            flag_next = False
            for bf_path in bf_paths:
                if line in bf_path[0] and bf_path[0].startswith("+"):
                    flag_next = True
            if flag_next == False:
                next = line
                break

    # print("pre:",pre)
    # print("target_line:",target_line)
    # print("next:",next)

    flag_pre = False
    flag_next = False
    target_num = None
    count = 0
    for line in code_a:
        count += 1
        if line == pre:
            flag_pre = True
        if flag_pre == True:
            if line == target_line:
                target_num = count

        if line == next and target_num != None:
            # print(target_num)
            return target_num

    return target_num


def remove_duplicates(nested_list):
    # 创建一个集合来保存唯一的子列表（转换为元组）
    seen = set()
    unique_list = []

    for sublist in nested_list:
        # 将子列表转换为元组，以便可以放入集合中
        sublist_tuple = tuple(sublist)
        if sublist_tuple not in seen:
            seen.add(sublist_tuple)
            unique_list.append(sublist)

    return unique_list

# 追溯增加代码的数据流，返回影响代码的上下流
# 如果前后都是新增，则放弃
# 如果前后有一个是新增，则记录另一个
# 如果前后都无新增，则记录前后
def label_A(bf_path, list1_b, list1_a, diff, num, bf_paths):
    #print(bf_path[0])
    front = []
    back=[]
    traces=[]
    for path in bf_path[4:]:
        codes = []
        flag = None
        line_num = 0
        for node in path:
            line_num += 1
            # print(node.coord.line)
            if node.coord.line == bf_path[2].coord.line:
                flag = line_num
            code = select_path.get_line_from_code(list1_b[num].splitlines(), node.coord.line)
            # print(code)
            codes.append(code)
        #print(flag)
        #print(codes)

        impacting_lines_front = find_impacting_lines_front(codes, flag)
        for lineno, code_line in impacting_lines_front.items():
            ev_front = []
            flag_front=None
            line_num=0
            for node in path:
                line_num+=1
                if line_num==lineno:
                    flag_front=node.coord.line

            # print(flag)
            # print(code_line)
            ev_front.append(flag_front)
            ev_front.append(code_line)
            front.append(ev_front)

        impacting_lines_back = find_impacting_lines_back(codes, flag)
        for lineno, code_line in impacting_lines_back.items():
            ev_back = []
            flag_back = None
            line_num = 0
            for node in path:
                line_num += 1
                if line_num == lineno:
                    flag_back = node.coord.line

            # print(flag)
            # print(code_line)
            ev_back.append(flag_back)
            ev_back.append(code_line)
            back.append(ev_back)

    front=remove_duplicates(front)
    back=remove_duplicates(back)
    #print("front:")
    for f in front:
        #print(f)
        trace=[]
        if f == None:
            continue
        front_num = b_to_a(f[0], list1_b[num].splitlines(), list1_a[num].splitlines(), bf_paths, diff)
        trace.append(af_code.remove_location_info(diff[0]))
        trace.append(front_num)
        trace.append(f[1])
        traces.append(trace)
    #print("back:")
    for b in back:
        #print(b)
        trace = []
        if b == None:
            continue
        back_num = b_to_a(b[0], list1_b[num].splitlines(), list1_a[num].splitlines(), bf_paths, diff)
        trace.append(af_code.remove_location_info(diff[0]))
        trace.append(back_num)
        trace.append(b[1])
        traces.append(trace)

    traces=remove_duplicates(traces)
    return traces



# 仅删除，追溯删除代码
def label_D(af_path, diff):
    # print("D")
    # 函数名，代码位置，代码
    if af_path[2]!=None:
        trace = []
        trace.append(af_code.remove_location_info(diff[0]))
        #print(af_path[2])
        trace.append(af_path[2].coord.line)
        trace.append(af_path[0].split("-", 1)[1])
        return trace
    else:
        return None


def label_M_1(af_path, diff):
    # print("M.1")
    # 返回函数名，代码位置，代码
    trace = []
    trace.append(af_code.remove_location_info(diff[0]))
    trace.append(af_path[2].coord.line)
    trace.append(af_path[0].split("-", 1)[1])
    return trace


def label_M_2(af_path, diff):
    # print("M.2")
    # 返回函数名，代码位置，代码
    trace = []
    trace.append(af_code.remove_location_info(diff[0]))
    trace.append(af_path[2].coord.line)
    trace.append(af_path[0].split("-", 1)[1])
    return trace


def label_M_3(af_path, diff):
    # print("M.2")
    # 返回函数名，代码位置，代码
    trace = []
    trace.append(af_code.remove_location_info(diff[0]))
    trace.append(af_path[2].coord.line)
    trace.append(af_path[0].split("-", 1)[1])
    return trace


# 追溯错误代码，追溯错误代码的前后数据流
def label_M_4(af_path, list1_b, list1_a, diff, num, bf_paths):
    front = []
    back = []
    traces = []
    for path in af_path[4:]:
        codes = []
        flag = None
        line_num = 0
        for node in path:
            line_num += 1
            # print(node.coord.line)
            if node.coord.line == af_path[2].coord.line:
                flag = line_num
            code = select_path.get_line_from_code(list1_a[num].splitlines(), node.coord.line)
            # print(code)
            codes.append(code)
        #print(flag)
        #print(codes)

        impacting_lines_front = find_impacting_lines_front(codes, flag)
        #print(impacting_lines_front)
        for lineno, code_line in impacting_lines_front.items():
            ev_front = []
            flag_front = None
            line_num = 0
            for node in path:
                line_num += 1
                if line_num == lineno:
                    flag_front = node.coord.line

            # print(flag)
            # print(code_line)
            ev_front.append(flag_front)
            ev_front.append(code_line)
            front.append(ev_front)

        impacting_lines_back = find_impacting_lines_back(codes, flag)
        for lineno, code_line in impacting_lines_back.items():
            ev_back = []
            flag_back = None
            line_num = 0
            for node in path:
                line_num += 1
                if line_num == lineno:
                    flag_back = node.coord.line

            # print(flag)
            # print(code_line)
            ev_back.append(flag_back)
            ev_back.append(code_line)
            back.append(ev_back)

    front = remove_duplicates(front)
    back = remove_duplicates(back)
    #print("front:")
    for f in front:
        #print(f)
        trace = []
        if f == None:
            continue
        trace.append(af_code.remove_location_info(diff[0]))
        trace.append(f[0])
        trace.append(f[1])
        traces.append(trace)
    # print("back:")
    for b in back:
        # print(b)
        trace = []
        if b == None:
            continue
        trace.append(af_code.remove_location_info(diff[0]))
        trace.append(b[0])
        trace.append(b[1])
        traces.append(trace)

    traces = remove_duplicates(traces)
    trace=[]
    trace.append(af_code.remove_location_info(diff[0]))
    trace.append(af_path[2].coord.line)
    trace.append(af_path[0].split("-", 1)[1])
    traces.append(trace)

    return traces


# 追溯b里M.5前后控制依赖
# 如果前后都新增，则放弃（包括后节点为空）
# 如果前后有一个新增的，取记录另一个
def label_M_5(bf_path, list1_b, list1_a, diff, num, bf_paths):
    # print("M.5")
    traces = []

    # 前后节点，前后节点是否有新增加的，如果有一个是新增加的，则取另一个，如果两个都是新增加的则放弃
    front_loc, back_loc = select_path.front_and_back_node(bf_path)
    if front_loc != []:
        for front in front_loc:
            trace = []
            front_code = select_path.get_line_from_code(list1_b[num].splitlines(), front)
            flag = False
            # 找出代码在a文件中的位置,如果在+补丁里，则不需要再搜索
            for line in diff:
                if front_code in line and line.startswith("+"):
                    flag = True
            if flag == False:
                front = b_to_a(front, list1_b[num].splitlines(), list1_a[num].splitlines(), bf_paths, diff)
                if front == None:
                    continue
                trace.append(af_code.remove_location_info(diff[0]))
                trace.append(front)
                trace.append(front_code)
                traces.append(trace)
    if back_loc != []:
        for back in back_loc:
            trace = []
            back_code = select_path.get_line_from_code(list1_b[num].splitlines(), back)
            flag = False
            # 找出代码在a文件中的位置
            for line in diff:
                if back_code in line:
                    flag = True
            if flag == False:
                back = b_to_a(back, list1_b[num].splitlines(), list1_a[num].splitlines(), bf_paths, diff)
                if back == None:
                    continue
                trace.append(af_code.remove_location_info(diff[0]))
                trace.append(back)
                trace.append(back_code)
                traces.append(trace)

    return traces


def main(CVE_id):
    # 补丁a文件代码块
    list1_a, count_a = af_code.main(CVE_id)
    # 补丁b文件代码块
    list1_b, count_b = bf_code.main(CVE_id)

    # 筛选后的补丁内容
    list2 = filter.main(CVE_id)

    # af和bf的所有路径
    af_paths, count_a = af_cfg.main(CVE_id)
    bf_paths, count_b = bf_cfg.main(CVE_id)
    # for af_path in af_paths:
    #     af_cfg.print_paths(af_path)
    # for bf_path in bf_paths:
    #     af_cfg.print_paths(bf_path)

    # 根据行号找到对应的node
    storage_a, Gs_a, count_a = af_ast.main(CVE_id)
    storage_b, Gs_b, count_b = bf_ast.main(CVE_id)

    del_and_add_path = select_path.main(CVE_id)
    all_vuln_link=[]
    for i in range(len(list2)):
        vuln_link=[]
        # 每个diff块中的每行删除代码
        for af_path in del_and_add_path[i][0]:

            # 追溯删除行
            if af_path[1] == "D":
                # print("D")
                # print(af_path[0])

                trace_line = label_D(af_path, list2[i])
                #print(trace_line)
                if trace_line!=None:
                    vuln_link.append(trace_line)

            # 追溯删除行
            if af_path[1] == "M.1" or af_path[1] == "M.2" or af_path[1] == "M.3" or af_path[1] == "M.5":
                #print("M.1 or M.2 or M.3 or M.5")
                #print(af_path[0])
                trace_line = label_M_1(af_path, list2[i])
                #print(trace_line)
                vuln_link.append(trace_line)

            #追溯代码前后数据依赖+删除行
            if af_path[1]=="M.4":
                #print("M.4")
                #print(af_path[0])
                func_name = select_path.find_func_name(list2[i])
                num = select_path.find_code_in_list1(list1_a, func_name)
                traces=label_M_4(af_path, list1_b, list1_a, list2[i], num, del_and_add_path[i][1])
                for trace in traces:
                    #print(trace)
                    if trace[1]!=None:
                        vuln_link.append(trace)


        # 每个diff块中的每行增加代码
        for bf_path in del_and_add_path[i][1]:
            #     # print(bf_path[0])
            #     # print(bf_path[1])
            # 追溯前后数据控制依赖
            if bf_path[1] == "A":
                #print("A")
                #print(bf_path[0])
                func_name = select_path.find_func_name(list2[i])
                num = select_path.find_code_in_list1(list1_a, func_name)
                traces=label_A(bf_path, list1_b, list1_a, list2[i], num, del_and_add_path[i][1])
                for trace in traces:
                    #print(trace)
                    if trace[1]!=None:
                        vuln_link.append(trace)

            # 追溯前后控制依赖
            if bf_path[1] == "M.5":
                #print("M.5")
                #print(bf_path[0])
                func_name = select_path.find_func_name(list2[i])
                num = select_path.find_code_in_list1(list1_a, func_name)
                traces = label_M_5(bf_path, list1_b, list1_a, list2[i], num, del_and_add_path[i][1])
                for trace in traces:
                    #print(trace)
                    if trace[1]!=None:
                        vuln_link.append(trace)

        #print("\n")
        #print("link:")
        vuln_link=remove_duplicates(vuln_link)
        for link in vuln_link:
            print(link)
        all_vuln_link.append(vuln_link)
    return all_vuln_link



if __name__ == "__main__":
    CVE_id = "CVE-2020-25284"
    main(CVE_id)
