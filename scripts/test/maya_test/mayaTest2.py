import mpdb
import pymel.core as pm

crv = pm.circle(ch=0)[0]

for cv in crv.cv:
    pos = cv.getPosition(space="world")
    loc = pm.spaceLocator(p=pos)
    mpdb.set_trace()
    print (loc,pos)