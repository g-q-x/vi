import bf_code
import af_ast

def main(CVE_id):
    list1,count=bf_code.main(CVE_id)
    # for i in list1:
    #     print(i)
    #构建ast
    storage,Gs=af_ast.build_ast(list1)
    return storage,Gs,count

if __name__ == "__main__":
    CVE_id="CVE-2023-31436"
    main(CVE_id)