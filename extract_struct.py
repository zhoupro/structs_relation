import fileinput

output_str = ""
depth = 0
collect = 0
for tmpline in fileinput.input():
    if "struct" in tmpline and "{" in tmpline:
        collect = 1
        output_str = tmpline
        depth = depth + 1
    elif "{" in tmpline and collect == 1:
        output_str += tmpline
        depth = depth + 1
    elif "}" in tmpline and collect == 1:
        output_str += tmpline
        depth = depth - 1
        if depth == 0:
            collect = 0
            print(output_str)
    elif collect == 1:
        output_str += tmpline
