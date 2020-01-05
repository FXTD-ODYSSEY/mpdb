import maya.cmds as cmds


# ----------------------------------------------------------------------------


INSTALL_COMMAND = """
import channelBoxPlus
channelBoxPlus.install(threshold=0.75)
"""


# ----------------------------------------------------------------------------


cmds.evalDeferred(INSTALL_COMMAND)
