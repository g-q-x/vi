import af_ast
import af_code
import filter
import networkx as nx
from pycparser import c_parser,c_ast
import sys





def find_all_paths(G, start_node):
    paths = []

    def dfs(current_node, current_path):
        # 添加当前节点到路径中
        current_path.append(current_node)

        # 如果当前节点没有出边（即为叶子节点），则记录当前路径
        if len(list(G.successors(current_node))) == 0:
            paths.append(list(current_path))
        else:
            # 否则，继续递归遍历后继节点
            for successor in G.successors(current_node):
                dfs(successor, current_path)

        # 回溯到前一个节点
        current_path.pop()

    # 从起始节点开始DFS遍历
    dfs(start_node, [])
    return paths

def get_node_info(node):
    if hasattr(node, 'coord') and node.coord:
        return f"{type(node).__name__} (Line {node.coord.line})"
    else:
        return f"{type(node).__name__} (Unknown Line)"

def print_paths(paths):
    for path in paths:
        path_str = " -> ".join(get_node_info(node) for node in path)
        print(f"Path: {path_str}")

def all_path(G):
    start_node = None
    for node in G.nodes():
        if isinstance(node, c_ast.FuncDef):
            start_node = node
            break
    path=[]
    # 获取所有路径
    if start_node:
        paths = find_all_paths(G, start_node)

    return paths



def main(CVE_id):
    #补丁文件代码块
    list1,count=af_code.main(CVE_id)

    #补丁函数建立的控制流图
    storage,Gs,count=af_ast.main(CVE_id)
    af_path=[]
    for i in range(len(list1)):
        # 获取 AST,CFG
        #storage.show_ast(i)
        #af_ast.print_control_flow_graph(Gs[i])
        paths=all_path(Gs[i])
        #print_paths(paths)
        af_path.append(paths)
    return af_path,count



if __name__ == "__main__":
    CVE_id="CVE-2023-5345"
    main(CVE_id)






