import math,operator,itertools, ROOT as r
from supy import wrappedChain,utils
from . import secondary

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
    def update(self,ignored) : self.value = self.source._wrappedChain__chain
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
#####################################


#####################################
class value(wrappedChain.calculable) :
    def __init__( self, var, indices = None, index = None, short = None) :
        self.fixes = ("%s."%var, "%d%s"%(index, short if indices!=None and short!=None else indices) if index else "")
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
#####################################



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
        return 0.5 if not hist else hist.GetBinContent(hist.FindFixBin(self.source[key]))

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
