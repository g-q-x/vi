import re
from pycparser import c_parser, c_ast
import filter
import bf_code
import af_cfg
import bf_cfg
import bf_ast
import af_code
import af_ast
from collections import Counter

M = ["M.1", "M.2", "M.3", "M.4", "M.5"]


def find_node_name(node):
    if isinstance(node, c_ast.Compound):
        return "Compound"
    elif isinstance(node, c_ast.For):
        return find_node_name(node.cond)
    elif isinstance(node, c_ast.If):
        return find_node_name(node.cond)
    elif isinstance(node, c_ast.While):
        return find_node_name(node.cond)
    elif isinstance(node, c_ast.DoWhile):
        return find_node_name(node.cond)
    elif isinstance(node, c_ast.Switch):
        return find_node_name(node.cond)
    elif isinstance(node, c_ast.Case):
        return find_node_name(node.expr)
    elif isinstance(node, c_ast.Default):
        return "Default"
    elif isinstance(node, c_ast.FuncDef):  # 函数定义
        return "FuncDef"
    elif isinstance(node, c_ast.FuncDecl):  # 函数声明
        return "FuncDecl"
    elif isinstance(node, c_ast.Return):
        return find_node_name(node.expr)
    elif isinstance(node, c_ast.Decl):
        return (node.name, node.type, find_node_name(node.init))
    elif isinstance(node, c_ast.ID):
        return find_node_name(node.name)
    elif isinstance(node, c_ast.BinaryOp):
        return (node.op, find_node_name(node.left), find_node_name(node.right))
    elif isinstance(node, c_ast.UnaryOp):
        return (node.op, find_node_name(node.expr))
    elif isinstance(node, c_ast.Assignment):
        return (node.op, find_node_name(node.lvalue), find_node_name(node.rvalue))
    elif isinstance(node, c_ast.ArrayDecl):
        return (find_node_name(node.type), node.dim)
    elif isinstance(node, c_ast.ArrayRef):
        return find_node_name(node.name)
    elif isinstance(node, c_ast.Struct):  # 结构体
        return node.name
    elif isinstance(node, c_ast.Union):
        return node.name
    elif isinstance(node, c_ast.Typedef):
        return node.name
    elif isinstance(node, c_ast.Continue):
        return "Continue"
    elif isinstance(node, c_ast.TypeDecl):
        return node.declname
    elif isinstance(node, c_ast.PtrDecl):
        return "PtrDecl"
    elif isinstance(node, c_ast.ExprList):
        expr_names = []
        for expr in node.exprs:
            expr_name = find_node_name(expr)
            if expr_name:
                expr_names.append(expr_name)
        return expr_names
    elif isinstance(node, c_ast.FuncCall):
        return node.name.name, find_node_name(node.args)
    elif isinstance(node, c_ast.Constant):
        return node.type, node.value
    elif isinstance(node, c_ast.Break):
        return "Break"
    elif isinstance(node, c_ast.Goto):
        return node.name
    elif isinstance(node, c_ast.Label):
        return node.name
    elif isinstance(node, c_ast.TernaryOp):
        return (find_node_name(node.cond), find_node_name(node.iftrue), find_node_name(node.iffalse))
    # 处理其他未包括的节点类型
    return None


def find_func_name(diff):
    for line in diff:
        if line.startswith("@@"):
            file_name = af_code.remove_location_info(line)
            return file_name


def find_code_in_list1(list1_a, func_name):
    for i in range(len(list1_a)):
        if func_name in list1_a[i].split('\n', 1)[0]:
            return i


def find_line_number(code_list, target_line, start_line, ele,empty_comment):
    start_line=start_line-empty_comment
    if start_line<=0:
        start_line=1
    #print("start_line:",start_line)
    # print(start_line)
    # print(ele)
    # 将代码段列表中的所有代码合并为一个字符串
    code_string = ''.join(code_list)
    # 按行分割代码字符串
    code_lines = code_string.split('\n')
    # 初始化目标行出现的次数计数器
    count = 0
    #print(start_line-1)
    # 遍历从指定开始行到结束的所有行，查找目标行的索引
    for i in range(start_line - 1, len(code_lines)):
        if code_lines[i].strip() == target_line.strip():
            count += 1
            # 当目标行出现的次数等于ele时，返回当前行号
            if count == ele:
                return i + 1  # 行号从1开始

    return -1  # 如果目标行在代码段中没有出现ele次，返回-1


def find_node_by_line(G, line_number):
    for node in G.nodes():
        if hasattr(node, 'coord') and node.coord and node.coord.line == line_number:
            return node
    return None


def func_start(path, cve_id, func_name):
    file_lines = af_code.read_file_lines("CVE/" + cve_id + "/" + path[0])
    if file_lines is None:
        print("文件不存在")
        return False
    a, b = af_code.find_target_function(file_lines, func_name)
    return a


def extract_numbers_from_diff(diff_line):
    # 使用正则表达式匹配 @@ -数字,数字 +数字,数字 @@ 模式
    match = re.search(r'@@ -(\d+),\d+ \+(\d+),\d+ @@', diff_line)
    if match:
        # 提取两个数字
        num1 = match.group(1)
        num2 = match.group(2)
        return int(num1), int(num2)
    else:
        return None


def nodes_equal(node1, node2):
    if type(node1) != type(node2):
        return False

    if isinstance(node1, c_ast.Node):
        # Compare attributes
        for attr in node1.attr_names:
            if getattr(node1, attr) != getattr(node2, attr):
                return False

        # Compare children
        children1 = [child for _, child in node1.children()]
        children2 = [child for _, child in node2.children()]

        if len(children1) != len(children2):
            return False

        for child1, child2 in zip(children1, children2):
            if not nodes_equal(child1, child2):
                # print("child1:",child1)
                # print("child2:", child2)
                return False

        return True

    return True


# 一个diff块中删除和增加行所在的路径
def include_path(diff, list1_a, Gs_a, af_paths, list1_b, Gs_b, bf_paths, CVE_id,count_a,count_b):

    a, b = extract_numbers_from_diff(diff[0])
    func_name = find_func_name(diff)
    i = find_code_in_list1(list1_a, func_name)
    # print("a,b:",a,b)
    line_del_path = []
    line_add_path = []


    for line in diff:
        element_counter = Counter()
        del_path = []
        add_path = []
        if line.startswith("-"):

            element_counter[line] += 1
            ele = element_counter[line]
            #print(ele)
            del_path.append(line)
            #print(line)
            del_path.append("D")
            line = line.split("-", 1)[1]
            a_code_path = af_code.find_files_with_prefix("CVE/" + CVE_id, "af#")
            start = func_start(a_code_path, CVE_id, func_name)

            line_number = find_line_number(list1_a[i], line, a - start,ele,count_a)

            #print("a:",line_number)
            find_node = find_node_by_line(Gs_a[i], line_number)
            del_path.append(find_node)
            del_path.append(line_number)
            node_name = find_node_name(find_node)
            # for af_path in af_paths:
            for paths in af_paths[i]:
                for node in paths:
                    if node.coord.line==line_number:
                        del_path.append(paths)
                        # path_str = " -> ".join(af_cfg.get_node_info(node) for node in paths)
                        # print(f"Path: {path_str}")
            if del_path != []:
                line_del_path.append(del_path)

        if line.startswith("+"):
            add_path.append(line)
            element_counter[line] += 1
            ele = element_counter[line]

            #print(line)
            add_path.append("A")
            line = line.split("+", 1)[1]
            b_code_path = af_code.find_files_with_prefix("CVE/" + CVE_id, "bf#")
            start = func_start(b_code_path, CVE_id, func_name)

            line_number = find_line_number(list1_b[i], line, b - start,ele,count_b)
            #print("b:",line_number)

            find_node = find_node_by_line(Gs_b[i], line_number)
            add_path.append(find_node)
            add_path.append(line_number)
            node_name = find_node_name(find_node)
            # for bf_path in bf_paths:
            for paths in bf_paths[i]:
                for node in paths:
                    if node.coord.line==line_number:
                        add_path.append(paths)
                        # path_str = " -> ".join(af_cfg.get_node_info(node) for node in paths)
                        # print(f"Path: {path_str}")

            if add_path != []:
                line_add_path.append(add_path)

    return line_del_path, line_add_path


def get_node_type(node):
    if hasattr(node, 'coord') and node.coord:
        return f"{type(node).__name__} "
    else:
        return f"{type(node).__name__} "


def remove_duplicates(lst):
    seen = set()
    output = []
    for item in lst:
        # 将子列表转换为元组，以便能够加入到set中
        t_item = tuple(item) if isinstance(item, list) else item
        if t_item not in seen:
            seen.add(t_item)
            output.append(item)  # 添加原始的item，而不是转换后的t_item
    return output


def complete_path_to_type(paths):
    front = []
    back = []
    for path in paths[4:]:

        front_path = []
        back_path = []
        flag = False
        for node in path:
            if nodes_equal(node, paths[2]):
                flag = True
                continue
            if flag == False:
                front_path.append(get_node_type(node))
            if flag == True:
                back_path.append(get_node_type(node))

        front.append(front_path)
        back.append(back_path)
    front = remove_duplicates(front)
    back = remove_duplicates(back)
    return front, back


def front_and_back_node(paths):
    front = []
    back = []
    for path in paths[4:]:
        pre_node = None
        next_node = None
        flag = False
        for node in path:
            if nodes_equal(node, paths[2]):
                flag = True
                continue
            if not flag:
                pre_node = node.coord.line
            if flag:
                next_node = node.coord.line
                break
        front.append(pre_node)
        back.append(next_node)
    front = remove_duplicates(front)
    back = remove_duplicates(back)
    front = [x for x in front if x is not None]
    back = [x for x in back if x is not None]
    return front, back


def compare_node_info(info_a, info_b):
    if info_a == info_b:
        return True
    elif isinstance(info_a, tuple) and isinstance(info_b, tuple):
        if len(info_a) == len(info_b):
            for a, b in zip(info_a, info_b):
                if not compare_node_info(a, b):
                    return False
            return True
    # 如果不是 tuple 类型或者长度不相等，则返回 False
    return False


def compare_part_path(a_paths, b_paths):
    for a_path in a_paths:
        for b_path in b_paths:
            if a_path == b_path:
                return True
    return False


def get_line_from_code(code_list, line_number):
    """
    从代码列表中获取指定行的内容。

    参数:
    - code_list: 包含代码的列表，每个元素是代码的一行。
    - line_number: 指定的行号（从 1 开始）。

    返回:
    - 指定行号的代码行内容。如果行号超出范围，则返回错误消息。
    """
    # 确保行号在有效范围内
    if line_number < 0 or line_number > len(code_list):
        return f"错误: 行号 {line_number} 超出范围。代码总行数为 {len(code_list)}。"

    # 获取指定行的内容，注意行号从1开始，所以需要减去1来匹配索引
    return code_list[line_number - 1].replace("\t","")


def compare_front_and_back_node(a_nodes, b_nodes, list1_a, list1_b,num):
    for a_node in a_nodes:
        for b_node in b_nodes:
            # print(a_node)
            # print(get_line_from_code(list1_a[0].splitlines(), a_node))
            # print(b_node)
            # print(get_line_from_code(list1_b[0].splitlines(), b_node))
            if get_line_from_code(list1_a[num].splitlines(), a_node) == get_line_from_code(list1_b[num].splitlines(),b_node):
                return True
    return False


def compare_none_node(a_nodes, b_nodes):
    for a_node in a_nodes:
        for b_node in b_nodes:
            if a_node == None and b_node == None:
                return True
    return False


def compare_node(a_node, b_node):
    if type(a_node) == type(b_node) and a_node != None and b_node != None:
        if compare_node_info(find_node_name(a_node), find_node_name(b_node)):
            return True
    return False


# 给删除行打标签：删除D，修改M
# 第一种情况，前后路径相同（类型），最标准的修改
# 第二种情况，前后节点相同（源码）
# 第三种情况，前后路径只有一个相同，但是该节点类型相同（类型+名称），同时a节点和b节点类型相同，名称相同
# 第四种情况，FuncCall，调用的函数相同，但流经的数据不同（所有包含funccall的语句）
# 第五种情况，完全相同（源码）

def label_af_node(af_path, line_add_path, list1_a, list1_b,num):
    # 第五种情况
    for bf_path in line_add_path:
        if af_path[0].split("-", 1)[1].replace("\t", "") == bf_path[0].split("+", 1)[1].replace("\t", ""):
            af_path[1] = "M.5"
            return af_path

    # 第四种情况
    if isinstance(af_path[2], c_ast.FuncCall):
        for bf_path in line_add_path:
            if isinstance(bf_path[2], c_ast.FuncCall):
                if compare_node_info(find_node_name(bf_path[2]), find_node_name(af_path[2])) and \
                        af_path[0].split("-", 1)[1].replace("\t", "") != bf_path[0].split("+", 1)[1].replace("\t", ""):
                    af_path[1] = "M.4"
                    return af_path

    # 第一种情况
    front_a, back_a = complete_path_to_type(af_path)
    for bf_path in line_add_path:
        front_b, back_b = complete_path_to_type(bf_path)
        if compare_part_path(front_a, front_b) and compare_part_path(back_a, back_b):
            af_path[1] = "M.1"
            return af_path

    # 第二种情况
    front_a, back_a = front_and_back_node(af_path)
    for bf_path in line_add_path:
        front_b, back_b = front_and_back_node(bf_path)
        if front_a is not None and front_b is not None and back_a is not None and back_b is not None:

            if compare_front_and_back_node(front_a, front_b, list1_a, list1_b,num) and compare_front_and_back_node(back_a,
                                                                                                               back_b,
                                                                                                               list1_a,
                                                                                                               list1_b,num):
                af_path[1] = "M.2"
                return af_path
        if front_a is None and front_b is None and back_a is not None and back_b is not None:
            if compare_front_and_back_node(back_a, back_b, list1_a, list1_b,num):
                af_path[1] = "M.2"
                return af_path
        if front_a is not None and front_b is not None and back_a is None and back_b is None:
            if compare_front_and_back_node(front_a, front_b, list1_a, list1_b,num):
                af_path[1] = "M.2"
                return af_path

    # 第三种情况
    front_a, back_a = front_and_back_node(af_path)
    for bf_path in line_add_path:
        front_b, back_b = front_and_back_node(bf_path)
        # 前后节点有一个相同，且不为None
        if front_a is not None and front_b is not None:

            if compare_front_and_back_node(front_a, front_b, list1_a, list1_b,num):

                if type(af_path[2]) == type(bf_path[2]):
                    af_path[1] = "M.3"
                    return af_path
        if back_a is not None and back_b is not None:
            # print("back_a:",back_a)
            # print("back_b:", back_b)
            if compare_front_and_back_node(back_a, back_b, list1_a, list1_b,num):
                #print("ok")
                if type(af_path[2]) == type(bf_path[2]):
                    af_path[1] = "M.3"
                    return af_path




    # 不属于以上四种情况
    return af_path


def label_bf_node(bf_path, line_del_path, list1_a, list1_b,num):
    # 第五种情况
    for af_path in line_del_path:
        if af_path[0].split("-", 1)[1].replace("\t", "") == bf_path[0].split("+", 1)[1].replace("\t", ""):
            bf_path[1] = "M.5"
            return bf_path

    # 第四种情况
    if isinstance(bf_path[2], c_ast.FuncCall):
        for af_path in line_del_path:
            if isinstance(af_path[2], c_ast.FuncCall):
                if compare_node_info(find_node_name(bf_path[2]), find_node_name(af_path[2])) and \
                        af_path[0].split("-", 1)[1].replace("\t", "") != bf_path[0].split("+", 1)[1].replace("\t", ""):
                    bf_path[1] = "M.4"
                    return bf_path


    # 第一种情况
    front_b, back_b = complete_path_to_type(bf_path)
    for af_path in line_del_path:
        front_a, back_a = complete_path_to_type(af_path)
        if compare_part_path(front_a, front_b) and compare_part_path(back_a, back_b):
            bf_path[1] = "M.1"
            return bf_path

    # 第二种情况
    front_b, back_b = front_and_back_node(bf_path)
    for af_path in line_del_path:
        front_a, back_a = front_and_back_node(af_path)
        if front_a is not None and front_b is not None and back_a is not None and back_b is not None:
            if compare_front_and_back_node(front_a, front_b, list1_a, list1_b,num) and compare_front_and_back_node(back_a,
                                                                                                               back_b,
                                                                                                               list1_a,
                                                                                                               list1_b,num):
                bf_path[1] = "M.2"
                return bf_path
        if front_a is None and front_b is None and back_a is not None and back_b is not None:
            if compare_front_and_back_node(back_a, back_b, list1_a, list1_b,num):
                bf_path[1] = "M.2"
                return bf_path
        if front_a is not None and front_b is not None and back_a is None and back_b is None:
            if compare_front_and_back_node(front_a, front_b, list1_a, list1_b,num):
                bf_path[1] = "M.2"
                return bf_path

    # 第三种情况
    front_b, back_b = front_and_back_node(bf_path)
    for af_path in line_del_path:
        front_a, back_a = front_and_back_node(af_path)
        # 前后节点有一个相同，且不为None
        if front_a is not None and front_b is not None:
            if compare_front_and_back_node(front_a, front_b, list1_a, list1_b,num):
                if type(af_path[2]) == type(bf_path[2]):
                    bf_path[1] = "M.3"
                    return bf_path
        if back_a is not None and back_b is not None and back_a!=[] and back_b!=[]:
            # print("back_a:", back_a)
            # print("back_b:", back_b)
            # print(get_line_from_code(list1_a[num].splitlines(), back_a[0]))
            # print(get_line_from_code(list1_b[num].splitlines(), back_b[0]))
            if compare_front_and_back_node(back_a, back_b, list1_a, list1_b,num):
                #print("ok")
                if type(af_path[2]) == type(bf_path[2]):
                    bf_path[1] = "M.3"
                    return bf_path




    # 不属于以上四种情况
    return bf_path


def patch_label(line_del_path, line_add_path, list1_a, list1_b,num):
    # for af_path in line_del_path:
    #     print("source code:",af_path[0])
    #     # print("label:",af_path[1])
    #     # print("node:",af_path[2])
    #     for paths in af_path[4:]:
    #         path_str = " -> ".join(get_node_type(node) for node in paths)
    #         print(f"Path: {path_str}")
    #
    # for bf_path in line_add_path:
    #     print("source code:", bf_path[0])
    #     # print("label:", bf_path[1])
    #     # print("node:", bf_path[2])
    #     for paths in bf_path[4:]:
    #         path_str = " -> ".join(get_node_type(node) for node in paths)
    #         print(f"Path: {path_str}")

    new_line_del_path = []
    new_line_add_path = []

    # 比较所有补丁,给补丁打标签
    for af_path in line_del_path:
        #print(af_path[0])
        af_path = label_af_node(af_path, line_add_path, list1_a, list1_b,num)

        #print(af_path[1])
        new_line_del_path.append(af_path)

    for bf_path in line_add_path:
        #print(bf_path[0])
        bf_path = label_bf_node(bf_path, line_del_path, list1_a, list1_b,num)

        #print(bf_path[1])
        new_line_add_path.append(bf_path)
    return new_line_del_path, new_line_add_path


def main(CVE_id):
    # 补丁a文件代码块
    list1_a,count_a = af_code.main(CVE_id)
    # 补丁b文件代码块
    list1_b,count_b = bf_code.main(CVE_id)

    # 筛选后的补丁内容
    list2 = filter.main(CVE_id)

    # af和bf的所有路径
    af_paths,count_a = af_cfg.main(CVE_id)
    bf_paths,count_b = bf_cfg.main(CVE_id)
    # for af_path in af_paths:
    #     af_cfg.print_paths(af_path)
    # for bf_path in bf_paths:
    #     af_cfg.print_paths(bf_path)

    # 根据行号找到对应的node
    storage_a, Gs_a,count_a = af_ast.main(CVE_id)
    storage_b, Gs_b,count_b = bf_ast.main(CVE_id)

    # 根据补丁找到对应的源码和路径
    num=0
    del_and_add_path = []
    for diff in list2:
        path = []
        # 一个diff块中删除和增加行所在的路径

        line_del_path, line_add_path = include_path(diff, list1_a, Gs_a, af_paths, list1_b, Gs_b, bf_paths, CVE_id,count_a,count_b)

        func_name = find_func_name(diff)
        num = find_code_in_list1(list1_a, func_name)

        # 给每一行补丁打标签
        new_line_del_path, new_line_add_path = patch_label(line_del_path, line_add_path, list1_a, list1_b,num)
        path.append(new_line_del_path)
        path.append(new_line_add_path)

        del_and_add_path.append(path)
        num=num+1

    # for i in list2:
    #     print(af_code.remove_location_info(i[0]))

    for i in range(len(list2)):
        path=del_and_add_path[i]
        del_path=path[0]
        for af_path in del_path:
            if af_path[1]=="D":
                # print(af_code.remove_location_info(list2[i][0]))
                for j in range(len(list2)):
                    if af_code.remove_location_info(list2[j][0])==af_code.remove_location_info(list2[i][0]) and i!=j:
                        for bf_path in del_and_add_path[j][1]:
                            if bf_path[1]=="A":
                                if af_path[0].split("-", 1)[1].replace("\t", "") == bf_path[0].split("+", 1)[1].replace("\t", ""):
                                    af_path[1] = "M.5"
                                    bf_path[1] = "M.5"
                                if isinstance(af_path[2], c_ast.FuncCall) and isinstance(bf_path[2], c_ast.FuncCall):
                                    if compare_node_info(find_node_name(bf_path[2]),find_node_name(af_path[2])) and af_path[0].split("-", 1)[1].replace("\t", "") != bf_path[0].split("+", 1)[1].replace("\t", ""):
                                        af_path[1] = "M.4"
                                        bf_path[1] = "M.4"
        #     print(af_path[0])
        #     print(af_path[1])
        # for bf_path in add_path:
        #     print(bf_path[0])
        #     print(bf_path[1])


    return del_and_add_path


if __name__ == "__main__":
    CVE_id = "CVE-2020-25284"
    main(CVE_id)
