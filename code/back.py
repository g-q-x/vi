import re


def find_impacting_lines_back(code, target_line):
    lines = code.strip().splitlines()
    impacting_lines = {}

    # 提取目标行中的依赖变量
    target_code = lines[target_line - 1].strip()
    dependencies = extract_variables_back(target_code)
    print("target_code:", target_code)
    print("dependencies:", dependencies)

    # 从指定行的下一行开始检查代码
    for lineno in range(target_line + 1, len(lines) + 1):
        line = lines[lineno - 1].strip()

        # 提取当前行中的所有变量
        current_vars = extract_variables_back(line)
        # print(f"Line {lineno}: {line}")
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
target_line = 25  # 指定行号

impacting_lines = find_impacting_lines_back(code, target_line)
print("Impacting lines:")
for lineno, code_line in impacting_lines.items():
    print(f"Line {lineno}: {code_line}")
