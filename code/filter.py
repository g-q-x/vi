import re_refactor
import re
def get_code_type(line):

    #print(line)
    # Check if the line starts with a space or tab
    if line.startswith(' ') or line.startswith('\t') or line.startswith('{') or line.startswith("}"):
        line = line.strip()
    else:
        return "FunctionDefinition"

    if all(char in {'+', '-', '/', '*', '=', '<', '>', '!', '%', '&', '|', '^', '~', '\t', '{', '}'} for char in line):
        return "sign"

    # Regular expressions for different types of lines
    variable_definition_re = re.compile(r'\b(struct|int|float|double|char|void|long|short|unsigned|signed)\b.*;')
    function_call_re = re.compile(r'\w+\s*\(.*\)\s*;')
    control_statement_re = re.compile(r'\b(if|else|while|for|do|switch|case|default|break|continue|return|goto|list_for_each_entry_safe|list_for_each_entry_rcu)\b')
    variable_assignment_re = re.compile(r'\w+\s*=\s*.*;')

    if variable_definition_re.match(line):
        return "Definition"
    elif function_call_re.match(line):
        return "FunctionCall"
    elif control_statement_re.match(line):
        return "ControlStatement"
    elif variable_assignment_re.match(line):
        return "VariableAssignment"
    else:
        return "Other"

def filter_code_type(list1):
    danger_func_list=[]
    for diff in list1:
        ev_list=[]
        for line in diff:
            ori_code=line
            if line.startswith("@@"):
                ev_list.append(ori_code)
            if line.startswith("+"):
                line = line.lstrip("+")
                type=get_code_type(line)
                #print(type,line)
                if type!="sign" and type!="Definition" :
                    ev_list.append(ori_code)
            if line.startswith("-"):
                line = line.lstrip("-")
                type=get_code_type(line)
                #print(type, line)
                if type!="sign" and type!="Definition" :
                    ev_list.append(ori_code)
        danger_func_list.append(ev_list)

    real_list = []
    for diff in danger_func_list:
        if re_refactor.clean_and_check_list(diff):
            real_list.append(diff)


    return real_list







def main(CVE_id):
    list1=re_refactor.main(CVE_id)
    # for diff in list1:
    #     for line in diff:
    #         print(line)
    #补丁类型过滤
    list2=filter_code_type(list1)
    for diff in list2:
        for line in diff:
            print(line)
    return list2


if __name__ == "__main__":
    CVE_id="CVE-2016-5314"
    main(CVE_id)