def remove_duplicates(data):
    # 使用集合来消除重复项
    unique_data = list(set(tuple(item) for item in data))
    return [list(item) for item in unique_data]

id_num=[]
with open("out5.txt","r")as file:
    lines = file.readlines()
    current_id=None

    for line in lines:
        line = line.strip()
        if "CVE" in line:
            current_id=line
        else:
            num=[]
            num.append(current_id)
            num.append(line)
            id_num.append(num)
file.close()
cleaned_data = remove_duplicates(id_num)
#print(cleaned_data)
for data in cleaned_data:
    print(data[0])
    print("https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id="+data[1])
# with open("out6.txt","w") as file:
#     for data in cleaned_data:
#         file.write(data[0])
#         file.write("\n")
#         file.write(data[1])
#         file.write("\n")
# file.close()