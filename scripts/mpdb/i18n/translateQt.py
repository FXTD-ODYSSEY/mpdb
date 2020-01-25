import os

DIR = os.path.dirname(__file__)
pylupdate5 = r"F:\Anaconda3\Scripts\pylupdate5.exe"
target_dir = os.path.dirname(DIR)
py_list = ' '.join(['"%s"' % os.path.join(target_dir,file_name) for file_name in os.listdir(target_dir) if file_name.endswith("py")])

output_list = ["zh_CN.ts"]

for output in output_list:
    output = os.path.join(target_dir,"i18n",output)
    commnad = '{pylupdate5} -verbose {file_list} -ts {output}'.format(output=output,pylupdate5=pylupdate5,file_list=py_list)
    os.system(commnad)
