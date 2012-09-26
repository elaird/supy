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
class Tridiscriminant(secondary) :
    def __init__(self, fixes = ("",""),
                 zero = {"pre":"", "samples":[], "tag":""},
                 pi23 = {"pre":"", "samples":[], "tag":""},
                 pi43 = {"pre":"", "samples":[], "tag":""},
                 dists = {}, # key = calc or leaf name : val = (bins,min,max)
                 bins = 60,
                 correlations = False
                 ) :
        for item in ['fixes','zero','pi23','pi43','dists','correlations','bins'] : setattr(self,item,eval(item))
        self.moreName = "zero:"+zero['pre'] +"; pi23:"+pi23['pre']+"; pi43:"+pi43['pre']
        self.populations = [self.zero,self.pi23,self.pi43]
        self.sqrt3 = math.sqrt(3)

    def onlySamples(self) : return [item['pre'] for item in self.populations]
    def baseSamples(self) :
        samples = [item['samples'] for item in self.populations]
        return set(sum(samples,[])) if all(samples) else []

    def likelihoods(self) :
        likes = [ self.fromCache([item['pre']], self.dists.keys()+[self.name], tag = item['tag'])[item['pre']]
                  for item in self.populations]
        for h in filter(None,sum([item.values() for item in likes],[])) :
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
        L,R,X = [ reduce( operator.mul,
                          [self.likelihood(item[key],self.source[key]) for key in self.dists if item[key]],
                          1 )
                  for item in self.likes]
        self.value = math.atan2( (R-X)*self.sqrt3,
                                 2*L - (R+X) ) / math.pi # [-1,1] with zero peaking at zero, +/- pi23 peaking at +/- 0.666

    def organize(self,org) :
        [ org.mergeSamples( targetSpec = {'name':item['pre']}, sources = item['samples'], scaleFactors = item['sf'] if 'sf' in item else [], force = True) if item['samples'] else
          org.mergeSamples( targetSpec = {'name':item['pre']}, allWithPrefix = item['pre'])
          for item in self.populations if org.tag == item['tag']]
        for sample in list(org.samples) :
            if (sample['name'],org.tag) not in [(item['pre'],item['tag']) for item in self.populations] :
                org.drop(sample['name'])

    def reportCache(self) :
        likes = self.likelihoods()
        fileName = '/'.join(self.outputFileName.split('/')[:-1]+[self.name])
        optstat = r.gStyle.GetOptStat()
        r.gStyle.SetOptStat(0)
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
                l = r.TLegend(0.75,0.85,0.98,0.98)
                l.SetHeader("Dilutions :  %.3f  %.3f  %.3f"%tuple(dilutions))
                for i,(item,color,pop) in enumerate(zip(likes,[r.kBlack,r.kRed,r.kBlue],self.populations)) :
                    item[key].SetLineColor(color)
                    item[key].SetMaximum(h)
                    item[key].SetMinimum(0)
                    item[key].GetYaxis().SetTitle("pdf")
                    item[key].Draw("hist" + ('same' if i else ''))
                    l.AddEntry(item[key], pop['pre'],'l')
                l.Draw()
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
        self.value = (symm,anti)

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
