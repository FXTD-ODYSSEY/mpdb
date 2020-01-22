import sys
MODULE = r"D:\Users\82047\Desktop\repo\mpdb\scripts\test\maya_test"
if MODULE not in sys.path:
    sys.path.append(MODULE)

import mayaTest
reload(mayaTest)

mayaTest.main()
