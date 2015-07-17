import math,operator,itertools,random,string, ROOT as r
from supy import wrappedChain,utils,whereami
from . import secondary
try: import numpy as np
except: np = None

#####################################
class localEntry(wrappedChain.calculable) :
    def update(self,localEntry) :
        self.value = localEntry
#####################################
class entry(wrappedChain.calculable) :
    def update(self,localEntry) :
        self.value = self.source.entry
#####################################
class chain_access(wrappedChain.calculable) :
    @property
    def name(self) : return "chain"
    def update(self,_) :
        self.value = self.source._wrappedChain__chain if type(self.source)==wrappedChain else self.source.someDict._wrappedChain__chain
#####################################
class treeFileName(wrappedChain.calculable) :
    def update(self,_) :
        self.value = self.source['chain'].GetFile().GetName().split('/')[-1]
#####################################
class abbreviation(wrappedChain.calculable) :
    @property
    def name(self) : return self.abr
    def __init__(self, var = "", abr = "", fixes = ("","")) :
        self.moreName = var.join(fixes)
        self.abr = abr.join(fixes)
    def update(self,_) : self.value = self.source[self.moreName]
#####################################
class crock(wrappedChain.calculable) :
    def update(self,localEntry) : self.value = {}
#####################################
class fixedValue(wrappedChain.calculable) :
    @property
    def name(self) :
        return self.label
    def __init__(self, label = "", value = None) :
        self.label = label
        self.value = value
    def update(self, ignored) :
        pass


class IndicesFiltered(wrappedChain.calculable):
    @property
    def name(self):
        return self.label

    def __init__(self, label="", accept="", reject=""):
        for item in ["label", "accept", "reject"]:
            setattr(self, item, eval(item))

    def update(self,_):
        self.value = filter(lambda x:x not in self.source[self.reject],
                            self.source[self.accept])


class IndexMatchMap(wrappedChain.calculable):
    @property
    def name(self):
        return self.label

    def __init__(self, label="", keyP4="", keyIndices="",
                 valueP4="", valueIndices="", maxDR=None):
        for item in ["label", "keyP4", "keyIndices",
                     "valueP4", "valueIndices", "maxDR"]:
            setattr(self, item, eval(item))

    def update(self,_):
        self.value = {}
        keyP4s = self.source[self.keyP4]
        valueP4s = self.source[self.valueP4]
        for iKey in self.source[self.keyIndices]:
            dRs = []
            for iValue in self.source[self.valueIndices]:
                dR = r.Math.VectorUtil.DeltaR(keyP4s.at(iKey), valueP4s.at(iValue))
                if self.maxDR and self.maxDR < dR:
                    continue
                dRs.append((dR, iValue))
            if dRs:
                self.value[iKey] = min(dRs)[1]


class SumP4(wrappedChain.calculable):
    def __init__(self, collection="", indices=""):
        self.fixes = (collection, indices)

    def update(self,_):
        self.value = utils.LorentzV()
        for i in self.source[self.fixes[1]]:
            self.value += self.source[self.fixes[0]].at(i)


class value(wrappedChain.calculable) :
    def __init__( self, var, indices = None, index = None, short = None) :
        self.fixes = ("%s."%var, "%d%s"%(index, short if indices!=None and short!=None else indices) if index!=None else "")
        for item in ['var','indices','index','short'] : setattr(self,item,eval(item))
    def update(self,_) :
        var = self.source[self.var]
        indices = [] if self.index is None else self.source[self.indices]
        self.value = self.function( var if self.index is None else
                                    var[self.source[self.indices][self.index]])  if self.index<len(indices) else None
    @staticmethod
    def function(x) : return x
#####################################
class pt(value) :
    @staticmethod
    def function(x) : return x.pt()
#####################################
class eta(value) :
    @staticmethod
    def function(x) : return x.eta()
#####################################
class size(value) :
    @staticmethod
    def function(x) : return len(x)


class keys(value) :
    @staticmethod
    def function(x) : return x.keys()


class values(value) :
    @staticmethod
    def function(x) : return x.values()




#####################################
class Ratio(secondary) :
    def __init__(self, var=None, binning=(0,0,0), thisSample = None, target = ("",[]), groups = []) :
        self.fixes = (var,"")
        self.defaultValue = 1.0

        self.thisGroup = next((pre for pre,samples in groups if thisSample in [s.split('.')[0] for s in samples]),
                              next((pre for pre,samples in groups if not samples and thisSample.find(pre)==0),
                                   None ))
        if self.thisGroup==None and not (thisSample in target[1] or (not target[1]) and thisSample.find(target[0])==0) :
            groups.append((thisSample,[thisSample]))
            self.thisGroup = thisSample
            
        for item in ["var","binning","target","groups"] : setattr(self,item,eval(item))
        
    def setup(self,*_) :
        hists = self.fromCache( [self.target[0], self.thisGroup], ['unweighted'])
        source = hists[self.thisGroup]['unweighted']
        self.weights = hists[self.target[0]]['unweighted']
        if source and self.weights :
            self.weights.Scale(1./self.weights.Integral(0,self.weights.GetNbinsX()+1))
            source.Scale(1./source.Integral(0,source.GetNbinsX()+1))
            self.weights.Divide(source)
        else :
            print "Ratio did not find the group for %s."%self.thisGroup
            self.weights = None
       
    def uponAcceptance(self,ev) :
        me = ev[self.name]
        self.book.fill( ev[self.var], "allweighted", *self.binning       , title = ";%s;events / bin"%self.var )
        self.book.fill( ev[self.var], "meweighted", *self.binning, w = me, title = ";%s;events / bin"%self.var )
        self.book.fill( ev[self.var], "unweighted", *self.binning, w = 1,  title = ";%s;events / bin"%self.var )
        self.book.fill( math.log(max(1e-20,me)), "logMyValue", 40, -5, 5,     w = 1,  title = ";log(%s);events / bin"%self.name )

    def update(self,_) :
        self.value = self.defaultValue if not self.weights else self.weights.GetBinContent(self.weights.FindFixBin(self.source[self.var]))

    def organize(self,org) :
        [ org.mergeSamples( targetSpec = {"name":pre}, sources = samples ) if samples else
          org.mergeSamples( targetSpec = {"name":pre}, allWithPrefix = pre )
          for pre,samples in self.groups + ([self.target] if type(self)==Ratio else []) ]
#####################################
class Target(Ratio) :
    '''Provides weights to make var have the distribution given by target. '''
    def __init__(self, var = None, target = None, thisSample = None, groups = []) :
        self.fixes = (var,"")
        self.defaultValue = 1.0

        self.thisGroup = next((pre for pre,samples in groups if thisSample in [s.split('.')[0] for s in samples]),
                              next((pre for pre,samples in groups if not samples and thisSample.find(pre)==0),
                                   None ))
        if self.thisGroup==None :
            groups.append((thisSample,[thisSample]))
            self.thisGroup = thisSample
        
        for item in ["var","target","groups"] : setattr(self,item,eval(item))

    def setup(self,*_) :
        file = r.TFile.Open(self.target[0])
        self.weights = file.Get(self.target[1]).Clone("weights")
        self.weights.SetDirectory(0)
        file.Close()
        N = self.weights.GetNbinsX()
        self.binning = ( N, self.weights.GetBinLowEdge(1), self.weights.GetBinLowEdge(N+1))

        source = self.fromCache( [self.thisGroup], ['unweighted'])[self.thisGroup]['unweighted']
        if source and self.weights :
            self.weights.Scale(1./self.weights.Integral(0,self.weights.GetNbinsX()+1))
            source.Scale(1./source.Integral(0,source.GetNbinsX()+1))
            self.weights.Divide(source)
        else :
            print "Ratio did not find the group for %s."%self.thisGroup
            self.weights = None
#####################################
class Tridiscriminant(secondary) :
    def __init__(self, fixes = ("",""),
                 zero = {"pre":"", "samples":[], "tag":""},
                 pi23 = {"pre":"", "samples":[], "tag":""},
                 pi43 = {"pre":"", "samples":[], "tag":""},
                 dists = {}, # key = calc or leaf name : val = (bins,min,max)
                 bins = 60,
                 correlations = False,
                 otherSamplesToKeep = []
                 ) :
        for item in ['fixes','zero','pi23','pi43','dists','correlations','bins','otherSamplesToKeep'] : setattr(self,item,eval(item))
        self.moreName = "zero:"+zero['pre'] +"; pi23:"+pi23['pre']+"; pi43:"+pi43['pre']
        self.populations = [self.pi43,self.zero,self.pi23]
        self.sqrt3 = math.sqrt(3)

    def onlySamples(self) : return [item['pre'] for item in self.populations]
    def baseSamples(self) :
        samples = [item['samples'] for item in self.populations] + [self.otherSamplesToKeep]
        return set(sum(samples,[])) if all(samples) else []

    def likelihoods(self) :
        likes = [ self.fromCache([item['pre']], self.dists.keys()+[self.name], tag = item['tag'])[item['pre']]
                  for item in self.populations]
        missing = sum([[key for key,val in item.items() if val==None] for item in likes],[])
        if missing:
            print self.name, ': missing ',','.join(missing)
        for h in filter(None,sum([item.values() for item in likes],[])) :
            for i in range(2+h.GetNbinsX()) :
                if h.GetBinContent(i) < 0 : h.SetBinContent(i,0)
            integral = h.Integral(0,h.GetNbinsX()+1)
            if h : h.Scale(1./integral if integral else 1., 'width')
        return likes

    def setup(self,*_) : self.likes = self.likelihoods()

    def uponAcceptance(self,ev) :
        for key,val in self.dists.iteritems() : self.book.fill(max( val[1], min(val[2]-1e-6, ev[key])), key, *val, title = ";%s;events / bin"%key)
        self.book.fill(ev[self.name], self.name, self.bins, -1, 1, title = ";%s;events / bin"%self.name)
        if self.correlations :
            for (key1,val1),(key2,val2) in itertools.combinations(self.dists.iteritems(),2) :
                self.book.fill( ( max( val1[1], min( val1[2]-1e-6, ev[key1] )),
                                  max( val2[1], min( val2[2]-1e-6, ev[key2] ))),"_cov_%s_%s"%(key1,key2), *zip(val1,val2), title = ';%s;%s;events / bin'%(key1,key2))

    def likelihood(self,hist,val) :
        return hist.Interpolate(val)

    def update(self,_) :
        X,L,R = [ reduce( operator.mul,
                          [self.likelihood(item[key],max( val[1], min(val[2]-1e-6, self.source[key]))) for key,val in self.dists.iteritems() if item[key]],
                          1 )
                  for item in self.likes]
        self.value = math.atan2( (R-X)*self.sqrt3,
                                 2*L - (R+X) ) / math.pi # [-1,1] with zero peaking at zero, +/- pi23 peaking at +/- 0.666

    def organize(self,org) :
        org.mergeSamples( targetSpec = {'name':'data'}, sources = [s['name'] for s in org.samples if 'lumi' in s])
        org.scale(lumiToUseInAbsenceOfData=1)
        [ org.mergeSamples( targetSpec = {'name':item['pre']}, sources = item['samples'], scaleFactors = item['sf'] if 'sf' in item else [], force = True) if item['samples'] else
          org.mergeSamples( targetSpec = {'name':item['pre']}, allWithPrefix = item['pre'])
          for item in self.populations if org.tag == item['tag']]
        for sample in list(org.samples) :
            if (sample['name'],org.tag) not in [(item['pre'],item['tag']) for item in self.populations] :
                org.drop(sample['name'])

    def reportCache(self) :
        useTDR = True
        likes = self.likelihoods()
        fileName = '/'.join(self.outputFileName.split('/')[:-1]+[self.name])

        lumistamp = r.TLatex(0.65, 0.96, "19.6 fb^{-1} (8 TeV)")
        lumistamp.SetTextFont(42)
        lumistamp.SetNDC()
        stamp = r.TText()
        ssize = stamp.GetTextSize()
        def doStamp():
            stamp.SetTextFont(62)
            stamp.SetTextSize(ssize)
            stamp.DrawTextNDC(0.2 ,0.88,"CMS")
            stamp.SetTextSize(0.8 * ssize)
            #stamp.SetTextFont(52)
            #stamp.DrawTextNDC(0.27, 0.96, "Simulation")
            stamp.SetTextFont(42)
            lumistamp.Draw()

        optstat = r.gStyle.GetOptStat()
        if useTDR:
            r.gROOT.ProcessLine(".L %s/cpp/tdrstyle.C"%whereami())
            r.setTDRStyle()
        r.gStyle.SetOptStat(0)
        r.gStyle.SetPalette(1)
        c = r.TCanvas()
        utils.tCanvasPrintPdf(c, fileName, False, '[')
        with open(fileName+'.txt', "w") as file :
            print >> file, '\n'.join(str(d) for d in self.populations)
            print >> file
            for key in sorted((set(likes[0]) & set(likes[1]) & set(likes[2])), key = lambda k: -1 if self.name==k else k) :
                if not all(item[key] for item in likes) : continue
                dilutions = [utils.dilution(bins1,bins2) for bins1,bins2 in itertools.combinations([utils.binValues(item[key]) for item in likes],2)]
                print >> file, "\t".join([key.ljust(25)]+["%.4f"%d for d in dilutions])
                h = 1.1*max(item[key].GetMaximum() for item in likes)
                l = r.TLegend(0.73,0.67,0.93,0.9)
                l.SetBorderSize(0)
                l.SetFillColor(r.kWhite)
                l.SetTextFont(42)
                if not useTDR: l.SetHeader("Dilutions :  %.3f  %.3f  %.3f"%tuple(dilutions))
                for i,(item,color,style,lw,pop) in enumerate(zip(likes,[r.kBlack,r.kRed,r.kBlue],[9,1,7],[1,5,3],self.populations)) :
                    names = {'TridiscriminantWTopQCD':'#Delta',
                             'ProbabilityHTopMasses':'P_{MSD}',
                             'TopRatherThanWProbability':'P_{CSV}',
                             'muMetMt':'M_{T} (GeV)',
                             'elMetMt':'M_{T} (GeV)'
                             }
                    labels = {'wj':"Wj",'ttj_ph':"t#bar{t}","Multijet":"Mj"}
                    if useTDR:
                        item[key].SetTitle(';%s;Probability / bin'%names[key])
                        I = item[key].Integral()
                        item[key].Scale(1./I)
                    else: I = 1
                    item[key].UseCurrentStyle()
                    item[key].SetLineColor(color)
                    item[key].SetLineStyle(style)
                    item[key].SetLineWidth(lw)
                    item[key].SetMaximum(h/I)
                    item[key].SetMinimum(0)
                    if not useTDR: item[key].GetYaxis().SetTitle("pdf")
                    item[key].Draw("hist" + ('same' if i else ''))
                    l.AddEntry(item[key], labels[pop['pre']] if pop['pre'] in labels else pop['pre'],'l')
                l.Draw()
                doStamp()
                r.gPad.RedrawAxis()
                utils.tCanvasPrintPdf(c, fileName, False)
        c.Clear()
        c.Divide(3,2)
        covs = [self.fromCache([item['pre']], ["_cov_%s_%s"%pair for pair in itertools.combinations(self.dists.keys(),2)], tag = item['tag'])[item['pre']] for item in self.populations]
        for key in (set(covs[0]) & set(covs[1]) & set(covs[2])) :
            if not all(item[key] for item in covs) : continue
            hists = [item[key] for item in covs]
            deps = [utils.dependence(h,limit=1,inSigma=False) for h in hists]
            for i,(h,d,pop) in enumerate(zip(hists,deps,self.populations)) :
                d.SetTitle(pop['pre'])
                c.cd(i+1); h.Draw('colz')
                c.cd(i+4); d.Draw('colz')
            utils.tCanvasPrintPdf(c, fileName, False)
        c.Clear()
        for key in sorted((set(likes[0]) & set(likes[1]) & set(likes[2])), key = lambda k: -1 if self.name==k else k) :
            if not all(item[key] for item in likes) : continue
            for i,j in itertools.combinations(range(3),2) :
                k = next(k for k in range(3) if k not in [i,j])
                templates = [ utils.binValues(likes[ii][key]) for ii in [i,j] ]
                observed = utils.binValues(likes[k][key])
                try:  cs = utils.fractions.componentSolver(observed,templates)
                except: cs = None
                if not cs : continue
                notK = likes[k][key].Clone('bf_not_'+likes[k][key].GetName())
                notK.Reset()
                notK.Add(likes[i][key],likes[j][key],cs.fractions[0],cs.fractions[1])
                dil = utils.dilution(utils.binValues(likes[k][key]),utils.binValues(notK))
                l = r.TLegend(0.75,0.85,0.98,0.98)
                l.SetHeader("Dilution : %.3f"%dil)
                l.AddEntry(likes[k][key], self.populations[k]['pre'], 'l')
                l.AddEntry(notK, 'not '+self.populations[k]['pre'], 'l')
                notK.SetLineStyle(2)
                likes[k][key].Draw('hist')
                notK.Draw('hist same')
                l.Draw()
                utils.tCanvasPrintPdf(c, fileName, False)
        utils.tCanvasPrintPdf(c, fileName, True, ']')
        r.gStyle.SetOptStat(optstat)

#####################################
class Discriminant(secondary) :
    def __init__(self, fixes = ("",""),
                 left = {"pre":"","samples":[],"tag":""},
                 right = {"pre":"","samples":[],"tag":""},
                 dists = {}, # key = calc or leaf name : val = (bins,min,max)
                 bins = 50,
                 correlations = False
                 ) :
        for item in ['fixes','left','right','dists','correlations','bins'] : setattr(self,item,eval(item))
        self.moreName = "L:"+left['pre']+"; R:"+right['pre']+"; "+','.join(dists.keys())

    def onlySamples(self) : return [self.left['pre'],self.right['pre']]
    def baseSamples(self) : return set(self.left['samples']+self.right['samples']) if self.left['samples'] and self.right['samples'] else []

    def leftRight(self) :
        left = self.fromCache( [self.left['pre']], self.dists.keys()+[self.name], tag = self.left['tag'])[self.left['pre']]
        right = self.fromCache( [self.right['pre']], self.dists.keys()+[self.name], tag = self.right['tag'])[self.right['pre']]
        for h in filter(None,left.values()+right.values()) :
            integral = h.Integral(0,h.GetNbinsX()+1)
            if h : h.Scale(1./integral if integral else 1.)
        return left,right

    def setup(self,*_) :
        left,right = self.leftRight()
        for key in self.dists :
            if not left[key]: print "%s (left) : cannot find %s"%(self.name,key)
            if not right[key]: print "%s (right) : cannot find %s"%(self.name,key)
            if left[key] and right[key] : left[key].Divide(right[key])
            else: left[key] = None
        self.likelihoodRatios = left

    def reportCache(self) :
        L,R = self.leftRight()
        fileName = '/'.join(self.outputFileName.split('/')[:-1]+[self.name])
        optstat = r.gStyle.GetOptStat()
        r.gStyle.SetOptStat(0)
        c = r.TCanvas()
        c.Print(fileName+'.pdf[')
        with open(fileName+'.txt', "w") as file :
            print >> file, "L:", self.left
            print >> file, "R:", self.right
            print >> file
            for dilution,key in sorted([(round(utils.dilution(utils.binValues(L[key]),utils.binValues(R[key])),3),key)
                                        for key in set.intersection(set(L),set(R))], reverse=True) :
                if not (L[key] and R[key]) : continue
                if issubclass(type(L[key]),r.TH2) : continue
                print >> file, key, "\t", dilution
                h = 1.1*max(L[key].GetMaximum(),R[key].GetMaximum())
                L[key].SetLineColor(r.kRed);
                L[key].SetMaximum(h) ; L[key].SetMinimum(0)
                R[key].SetMaximum(h) ; R[key].SetMinimum(0)
                L[key].GetYaxis().SetTitle("pdf")
                R[key].GetYaxis().SetTitle("pdf")
                L[key].Draw("hist")
                R[key].Draw("histsame")
                l = r.TLegend(0.75,0.85,0.91,0.95)
                l.SetHeader("Dilution :  %.3f"%dilution)
                l.AddEntry(L[key], self.left['pre'],'l')
                l.AddEntry(R[key], self.right['pre'], 'l')
                l.Draw()
                c.Print(fileName+'.pdf')
        c.Print(fileName+'.pdf]')
        r.gStyle.SetOptStat(optstat)
        print "Wrote file: %s.txt"%fileName
        print "Wrote file: %s.pdf"%fileName

    def uponAcceptance(self,ev) :
        for key,val in self.dists.iteritems() : self.book.fill(ev[key], key, *val, title = ";%s;events / bin"%key)
        self.book.fill(ev[self.name], self.name, self.bins, 0, 1, title = ";%s;events / bin"%self.name)
        if self.correlations :
            for (key1,val1),(key2,val2) in itertools.combinations(self.dists.iteritems(),2) :
                self.book.fill( ( max( val1[1], min( val1[2]-1e-6, ev[key1] )),
                                  max( val2[1], min( val2[2]-1e-6, ev[key2] ))),"_cov_%s_%s"%(key1,key2), *zip(val1,val2), title = ';%s;%s;events / bin'%(key1,key2))

    def likelihoodRatio(self,key) :
        hist = self.likelihoodRatios[key]
        return 1 if not hist else hist.Interpolate(self.source[key])

    def update(self,_) :
        likelihoodRatios = [self.likelihoodRatio(key) for key in self.dists]
        self.value = 1. / ( 1 + reduce(operator.mul, likelihoodRatios, 1) )

    def organize(self,org) :
        [ org.mergeSamples( targetSpec = {'name':item['pre']}, sources = item['samples'], scaleFactors = item['sf'] if 'sf' in item else [], force = True) if item['samples'] else
          org.mergeSamples( targetSpec = {'name':item['pre']}, allWithPrefix = item['pre'])
          for item in [self.left,self.right] if org.tag == item['tag']]
        for sample in list(org.samples) :
            if (sample['name'],org.tag) not in [(self.left['pre'],self.left['tag']),(self.right['pre'],self.right['tag'])] :
                org.drop(sample['name'])
        for key,hists in list(org.steps[0].iteritems()) :
            example = next(iter(hists),None)
            if not example : continue
            if issubclass(type(example),r.TH2) : del org.steps[0][key]
#####################################
class SymmAnti(secondary) :
    def __init__(self, thisSample, var, varMax, nbins=100, inspect = False, weights = ['weight'],
                 funcEven = "pol8",
                 funcOdd = "pol8") :
        for item in ['thisSample','var','varMax','nbins','inspect','weights','funcEven','funcOdd'] : setattr(self,item,eval(item))
        self.fixes = (var,'')
        self.moreName = "%s: %.2f"%(var,varMax)
        self.__symm, self.__anti = None,None

    def uponAcceptance(self, ev) :
        w = reduce(operator.mul, [ev[W] for W in self.weights], 1)
        self.book.fill(ev[self.var], self.var, self.nbins, -self.varMax, self.varMax, title = ';%s;events / bin'%self.var, w = w)
        if not self.inspect : return
        symmanti = ev[self.name]
        if not symmanti : return
        sumsymmanti = sum(symmanti)
        symm,anti = symmanti
        self.book.fill(ev[self.var], self.var+'_symm', self.nbins, -self.varMax, self.varMax, w = w * symm / sumsymmanti, title = ';(symm) %s;events / bin'%self.var)
        self.book.fill(ev[self.var], self.var+'_anti', self.nbins, -self.varMax, self.varMax, w = w * anti / sumsymmanti, title = ';(anti) %s;events / bin'%self.var)
        self.book.fill(ev[self.var], self.var+'_flat', self.nbins, -self.varMax, self.varMax, w = w * 0.5  / sumsymmanti / self.varMax, title = ';(flat) %s;events / bin'%self.var)

    def update(self,_) :
        self.value = ()
        if not self.__symm : return
        val = self.source[self.var]
        anti = self.__anti.Eval(val)
        symm = max(self.__symm.Eval(val), 1.5*abs(anti))
        self.value = (symm,anti) if symm else (1,0)

    @staticmethod
    def prep(var,funcEven,funcOdd) :
        var.Scale(1./var.Integral(0,1+var.GetNbinsX()),'width')
        symm,anti = utils.symmAnti(var)
        low = symm.GetBinLowEdge(1)
        op = "QMI"
        gop = ""
        trunc = 0.992
        if type(funcEven)==r.TF1 :
            for i in range(funcEven.GetNpar()) : funcEven.SetParameter(i,0)
        symm.Fit(funcEven, op, gop, trunc*low, 0)
        if type(funcOdd)==r.TF1 :
            for i in range(funcOdd.GetNpar()) : funcOdd.SetParameter(i,0)
        anti.Fit(funcOdd, op, gop, trunc*low, 0)
        return symm,anti

    def setup(self,*_) :
        var = self.fromCache([self.thisSample], [self.var])[self.thisSample][self.var]
        if not var : print "cannot find cache:", self.name ; return
        if self.nbins != var.GetNbinsX() : print "inconsistent binning: %s, %s"%(self.name,self.thisSample)
        self.__stashsymmanti = self.prep(var,self.funcEven,self.funcOdd)
        self.__symm,self.__anti = [next(iter(h.GetListOfFunctions())) for h in self.__stashsymmanti]

    def reportCache(self) :
        r.gStyle.SetOptStat(0)
        fileName = '/'.join(self.outputFileName.split('/')[:-1]+[self.name])
        vars = dict([(sample,hists[self.var]) for sample,hists in self.fromCache(self.allSamples, [self.var]).items()])

        symmantis = dict([(s,(var,)+self.prep(var,self.funcEven,self.funcOdd)) for s,var in vars.items() if var])
        canvas = r.TCanvas()
        textlines = []
        for j,label in enumerate(['','Symmetric','Antisymmetric']) :
            leg = r.TLegend(0.85,0.85,0.98,0.98)
            limit_up = max([val[j].GetMaximum() for val in symmantis.values()] )
            limit_dn = min([val[j].GetMinimum() for val in symmantis.values()] + [0] )
            funcs = []
            for i,(sample,val) in enumerate(sorted(symmantis.items())) :
                val[j].SetMaximum(limit_up * 1.1)
                val[j].SetMinimum(limit_dn * 1.1)
                val[j].SetLineColor(i+1)
                val[j].SetMarkerColor(i+1)
                val[j].SetTitle("%s;%s;p.d.f"%(label,self.var))
                leg.AddEntry(val[j],sample,'l')
                val[j].Draw('hist' if not i else 'hist same')
                if not j : continue
                f = next(iter(val[j].GetListOfFunctions()))
                f.SetLineColor(i+1)
                f.SetLineStyle(2)
                f.SetLineWidth(1)
                f.Draw("same")
                textlines+=["%s : %s"%(sample,label)] + (['%+.4f\t%s'%(f.GetParameter(m),part) for m,part in enumerate(f.GetName().split('++'))] if '++' in f.GetName() else
                                                         ['[%d]\t%+.8f'%(m,f.GetParameter(m)) for m in range(f.GetNpar())]) + ['']
            leg.Draw()
            utils.tCanvasPrintPdf(canvas,fileName, verbose = j==2, option = ['(','',')'][j])
        with open(fileName+'.txt','w') as txtfile : print >> txtfile, '\n'.join(textlines)
#####################################
class TwoDChiSquared(secondary) :
    def __init__(self, var, samples, tag, binningX = (), binningY = (), labelsXY = (), tailSuppression = None ) :
        for item in ['var','samples','tag','binningX','binningY','labelsXY','tailSuppression'] : setattr(self,item,eval(item))
        self.fixes = (var,'')
        self.stats = ['w','w*X','w*Y','w*X*X','w*X*Y','w*Y*Y']
        self.labels = ['#sum %s'%s.replace('*','') for s in self.stats]
        self.N = len(self.stats)

    def onlySamples(self) : return ['merged']
    def baseSamples(self) : return self.samples
    def organize(self,org) :
        if org.tag ==self.tag :
            org.mergeSamples(targetSpec = {"name":'merged'}, sources = self.samples )

    def uponAcceptance(self,ev) :
        xy = ev[self.var]
        if not xy : return
        X,Y = xy
        w = ev['weight']
        for i,stat in enumerate( self.stats ) :
            self.book.fill(i, "stats", self.N,0,self.N,
                           w = eval(stat),
                           title = ";stats for %s;"%self.var,
                           xAxisLabels = self.labels )
        if self.binningX and self.binningY and self.labelsXY :
            self.book.fill( xy, "xy", *zip(self.binningX,self.binningY), title = ";%s;%s"%self.labelsXY)

    def update(self,_) :
        xy = self.source[self.var] + (1,)
        self.value = np.dot( xy, np.dot( self.matrix, xy) ) if len(xy)>2 else None

    def setup(self,*_) :
        hists = self.fromCache(['merged'],['stats','xy'], tag = self.tag)['merged']
        H = hists['stats']
        self.xy = hists['xy']
        if not H:
            print self.name, 'stats histogram not found.'
            self.matrix = np.array(3*[3*[0]])
            return

        if self.xy and self.tailSuppression :
            self.xy.SetTitle(';%s;%s'%self.labelsXY)
            xyDraw = self.xy.Clone('_draw')
            self.xySup = self.xy.Clone('_suppressed')
            self.xySup.Reset()
            self.xySup.SetTitle("Tail suppressed at %.2f"%self.tailSuppression)
            stats = dict((s,0) for s in self.stats)
            iX,iY,iZ = [r.Long() for _ in range(3)]
            while xyDraw.Integral() > self.tailSuppression * self.xy.Integral() :
                iMax = xyDraw.GetMaximumBin()
                xyDraw.SetBinContent(iMax,0)
                w = self.xy.GetBinContent(iMax)
                self.xySup.SetBinContent(iMax,w)
                self.xy.GetBinXYZ(iMax,iX,iY,iZ)
                X = self.xy.GetXaxis().GetBinCenter(iX)
                Y = self.xy.GetYaxis().GetBinCenter(iY)
                for item in self.stats : stats[item] += eval(item)
            stats = dict((key.replace('w','').replace('*',''),
                          val/stats['w']) for key,val in stats.items())
        else:
            H.Scale(1./H.GetBinContent(H.FindFixBin(self.stats.index('w'))))
            stats = dict([(L.replace('w','').replace('*',''),
                           H.GetBinContent(H.FindFixBin(i)))
                          for i,L in enumerate(self.stats)])

        inv = np.vstack( [np.vstack( [np.linalg.inv([[  stats['XX']-stats['X']*stats['X'],  stats['XY']-stats['X']*stats['Y']],
                                                     [  stats['XY']-stats['X']*stats['Y'],  stats['YY']-stats['Y']*stats['Y']]]),
                                      2*[0]] ).T,
                          3*[0]] )

        trans = np.array([[1,0,-stats['X']],
                          [0,1,-stats['Y']],
                          [0,0,1]])

        self.matrix = np.dot( trans.T, np.dot( inv, trans ) )

    def hzoom(self,h):
        def newbins(N,low,high):
            N_ = int(N/3)
            low_ = low
            high_ = N_ * (high-low)/N
            return (N_, low_, high_)
        h_ = r.TH2D(h.GetName()+"_zoom",h.GetTitle(), *(newbins(*self.binningX)+newbins(*self.binningY)))
        for iX in range(1,h_.GetNbinsX()):
            for iY in range(1,h_.GetNbinsY()):
                h_.SetBinContent(iX,iY, h.GetBinContent(iX,iY))
        return h_

    def fillsigmas(self, emptyhist):
        for iX in range(1,1+emptyhist.GetNbinsX()) :
            for iY in range(1,1+emptyhist.GetNbinsY()) :
                xy = (emptyhist.GetXaxis().GetBinCenter(iX),
                      emptyhist.GetYaxis().GetBinCenter(iY),
                      1)
                emptyhist.SetBinContent(iX, iY, math.sqrt( np.dot(xy, np.dot(self.matrix, xy) ) ) )
        return emptyhist

    def reportCache(self) :
        optstat = r.gStyle.GetOptStat()
        r.gStyle.SetOptStat(0)
        r.gROOT.ProcessLine(".L %s/cpp/tdrstyle.C"%whereami())
        r.setTDRStyle()
        r.tdrStyle.SetPadRightMargin(0.2)
        #r.gStyle.SetPalette(56) # works in ROOT 5.34 but not 5.32
        utils.invertedDarkBodyRadiatorPalette() # implemented manually
        self.setup()
        fileName = '/'.join(self.outputFileName.split('/')[:-1]+[self.name])
        sigmas = self.fillsigmas( r.TH2D("sigmas","Contours of Integer Sigma, Gaussian Approximation;%s;%s"%self.labelsXY, *(self.binningX+self.binningY)) )

        xyz = self.hzoom(self.xy)
        xyz.SetTitle(';%s;%s'%self.labelsXY)
        sigmasz = self.fillsigmas(xyz.Clone("sigmasz"))

        sigmasz.SetContour(6, np.array([0.1]+range(1,6),'d'))
        sigmas.SetContour(6, np.array([0.1]+range(1,6),'d'))
        c = r.TCanvas()
        c.SetTopMargin(0.055)
        c.Print(fileName+'.pdf[')
        sigmas.Draw("cont3")
        c.Print(fileName+'.pdf')
        if self.xy :
            self.xy.GetZaxis().SetTitle("Probability / bin")
            self.xy.SetContour(200)
            self.xy.UseCurrentStyle()
            self.xy.Draw('colzsame')
            sigmas.Draw('cont3same')
            c.Print(fileName+'.pdf')

            xyz.GetZaxis().SetTitle("Probability / bin")
            xyz.SetContour(200)
            xyz.UseCurrentStyle()
            xyz.GetXaxis().SetNdivisions(4,4,0,False)
            xyz.Draw('colz')
            sigmasz.Draw('cont3same')

            stamp = r.TText()
            ssize = stamp.GetTextSize()
            stamp.SetTextFont(62)
            stamp.SetTextSize(1.1*ssize)
            stamp.DrawTextNDC(0.20 ,0.88,"CMS")
            stamp.SetTextFont(52)
            stamp.SetTextSize(0.8 * ssize)
            stamp.DrawTextNDC(0.20, 0.83, "Simulation")
            stamp.SetTextFont(42)
            stamp.SetTextSize(ssize)
            stamp.DrawTextNDC(0.65, 0.96, "(8 TeV)")
            stamp.SetTextSize(0.7*ssize)
            stamp.DrawTextNDC(0.5505, 0.805, "MSD = 5")
            stamp.DrawTextNDC(0.61, 0.74, "4")
            stamp.DrawTextNDC(0.56, 0.68, "3")
            stamp.DrawTextNDC(0.5105, 0.617, "2")
            stamp.DrawTextNDC(0.47, 0.557, "1")
            

            c.Print(fileName+'.pdf')
        if hasattr(self,'xySup') :
            self.xySup.GetZaxis().SetTitle("Probability / bin")
            self.xySup.SetContour(200)
            self.xySup.UseCurrentStyle()
            self.xySup.Draw('colz')
            sigmas.Draw('cont3same')
            c.Print(fileName+'.pdf')
        c.Print(fileName+'.pdf]')
        print 'Wrote : %s.pdf'%fileName
        r.gStyle.SetOptStat(optstat)
######################################

class CombinationsLR(secondary) :
    def __init__(self, var, varMax, trueKey, samples, tag, label="") :
        if not label: label = var
        for item in ['samples','tag','var','varMax','trueKey','label'] : setattr(self,item,eval(item))
        self.fixes = (var,'')

    def update(self,_) :
        var = self.source[self.var]
        self.value = dict( (i,
                            self.LR.Interpolate(v) if self.LR else 1)
                           for i,v in self.source[self.var].items())

    def uponAcceptance(self,ev) :
        trueKey = self.source[self.trueKey]
        for key,val in self.source[self.var].items() :
            self.book.fill(min(val,self.varMax*(1-1e-6)),'%scorrect'%('' if key==trueKey else 'in'), 100,0,self.varMax, title = ';%s'%self.label)

    def setup(self,*_) :
        hists = self.fromCache(['merged'],['correct','incorrect'], tag = self.tag)['merged']
        if None in hists.values() :
            print self.name, ": Histograms not found."
            self.LR = None
            return
        for h in hists.values() : h.Scale(1./h.Integral(0,1+h.GetNbinsX()))
        self.LR = hists['correct'].Clone('LR')
        self.LR.Divide(hists['incorrect'])
        return hists
    def onlySamples(self) : return ['merged']
    def baseSamples(self) : return self.samples
    def organize(self,org) :
        if org.tag == self.tag :
            org.mergeSamples(targetSpec = {"name":'merged'}, sources = self.samples )
    def reportCache(self) :
        r.gROOT.ProcessLine(".L %s/cpp/tdrstyle.C"%whereami())
        r.setTDRStyle()
        r.gStyle.SetPalette(1)
        hists = self.setup()
        if not hists :
            print '%s.setup() failed'%self.name
            return
        fileName = '/'.join(self.outputFileName.split('/')[:-1]+[self.name]) + '.pdf'
        c = r.TCanvas()
        c.SetTopMargin(0.06)
        c.Print(fileName +'[')
        for h in hists.values() + [self.LR]:
            h.UseCurrentStyle()
            h.SetTitle(";%s;Probability / %.2f"%(self.label, self.varMax / 100.0))
            h.SetLineWidth(2)
        leg = r.TLegend(0.5,0.5,0.9,0.70)
        leg.SetBorderSize(0)
        leg.SetFillColor(r.kWhite)
        leg.SetTextFont(42)
        hists['correct'].SetLineColor(r.kRed)
        hists['correct'].SetLineWidth(3)
        hists['correct'].Draw('hist')
        hists['incorrect'].SetLineWidth(1)
        hists['incorrect'].SetLineStyle(7)
        hists['incorrect'].Draw('hist same')
        leg.AddEntry(hists['correct'], 'Correct', 'l')
        leg.AddEntry(hists['incorrect'], 'Incorrect', 'l')
        leg.Draw()

        stamp = r.TText()
        ssize = stamp.GetTextSize()
        def dostamp():
            stamp.SetTextFont(62)
            stamp.SetTextSize(1.1*ssize)
            stamp.DrawTextNDC(0.83 ,0.85,"CMS")
            stamp.SetTextFont(52)
            stamp.SetTextSize(0.8 * ssize)
            stamp.DrawTextNDC(0.77, 0.8, "Simulation")
            stamp.SetTextFont(42)
            stamp.SetTextSize(ssize)
            stamp.DrawTextNDC(0.83, 0.96, "(8 TeV)")

        dostamp()
        c.Print(fileName)
        self.LR.SetTitle(";%s;Likelihood ratio, correct/incorrect"%self.label)
        self.LR.SetMinimum(0)
        self.LR.Draw('hist')
        dostamp()

        c.Print(fileName)
        c.Print(fileName +']')
        print 'Wrote : %s'%fileName
######################################

class QueuedBin(wrappedChain.calculable) :
    def __init__(self, N, vars, limits, prefix="") :
        self.moreName = "%d; %s; %s"%((N,)+vars)
        self.fixes = (prefix,str(N))
        self.vars = vars
        r.gStyle.SetOptStat(0)
        pad = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(6))
        self.mapping = r.TH2D(self.name+pad,"", N, -limits[0], limits[0], N, -limits[1], limits[1])

        N2 = N*N
        binsValues = [((1.+2*i-N2)/N2,bins) for i,bins in enumerate([(sB-j,j) if sB%2 else (j,sB-j) for sB in range(N) for j in range(sB+1)])]
        for val,(binx,biny) in binsValues :
            if val>0 : continue
            self.mapping.SetBinContent(1+binx,1+biny,val)
            self.mapping.SetBinContent(N-binx,N-biny, -val)

    def update(self,_) :
        self.value = self.mapping.GetBinContent( self.mapping.FindFixBin( self.source[self.vars[0]],
                                                                          self.source[self.vars[1]]) )
