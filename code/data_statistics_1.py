import re


def check_insertions_deletions(log):

    insertions = int(re.search(r'(\d+) insertions?', log).group(1))
    deletions = int(re.search(r'(\d+) deletions?', log).group(1))

    return insertions,deletions

with open("out11_output.txt","r")as file:
    lines=file.readlines()
file.close()

add=0
dele=0
modify=0

for line in lines:
    flag="[]\n"
    if line==flag:
        continue
    line = line.strip()
    print(line)
    insertion,deletion=check_insertions_deletions(line)
    if insertion>0 and deletion>0:
        print("modify")
        modify+=1
    elif insertion>0:
        print("add")
        add+=1
    elif deletion>0:
        print("del")
        dele+=1

print("add:",add)
print("del:",dele)
print("modify:",modify)