import fileinput

import re

output_str = ""
depth = 0
collect = 0
strus = []
fieldobj = {}
stack = []
node_type = "struct"

nodeList = []
linkList = []


dotText ='''
digraph {
    graph [pad="0.5", nodesep="0.5", ranksep="2"];
    node [shape=plain]
    rankdir=LR;
'''



for tmpline in fileinput.input():

    if "struct" in tmpline and "{" in tmpline or  "union" in tmpline and "{" in tmpline:
        if "union" in tmpline:
            node_type = "union"
        depth = depth + 1
    elif "}" in tmpline:
        m = re.search(r'}\s*([0-9a-zA-Z_\-\[\]\*]*)\s*\;\s*', tmpline)
        struct_name = m.group(1)
        top_node = stack[-1]
        curList = []
        curObj = {}
        while top_node["_depth"] ==  depth:
            curList.append(top_node)
            node_type = top_node["_node_type"]
            stack.pop()
            if len(stack) == 0:
                break
            top_node = stack[-1]
        curObj["val"] = curList
        curObj["key"] = struct_name
        depth = depth - 1
        curObj["_depth"] = depth
        curObj["_node_type"] = node_type
        curObj["_cur_node_type"] = "stru"
        stack.append(curObj)
        if depth == 0:
            strus.append(stack[0])
            stack = []
            continue
    else :

        fieldobj = {}
        tmpline = re.sub(r'; *', '', tmpline)
        tmpline = tmpline.strip()
        if "(" in tmpline:

            m = re.search(r'.*\(\s*\*\s*([0-9a-zA-Z_\-]+)\).*', tmpline)
            fieldobj["val"] =  tmpline
            fieldobj["key"] =  m.group(1) 
            fieldobj["_depth"] =  depth
            fieldobj["_cur_node_type"] =  "func"
        else:
            if "[" in tmpline:
                tmpline = re.sub(r'\[', '_', tmpline)
                tmpline = re.sub(r'\]', '_', tmpline)
            tmpline = re.sub(r'struct', '', tmpline)
            tmpline = tmpline.strip()
            if "," in tmpline:

                fieldListOri = tmpline.split(",")
                fieldList = fieldListOri[0].split(" ")

                for field in fieldListOri[1:len(fieldListOri)]:
                    fieldobj = {}
                    fieldobj["val"] =  "_".join(fieldList[0:-1])
                    fieldobj["key"] =  field.strip(" ")
                    fieldobj["_depth"] =  depth
                    fieldobj["_cur_node_type"] =  "attr"
                    fieldobj["_node_type"] =  node_type
                    stack.append(fieldobj)

                fieldobj = {}
                fieldobj["val"] =  "_".join(fieldList[0:-1])
                fieldobj["_depth"] =  depth
                fieldobj["_cur_node_type"] =  "attr"
                fieldobj["_node_type"] =  node_type
                fieldobj["key"] =  fieldList[-1]
                stack.append(fieldobj)
                continue

            else:
                fieldList = tmpline.split(" ")
                name  = fieldList[-1].strip()
                fieldobj["val"] =  "_".join(fieldList[0:-1])
                fieldobj["key"] =  name
                fieldobj["_depth"] =  depth
                fieldobj["_cur_node_type"] =  "attr"

        fieldobj["_node_type"] =  node_type
        stack.append(fieldobj)



nodeStack = []
linkStr = ""


sset = {"mock"}
for s in strus:
    s["path"] = s["key"]
    nodeStack.append(s)
    sset.add(s["key"])


while (len(nodeStack) > 0):
    curNode = nodeStack.pop()
    key = curNode["key"]
    dotText =  dotText + """    {} [label=<
    <table border="0" cellborder="1" cellspacing="0">
    <tr><td colspan="2" port="head"><i>{}</i></td></tr>\n""".format(key, key)

    vals = curNode["val"]
    for row in vals:
        replacedKey = re.sub(r'\*',"__",row["key"]) 
        if isinstance(row["val"],list):
            tmpNode = {}
            # tmpNode["path"] = curNode["path"] +"#" + row["key"]
            tmpLinkStr = "    {}:{}->{}:head\n".format(key, replacedKey,row["key"])
            linkStr = linkStr + tmpLinkStr
            tmpNode["key"] = row["key"]
            tmpNode["val"] = row["val"]
            nodeStack.append(tmpNode)
            sset.add(row["key"])
        nodeType = row["val"]
        if isinstance(row["val"],list):
            nodeType = row["_node_type"]

        if not isinstance(row["val"],list):
            if row["val"] in sset:
                tmpLinkStr = "    {}:{}->{}:head\n".format(key, replacedKey,row["val"])
                linkStr = linkStr + tmpLinkStr

        if row["_cur_node_type"] == "func":
            dotText = dotText + """    <tr><td colspan="2" port="{}">{}</td></tr>\n""".format(  replacedKey, row["val"])
        else:
            dotText = dotText + """    <tr><td>{}</td><td port="{}">{}</td></tr>\n""".format(nodeType,replacedKey, row["key"])

    dotText = dotText + """    </table>>];\n"""


dotText = dotText + linkStr

dotText = dotText + """}"""
print(dotText)
