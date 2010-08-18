def getOpts() :
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--loop",                                dest = "loop",
                      default = None,  help = "loop over events using N cores", metavar = "N")
    parser.add_option("--profile",      action = "store_true", dest = "profile",
                      default = False, help = "profile the code")
    parser.add_option("--onlymerge",    action = "store_true", dest = "onlymerge",
                      default = False, help = "used with --loop to skip the loop and simply merge the output files")
    parser.add_option("--singlesampleid",                      dest = "singlesampleid",
                      default = None,  help = "[used with batch.py]", metavar = "id")
    (options, args) = parser.parse_args()
    return options,args

def setRootBatchMode() :
    import sys
    sys.argv.append("-b")

def globalSetup(listOfSourceFiles=[]) :
    import ROOT as r
    for sourceFile in listOfSourceFiles :
        r.gROOT.LoadMacro(sourceFile+"+")
    r.gROOT.SetStyle("Plain")
    r.gStyle.SetPalette(1)
    #r.TH1.SetDefaultSumw2(True)#comment until ROOT 5.24, which has a needed bug-fix
    r.gErrorIgnoreLevel=2000
    r.gROOT.SetBatch(True)

options,args = getOpts()
setRootBatchMode()
globalSetup(listOfSourceFiles=["pragmas.h","helpers.C"])

