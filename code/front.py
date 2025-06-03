import re

def find_impacting_lines(code, target_line):
    lines = code.strip().splitlines()
    dependencies = set()
    impacting_lines = {}

    # 提取目标行中的依赖变量
    target_code = lines[target_line - 1].strip()
    dependencies = extract_variables(target_code)
    print("target_code:",target_code)
    print("dependencies:",dependencies)

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
            func_call_vars = extract_variables(line)
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


def extract_variables(expression):
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

# 示例使用：
code = """
struct nft_set_elem_catchall *catchall, *next;
const struct nft_set *set = gc->set;
struct nft_elem_priv *elem_priv;
struct nft_set_ext *ext;
while(catchall, next, &set->catchall_list, list)
{
    ext = nft_set_elem_ext(set, catchall->elem);
    if (!nft_set_elem_expired(ext))
        continue;
    if (nft_set_elem_is_dead(ext))
        goto dead_elem;
    nft_set_elem_dead(ext);
dead_elem:
    if (sync)
        gc = nft_trans_gc_queue_sync(gc, GFP_ATOMIC);
    else
        gc = nft_trans_gc_queue_async(gc, gc_seq, GFP_ATOMIC);
    if (!gc)
        return NULL;
    elem_priv = catchall->elem;
    if (sync) {
        nft_setelem_data_deactivate(gc->net, gc->set, elem_priv);
        nft_setelem_catchall_destroy(catchall);
    }
    nft_trans_gc_elem_add(gc, elem_priv);
}
return gc;
"""
target_line = 27 # 指定行号
#find_impacting_lines(code, target_line)

impacting_lines = find_impacting_lines(code, target_line)
print("Impacting lines:")
for lineno, code_line in impacting_lines.items():
    print(f"Line {lineno}: {code_line}")
