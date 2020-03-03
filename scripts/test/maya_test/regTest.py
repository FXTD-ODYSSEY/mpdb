import re


# def replaceText(text):
#     return re.sub(,"__name__ == 'mpdb'",text.strip())


text = """
'''
__name__=="__main__"

""

'''
__name__=="__main__"

'''

"""
pattern = r"__name__\s*==\s*[\',\"]__main__[\',\"]"
result = re.search(r"[\',\"](?:\n|.)*?%s(?:\n|.)*?[\',\"]" % pattern,text)

print result
print result.group(0)
# print replaceText(text)