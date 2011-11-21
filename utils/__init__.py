from multiprocessing import Process,JoinableQueue
import os,traceback,sys,itertools
import ROOT as r
try:
    import numpy as np
except:
    pass

for module in ['algos','cms','io','root'] : exec("from %s import *"%module)

#####################################
hyphens="-"*115
#####################################
class vessel(object) : pass
#####################################
class vector(list) :
    def at(self, i) : return self[i]
    def size(self) : return len(self)
    def push_back(self, thing) : self.append(thing)
#####################################        
def hackMap(*args) :
    out = []
    func = args[0]
    for i in range(len(args[1])) :
        out.append(func(*tuple([x[i] for x in args[1:]])))
    return out
#####################################
def operateOnListUsingQueue(nCores,workerFunc,inList,daemon=True) :
    q = JoinableQueue()
    listOfProcesses=[]
    for i in range(nCores):
        p = Process(target = workerFunc, args = (q,))
        p.daemon = daemon
        p.start()
        listOfProcesses.append(p)
    map(q.put,inList)
    q.join()# block until all tasks are done
    #clean up
    for process in listOfProcesses :
        process.terminate()
#####################################
class qWorker(object) :
    def __init__(self,func = None) : self.func = func
    def __call__(self,q) :
        while True:
            item = q.get()
            try:
                if self.func : self.func(*item)
                else: item()
            except Exception as e:
                traceback.print_tb(sys.exc_info()[2], limit=20, file=sys.stdout)
                print e.__class__.__name__,":", e
            q.task_done()
#####################################        
def roundString(val, err, width=None, noSci = False, noErr = False) :
    err_digit = int(math.floor(math.log(abs(err))/math.log(10))) if err else 0
    val_digit = int(math.floor(math.log(abs(val))/math.log(10))) if val else 0
    dsp_digit = max(err_digit,val_digit)
    sci = (val_digit<-1 or err_digit>0) and not noSci

    precision = val_digit-err_digit if sci else -err_digit

    display_val = val/pow(10.,dsp_digit) if sci else val
    display_err = str(int(round(err/pow(10,err_digit))))

    while True:
        display_sci = ("e%+d"%dsp_digit) if sci else ""
        returnVal = "%.*f(%s)%s"%(precision,display_val,display_err,display_sci) if not noErr else "%.*f%s"%(precision,display_val,display_sci)
        if (not width) or len(returnVal) <= width or precision < 1: break
        else:
            display_err = "-"
            if not precision :
                display_val*=10
                dsp_digit-=1
            precision-=1
    return returnVal
#####################################
def dependence(TH2, name="", minimum=-5, maximum=5, inSigma = True) :
    if not TH2: return None
    if TH2.GetDirectory() : TH2.GetDirectory().cd()
    dep = TH2.Clone(name if name else TH2.GetName()+"_dependence")
    dep.SetZTitle("dependence")
    norm = TH2.Integral()
    projX = TH2.ProjectionX()
    projY = TH2.ProjectionY()
    for iX in range(1,TH2.GetNbinsX()+1) :
        for iY in range(1,TH2.GetNbinsY()+1) :
            X = projX.GetBinContent(iX)
            Y = projY.GetBinContent(iY)
            bin = TH2.GetBin(iX,iY)
            XY = TH2.GetBinContent(bin)
            dBin = math.log(norm*XY/X/Y) if XY else 0
            eX = projX.GetBinError(iX)
            eY = projX.GetBinError(iY)
            eXY = TH2.GetBinError(bin)
            eBin = math.sqrt((eXY/XY)**2 + (eX/X)**2 + (eY/Y)**2) if XY else 1# faulty assumption of independent errors
            #dep.SetBinContent(bin, min(maximum,max(minimum,math.log(norm*XY/X/Y)/(eBin if eBin and inSigma else 1))) if XY else 0)
            dep.SetBinContent(bin, min(maximum,max(minimum,dBin/(eBin if eBin and inSigma else 1))) if XY else 0)
            dep.SetBinError(bin,0)
    dep.SetMinimum(minimum)
    dep.SetMaximum(maximum)
    
    return dep
#####################################
class rBin(object) :
    def __init__(self,num,den,i, minRelUnc=0.25) :
        self.lowEdge = num.GetBinLowEdge(i)
        self.num = num.GetBinContent(i)
        self.enum = num.GetBinError(i)
        self.den = den.GetBinContent(i)
        self.eden = den.GetBinError(i)
        self.next = None
        self.minRelUnc = minRelUnc
        return
        
    def ratio(self) :
        return self.num / self.den if self.den else 0
    
    def error(self) :
        return math.sqrt(self.enum**2 + self.ratio()**2 * self.eden**2) / self.den if self.den else 0
    
    def eatNext(self) :
        if not self.next: return 
        self.num += self.next.num
        self.den += self.next.den
        self.enum = math.sqrt(self.enum**2+self.next.enum**2)
        self.eden = math.sqrt(self.eden**2+self.next.eden**2)
        self.next = self.next.next
        return
        
    def ok(self) :
        return self.empty() or ( self.num!=0 and self.enum/self.num < self.minRelUnc and \
                                 self.den!=0 and self.eden/self.den < self.minRelUnc)
    
    def empty(self) :
        return self.num==0 and self.den==0
    
    def subsequentEmpty(self) :
        return  (not self.next) or self.next.empty() and self.next.subsequentEmpty()
    
    def eatMe(self,lastNonZeroOK=None) :
        if not lastNonZeroOK :
            while self.next and not self.ok():
                self.eatNext()
        if self.next and self.next.eatMe( self if self.ok() and not self.empty() else lastNonZeroOK ) :
            self.eatNext()
        if (not self.ok()) and \
           (not self.subsequentEmpty()) and \
           (self.nextNonZeroOKlowEdge() - self.lowEdge < \
            self.lowEdge - lastNonZeroOK.lowEdge ) :
            while self.next and not self.ok() :
                self.eatNext()
        return not self.ok()
    
    def nextNonZeroOKlowEdge(self) :
        if self.next.ok() and not self.next.empty() :
            return self.next.lowEdge
        return self.next.nextNonZeroOKlowEdge()
#####################################
def ratioHistogram(num,den) :
    bins = [ rBin(num,den,i+1) for i in range(num.GetNbinsX()) ]
    for i in range(len(bins)-1) : bins[i].next = bins[i+1]
    b = bins[0]
    b.eatMe()
    bins = [b]
    while(b.next) :
        bins.append(b.next)
        b=b.next
        
    lowEdges = [b.lowEdge for b in bins] + [num.GetXaxis().GetBinUpEdge(num.GetNbinsX())]
    den.GetDirectory().cd()
    ratio = r.TH1D("ratio"+num.GetName()+den.GetName(),"",len(lowEdges)-1, array.array('d',lowEdges))
    
    for i,bin in enumerate(bins) :
        ratio.SetBinContent(i+1,bin.ratio())
        ratio.SetBinError(i+1,bin.error())

    return ratio
#####################################
def intFromBits(bits) :
    return sum([j[1] * (1<<j[0]) for j in enumerate(reversed(bits))])
#####################################
def splitList(List,item) :
    if item not in List: return [List]
    i = List.index(item)
    return [List[:i+1]] + splitList(List[i+1:],item)
#####################################
def pages(blocks,size) :
    iBreak = next((i-1 for i in range(len(blocks)) if len(sum(blocks[:i],[]))>size), None)
    return [blocks] if not iBreak else [blocks[:iBreak]] + pages(blocks[iBreak:],size)
#####################################
def jsonFromRunDict(runDict) :
    json = {}
    for run,lumis in runDict.iteritems() :
        blocks = []
        for lumi in sorted(lumis) :
            if (not blocks) or lumi-blocks[-1][-1]!=1: blocks.append([lumi])
            else : blocks[-1].append(lumi)
        json[str(run)] = [[block[0], block[-1]] for block in blocks]
    return json
#####################################
def justNameTitle(tkey) :
    name,title = tkey.GetName(),tkey.GetTitle()
    name = name.replace('-SLASH-','/').replace('-SEMI-',';').replace('-COLON-',':')
    L = len(title)
    return ( (name,"") if name == title else
             (name[:-L],title) if name[-L:] == title else
             (name,title) )
#####################################
def optimizationContours(signals, backgds, left = True, right = True, var = "") :
    stat = r.gStyle.GetOptStat()
    r.gStyle.SetOptStat(0)
    nBins = signals[0].GetNbinsX()
    edges = [signals[0].GetBinLowEdge(i) for i in range(nBins+2)]
    signal = sum([np.array([sample.GetBinContent(i) for i in range(nBins+2)]) for sample in signals])
    backgd = sum([np.array([sample.GetBinContent(i) for i in range(nBins+2)]) for sample in backgds])

    if left^right :
        eff = np.array([ sum( signal[::left-right][i:]) for i in range(len(signal)) ])[::left-right] / sum(signal)
        s = np.array([ sum( signal[::left-right][i:]) for i in range(len(signal)) ])[::left-right]
        b = np.array([ sum( backgd[::left-right][i:]) for i in range(len(backgd)) ])[::left-right]
        pur = s / np.maximum(1e-6,s+b)

        gEff, gPur = [r.TGraph(nBins, np.array(edges), vals) for vals in [eff,pur]]
        for g,col in [(gEff,r.kRed),(gPur,r.kBlue)]:
            g.SetTitle(var)
            g.SetLineColor(col)
            g.SetMinimum(0)
            g.SetMaximum(1)
        c = r.TCanvas()
        c.SetGrid()
        gEff.Draw("AL")
        gPur.Draw("L")
        return c,zip(pur,eff),gEff,gPur

    def h(name,scale="") : return r.TH2D(name,name+";lower;upper;"+scale,nBins,0,nBins,nBins,0,nBins)
    eff,pur,signalb,ssqrtb,contour = (h('efficiency'),h('purity'),h("signalOverBackground"),h('signalOverSqrtBackground',"1e1"),h('contour'))

    S = float(sum(signal))
    for low,up in itertools.combinations(range(nBins),2) :
        s = sum(signal[low:up])
        b = sum(backgd[low:up])
        eff.SetBinContent(low+1,up+1,s/S)
        pur.SetBinContent(low+1,up+1,s/float(s+b))
        if not b : continue
        signalb.SetBinContent(low+1,up+1,min(10,s/float(b)))
        ssqrtb.SetBinContent(low+1,up+1,s/math.sqrt(b))
        
    contour = signalb.Clone("contour")
    contour.SetContour(2,np.array([4.4,9.9]))
    signalb.SetContour(10,np.arange(0,10,1.0))
    c = r.TCanvas()
    c.Divide(2,2)
    option = "cont4z"
    option = "colz"
    c.cd(1); eff.Draw(option) ; contour.Draw("cont3 same")
    c.cd(2); pur.Draw(option) ; contour.Draw("cont3 same")
    c.cd(3); signalb.Draw(option); contour.Draw("cont3 same")
    c.cd(4); ssqrtb.Draw(option);  contour.Draw("cont3 same")
    r.gStyle.SetOptStat(stat)
    return [c,eff,pur,signalb,ssqrtb,contour]
#####################################
