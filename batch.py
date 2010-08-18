import sys,analysis

def getArg() :
    if sys.argv[-1]=="-b" : sys.argv.pop() #undo modification done in prep.py
    if len(sys.argv)<2 :
        print 'batch.py requires an argument, e.g. try \"python batch.py analyses/example.py"'
        exit()
    return sys.argv[1]

def getAnalysis() :
    count = 0
    theAnalysis = None
    for itemName in dir(eval(module)) :
        item=eval(module+"."+itemName)
        if hasattr(item,"__class__") and item.__class__ is analysis.analysis :
            count+=1
            theAnalysis = item
    assert count==1,arg+" needs exactly 1 analysis; it has "+str(count)
    return theAnalysis

arg = getArg()
module = arg.replace("analyses/","").replace(".py","")
exec("import "+module)
someAnalysis = getAnalysis()

for iSample in range(len(someAnalysis.listOfSamples)) :
    cmd="python "+" ".join(sys.argv[1:])+" --singlesampleid "+str(iSample)
    print cmd
    #import os
    #os.system(cmd)
