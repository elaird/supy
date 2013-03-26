import configuration,os,math,array, ROOT as r
try:  import numpy as np
except: np = None

#####################################
def gDirectory() :
    return r.gDirectory if type(r.gDirectory)==r.TDirectory else r.gDirectory.CurrentDirectory()
#####################################
def generateDictionaries(inList, dir = None) :
    '''http://root.cern.ch/drupal/content/how-generate-dictionary'''
    wd = os.getcwd()
    r.gSystem.ChangeDirectory((dir if dir!=None else wd)+"/cpp")
    for item in inList : r.gInterpreter.GenerateDictionary(*item)
    r.gSystem.ChangeDirectory(wd)
#####################################
lvClass = None
def LorentzV(*args) :
    global lvClass
    if lvClass is None :
        coord,prec = configuration.LorentzVectorType()
        lvClass = r.Math.LorentzVector(getattr( r.Math, coord)(prec))
    return lvClass(*args)
#####################################
pvClass = None
def PositionV(*args) :
    global pvClass
    if pvClass is None :
        coord,prec = configuration.PositionVectorType()
        pvClass = r.Math.PositionVector3D(getattr( r.Math, coord)(prec))
    return pvClass(*args)
#####################################
def Dot(lvA,lvB) :
    return lvA.E()*lvB.E() - lvA.P()*lvB.P()*r.Math.VectorUtil.CosTheta(lvA,lvB)
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
def binValues(hist) : return [hist.GetBinContent(i) for i in range(hist.GetNbinsX()+2)]
#####################################
def tCanvasPrintPdf(canvas, fileName, verbose = True, option = '' ) :
    illegal = [':','[',']','(',')']
    for ill in illegal : fileName = fileName.replace(ill,"_")
    canvas.Print(fileName+".pdf" + option,"pdf")
    if verbose : print "Output file: %s.pdf"%fileName
#####################################
def ratioHistogram( num, den, relErrMax=0.25) :

    def groupR(group) :
        N,D = [float(sum(hist.GetBinContent(i) for i in group)) for hist in [num,den]]
        return N/D if D else 0

    def groupErr(group) :
        N,D = [float(sum(hist.GetBinContent(i) for i in group)) for hist in [num,den]]
        ne2,de2 = [sum(hist.GetBinError(i)**2 for i in group) for hist in [num,den]]
        return math.sqrt( ne2/N**2 + de2/D**2 ) * N/D if N and D else 0

    def regroup(groups) :
        err,iG = max( (groupErr(g),groups.index(g)) for g in groups )
        if err < relErrMax or len(groups)<3 : return groups
        iH = max( [iG-1,iG+1], key = lambda i: groupErr(groups[i]) if 0<=i<len(groups) else -1 )
        iLo,iHi = sorted([iG,iH])
        return regroup(groups[:iLo] + [groups[iLo]+groups[iHi]] + groups[iHi+1:])

    try :
        groups = regroup( [(i,) for i in range(1,1+num.GetNbinsX())] )
    except :
        print 'Ratio failed:', num.GetName()
        groups = [(i,) for i in range(1,1+num.GetNbinsX()) ]
    ratio = r.TH1D("ratio"+num.GetName()+den.GetName(),"",len(groups), array.array('d', [num.GetBinLowEdge(min(g)) for g in groups ] + [num.GetXaxis().GetBinUpEdge(num.GetNbinsX())]) )
    for i,g in enumerate(groups) :
        ratio.SetBinContent(i+1,groupR(g))
        ratio.SetBinError(i+1,groupErr(g))
    return ratio
#####################################
def divideX(hist2D,histX=None,ratherY=False) :
    '''Divide each slice of 2D histogram in X(or Y) by 1D histogram.'''
    if not histX :
        histX = hist2D.ProjectionX() if not ratherY else hist2D.ProjectionY()
    divX = hist2D.Clone(hist2D.GetName()+'_divide%s_'%('Y' if ratherY else 'X')+histX.GetName())
    assert (hist2D.GetNbinsX() if not ratherY else hist2D.GetNbinsY())==histX.GetNbinsX()
    for iX in range(2+histX.GetNbinsX()) :
        finv = histX.GetBinContent(iX)
        f = 1./finv if finv else 1.
        for iY in range(2+(hist2D.GetNbinsY() if not ratherY else hist2D.GetNbinsX())) :
            args = (iX,iY) if not ratherY else (iY,iX)
            divX.SetBinContent(*(args+(f*divX.GetBinContent(*args),)))
            divX.SetBinError(*(args+(f*divX.GetBinError(*args),)))
    return divX
#####################################
def subtractX(hist2D,histX,ratherY=False) :
    '''Subtract 1D histogram from each slice of of 2D histogram in X(or Y).'''
    divX = hist2D.Clone(hist2D.GetName()+'_divide%s_'%('Y' if ratherY else 'X')+histX.GetName())
    assert (hist2D.GetNbinsX() if not ratherY else hist2D.GetNbinsY())==histX.GetNbinsX()
    for iX in range(2+histX.GetNbinsX()) :
        f = histX.GetBinContent(iX)
        ferr = histX.GetBinError(iX)
        for iY in range(2+(hist2D.GetNbinsY() if not ratherY else hist2D.GetNbinsX())) :
            args = (iX,iY) if not ratherY else (iY,iX)
            divX.SetBinContent(*(args+(divX.GetBinContent(*args)-f,)))
            divX.SetBinError(*(args+(math.sqrt(divX.GetBinError(*args)**2+ferr**2),)))
    return divX
