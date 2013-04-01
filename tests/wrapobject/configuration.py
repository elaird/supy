import supy
from supy.defaults import *

def localpath() :
    return "tests/wrapobject"
def ttreecacheMB() :
    return 20

def librariesToLoad() :
    return ['libPhysics.so',
            "%s/cpp/libSusy.so"%supy.whereami()
            ]

def initializeROOT(r, cppFiles = []) :
    supy.defaults.initializeROOT(r, cppFiles)
    for l in librariesToLoad() :
        r.gSystem.Load(l)

