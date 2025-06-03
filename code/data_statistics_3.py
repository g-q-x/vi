import re


def check_insertions_deletions(log):
    files = int(re.search(r'(\d+) files?', log).group(1))
    insertions = int(re.search(r'(\d+) insertions?', log).group(1))
    deletions = int(re.search(r'(\d+) deletions?', log).group(1))

    return files,insertions,deletions

with open("out11_output.txt","r")as file:
    lines=file.readlines()
file.close()

files=0
insertions=0
deletions=0


for line in lines:
    flag="[]\n"
    if line==flag:
        continue
    line = line.strip()
    print(line)
    file,insertion,deletion=check_insertions_deletions(line)
    files=files+file
    insertions=insertions+insertion
    deletions=deletions+deletion


print("file:",files)
print("insertions:",insertions)
print("deletions:",deletions)