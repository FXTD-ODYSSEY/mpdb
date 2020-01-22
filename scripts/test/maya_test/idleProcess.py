import time
import maya
try:
    from PySide2 import QtCore
except:
    from PySide import QtCore

def main():
        
    curr = time.time()

    while True:
        elapsed = abs(curr - time.time())
        if elapsed > 3:
            break

        print elapsed
        QtCore.QCoreApplication.processEvents()
        maya.utils.processIdleEvents()

if __name__ == "__main__":
    main()

# import idleProcess
# reload(idleProcess)
# idleProcess.main()