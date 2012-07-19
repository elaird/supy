import os,supy,unittest

def runAll(lst = ["integers"]) :
    for item in lst :
        cmd = "cd %s/tests/%s && python __init__.py"%(supy.whereami(), item)
        print cmd
        os.system(cmd)
