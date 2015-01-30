def experiment() :
    '''Used by specifications in sites/__init__.py'''
    return ""

def mainTree() :
    return ("/","tree")

def otherTreesToKeepWhenSkimming() :
    return []

def leavesToBlackList() :
    return []

def ttreecacheMB() :
    return 20

def trace() :
    '''Record dependencies of (wrappedChain.calculable)s'''
    return False

def nCoresDefault() :
    return 4

def useCachedFileLists() :
    '''WARNING: False is always correct. True saves time, but may bite you.

    The cache is keyed on sample name, and is not updated
    by changing the sample definition or actual files on disk.
    Clear the cache by removing sample_name.inputFiles'''
    return False

def maxArrayLength() :
    '''In case of array TTree branches, the maximum length.  STL (eg, std::vector) has no maximum.'''
    return 256

def computeEntriesForReport() :
    '''WARNING: If set to True, all files in chain must be read before looping, which may be slow.'''
    return False

def computeEntriesAtMakeFileList():
    '''WARNING: If set to True, all files in sample must be read before file list is cached, which may be slow.'''
    return False

def printNodesUsed() :
    '''Dumps nodes accessed from wrappedChain to stdout at end of job: useful for debugging.'''
    return False

def fakeString() :
    '''String used by plotter to identify wrappedChain.calculable.isFake()'''
    return ";FAKE"

def hadd() :
    '''You may wish to use an alternative to hadd, such as bin/phaddy'''
    return "hadd"

def cppROOTDictionariesToGenerate() :
    '''List of pairs of strings. pair[0] is the C++ class name; pair[1] is a semicolon list of required header files.
    Used by utils.root.generateDictionaries().
    See https://github.com/betchart/susycaf/blob/master/configuration.py for an example.'''
    return []

def cppFiles() :
    '''List of strings specifying cpp files to compile and load into ROOT namespace.'''
    return []

def initializeROOT(r, cppFiles = []) :
    r.gROOT.SetStyle("Plain")
    r.gStyle.SetPalette(1)
    r.TH1.SetDefaultSumw2(True)
    r.gErrorIgnoreLevel = 2000
    r.gROOT.SetBatch(True)

    for sourceFile in cppFiles :
        r.gROOT.LoadMacro(sourceFile+"+")


def haddErrorsToIgnore() :
    return ["", "Exception in thread QueueFeederThread (most likely raised during interpreter shutdown):",]


def LorentzVectorType() :
    return ('PtEtaPhiM4D','float')

def PositionVectorType() :
    return ('Cartesian3D','float')
