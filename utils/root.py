import os,math, ROOT as r
try:
    import numpy as np
except:
    pass

#####################################
def generateDictionaries(inList) :
    wd = os.getcwd()
    r.gSystem.ChangeDirectory(wd+"/cpp")
    for item in inList : r.gInterpreter.GenerateDictionary(*item)
    r.gSystem.ChangeDirectory(wd)
#####################################
def compileSources(inList) :
    for sourceFile in inList :
        r.gROOT.LoadMacro(sourceFile+"+")
#####################################
lvClass = None
def LorentzV(*args) :
    global lvClass
    if lvClass is None : lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('float'))
    return lvClass(*args)
#####################################
def delete(thing) :
    #free up memory (http://wlav.web.cern.ch/wlav/pyroot/memory.html)
    thing.IsA().Destructor(thing)
#####################################
def canvas(name) :
    c = r.TCanvas(name,name, 260*2, 200*2)
    c.SetTopMargin(0.0)
    c.SetBottomMargin(0.0)
    c.SetRightMargin(0.0)
    c.SetLeftMargin(0.0)
    return c
#####################################
def rHist(name,bins,edges,poissonErrors=False) :
    hist = r.TH1D(name,"",len(bins), np.array(edges,dtype='double'))
    for i,bin in enumerate(bins) : 
        hist.SetBinContent(i+1,bin)
        hist.SetBinError(i+1,math.sqrt(bin) if poissonErrors else 0)
    return hist
#####################################
def tCanvasPrintPdf(canvas, fileName, verbose = True) :
    illegal = [':','[',']','(',')']
    for ill in illegal : fileName = fileName.replace(ill,"_")
    canvas.Print("%s.eps"%fileName)
    os.system("epstopdf %s.eps"%fileName)
    os.system("rm %s.eps"%fileName)
    if verbose : print "Output file: %s.pdf"%fileName
#####################################
