import pandas as pd
import re

def template_to_regex(template):
    regex = template
    regex = regex.replace("\\", "\\\\")
    regex = regex.replace(".", "\.")
    regex = regex.replace("*", "\*")

    regex = regex.replace("<\*>", ".*")

    regex = regex.replace("(", "\(")
    regex = regex.replace(")", "\)")

    regex = regex.replace("[","\[")
    regex = regex.replace("]","\]")

    regex = regex.replace("|","\|")

    regex = regex.replace("+", "\+")
    regex = regex.replace("?", "\?")
    regex = regex.replace("$", "\$")
    regex = regex.replace("@", "\@")
    regex = regex.replace("^", "\^")

    #regex = regex.replace(":", "\:")
    #regex = regex.replace("\"", "\\\"")

    regex = regex + '$'

    return regex

def tmp0_match_tmp1(tmp0, tmp1):
    regex0 = template_to_regex(tmp0)
    match = re.search(regex0, tmp1)
    if(match):
        return True
    else:
        return False

def insertTemplate(tmp, tmplist):
    index = 0
    for t in tmplist:
        if((tmp0_match_tmp1(t, tmp) == True) and (tmp0_match_tmp1(tmp, t) == False)):
            return index
        else:
            index = index+1
    return -1

contentlist = pd.read_csv("../Data/Template/Refine_v2/Zookeeper_templates.csv", usecols=['Template'])
templates = contentlist['Template']

templates_new = []
for index in range(0,len(templates)):
    if(templates[index] in templates_new):
        pass
    else:
        pos = insertTemplate(templates[index], templates_new)
        if(pos == -1):
            templates_new.append(templates[index])
        else:
            templates_new.insert(pos, templates[index])

print(len(templates))
print(len(templates_new))

refinedtmps = pd.DataFrame({'Template' : templates_new})
refinedtmps.to_csv("../Data/Template/Refine_v2/Zookeeper_templates.csv")