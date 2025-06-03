import bf_code
import filter
import bf_ast
import af_cfg

def main(CVE_id):
    #补丁文件代码块
    list1,count=bf_code.main(CVE_id)

    #补丁函数建立的控制流图
    storage,Gs,count=bf_ast.main(CVE_id)
    bf_path=[]
    for i in range(len(list1)):
        # 获取 AST,CFG
        #storage.show_ast(i)
        #af_ast.print_control_flow_graph(Gs[i])
        paths = af_cfg.all_path(Gs[i])
        #af_cfg.print_paths(paths)
        bf_path.append(paths)
    return bf_path,count


if __name__ == "__main__":
    CVE_id="CVE-2023-6111"
    main(CVE_id)
