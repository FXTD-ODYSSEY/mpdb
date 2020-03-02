import maya.cmds as cmds


# ----------------------------------------------------------------------------
# import sys
# MODULE = r"D:\Users\82047\Desktop\repo\mpdb\scripts"
# if MODULE not in sys.path:
#     sys.path.append(MODULE)

# try:
        
#     import mpdb
#     reload(mpdb)

#     mpdb.install()
    
# except:
#     import traceback
#     traceback.print_exc()
# # debugger.deleteEvent()

# ----------------------------------------------------------------------------

INSTALL_COMMAND = """
import mpdb
mpdb.install()
"""

if not cmds.about(batch=True):
    cmds.evalDeferred(INSTALL_COMMAND)
