def mainTree() :
    return ("/","tree")

def otherTreesToKeepWhenSkimming() :
    return []

def leavesToBlackList() :
    return []

def ttreecacheMB() :
    return 20

def trace() :
    return False

def nCoresDefault() :
    return 4

def useCachedFileLists() :
    return False

def maxArrayLength() :
    return 256

def computeEntriesForReport() :
    return False

def printNodesUsed() :
    return False

def fakeString() :
    return ";FAKE"

def cppFiles() :
    return []

def hadd() :
    return "hadd"

def dictionariesToGenerate() :
    return []

def initializeROOT(r) :
    r.gROOT.SetStyle("Plain")
    r.gStyle.SetPalette(1)
    r.TH1.SetDefaultSumw2(True)
    r.gErrorIgnoreLevel = 2000
    r.gROOT.SetBatch(True)
