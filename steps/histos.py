import copy,array,os,collections
import ROOT as r
from supy import analysisStep,utils
#####################################
class generic(analysisStep) :

    def __init__(self,var,N,low,up,title="", funcString = "lambda x:x" , suffix = "") :
        for item in ["var","N","low","up","title","funcString"] : setattr(self,item,eval(item))
        self.oneD = type(var) != tuple
        self.hName = (var if self.oneD else "_vs_".join(reversed(var)))+suffix
        self.moreName = "%s(%s)"% ("(%s)"%funcString if funcString!="lambda x:x" else "", str(self.hName))
        self.funcStringEvaluated = False

    def uponAcceptance(self,eventVars) :
        if not self.funcStringEvaluated :
            self.func = eval(self.funcString)
            self.funcStringEvaluated = True
            
        value = eventVars[self.var] if self.oneD else \
                tuple(map(eventVars.__getitem__,self.var))
        if value is None or ((not self.oneD) and any(v is None for v in value)) : return

        self.book.fill( self.func(value), self.hName, self.N, self.low, self.up, title=self.title)
#####################################
class value(analysisStep) :
    def __init__(self, var,N,low,up, indices = "", index = None, xtitle = "", w = None) :
        if type(var)!=tuple : var = var,
        for item in ["var","N","low","up","indices","index",'w'] :
            setattr(self,item,eval(item))

        iMore = ("[i[%d]]"%index if index!=None else "")
        self.moreName = '; '.join(v+wn+iMore for v,wn in zip(3*var,self.wrapName())) + (('; '+indices) if indices else '')
        iTitle = ("[%s[%d]]"%(indices,index) if indices and index!=None else "")
        xtitleDef = ';'.join([iTitle.join(vwn) for vwn in zip(3*var,self.wrapName())])
        self.title = ";%s;%s"%(xtitle if xtitle else xtitleDef,
                               "%s / bin"%(indices if indices and index==None else "events"))

    def uponAcceptance(self,eventVars) :
        val = tuple(eventVars[v] for v in self.var)
        if any(v is None for v in val) : return

        if not self.indices: 
            self.book.fill(self.wrap(val), self.moreName, self.N, self.low, self.up, title=self.title, w = (eventVars[self.w] if self.w else None))
            return

        indices = eventVars[self.indices]
        if self.index!=None :
            if self.index<len(indices) :
                self.book.fill(self.wrap(tuple(v[indices[self.index]] for v in val)), self.moreName, self.N, self.low, self.up, title=self.title)
            return
        for i in indices :
            self.book.fill(self.wrap(tuple(v[i] for v in val)), self.moreName, self.N, self.low, self.up, title=self.title)

    def wrapName(self) : return ("",)*len(self.var)
    def wrap(self,val) : return val
#####################################
class pt(value) :
    def wrapName(self) : return ".pt",
    def wrap(self,val) : return val[0].pt()
class pz(value) :
    def wrapName(self) : return ".pz",
    def wrap(self,val) : return val[0].pz()
class phi(value) :
    def wrapName(self) : return ".phi",
    def wrap(self,val) : return val[0].phi()
class eta(value) :
    def wrapName(self) : return ".eta",
    def wrap(self,val) : return val[0].eta()
class Rapidity(value) :
    def wrapName(self) : return ".Rapidity",
    def wrap(self,val) : return val[0].Rapidity()
class absEta(value) :
    def wrapName(self) : return ".absEta",
    def wrap(self,val) : return abs(val[0].eta())
class mass(value) :
    def wrapName(self) : return ".mass",
    def wrap(self,val) : return val[0].M()
class phiVsEta(value):
    def wrapName(self) : return ('.eta','.phi')
    def wrap(self, val) : return (val[0].eta(),val[0].phi())
#####################################
class multiplicity(analysisStep) :
    def __init__(self,var, max = 10) :
        self.var = var
        self.max = max
        self.moreName = "%sMultiplicity"%var
        self.title = ";%s multiplicity;events / bin"%var
    def uponAcceptance(self,eventVars) :
        self.book.fill(len(eventVars[self.var]), self.moreName, self.max, -0.5, self.max-0.5, title = self.title)
#####################################
class weighted(analysisStep) :
    def __init__(self, var, N,low,up, baseWeight = "", weights = [], pred = "one") :
        for item in ['var','N','low','up','baseWeight','weights','pred'] : setattr(self,item,eval(item))
        self.moreName = "%s (%d); bW:%s; w:%s"%(var,N,baseWeight,utils.contract(weights))

    def uponAcceptance(self,ev) :
        bW = ev[self.baseWeight] if self.baseWeight else 1
        var = ev[self.var]
        for iW,w in enumerate([1]+([] if not ev[self.pred] else [ev[w] for w in self.weights])) :
            if not w : continue
            self.book.fill( var, "%02d%s"%(iW,self.var), self.N, self.low, self.up, title = ";%s;events / bin"%self.var,
                            w = bW * w )
#####################################
class symmAnti(analysisStep) :
    def __init__(self, weightVar, var, N, low, up, other = None) :
        for item in ['weightVar','var','N','low','up'] : setattr(self,item,eval(item))
        self.moreName = "%s in (anti)symm parts of %s%s"%(var,weightVar,"; %s"%other[0] if other else "")
        self.other = other
    def uponAcceptance(self,ev) :
        var = ev[self.var]
        if self.other :
            self.book.fill( (var,ev[self.other[0]]), self.var + self.other[0], (self.N,self.other[1]), (self.low,self.other[2]), (self.up,self.other[3]), title = ";%s;%s;events / bin"%(self.var,self.other[0]))
        else:
            self.book.fill(var, self.var, self.N, self.low, self.up, title = ";%s;events / bin"%self.var)

        symmanti = ev[self.weightVar + "SymmAnti"]
        if not symmanti : return
        sumsymmanti = sum(symmanti)
        if self.other :
            self.book.fill( (var, ev[self.other[0]]), self.var+self.other[0]+'_symm', (self.N,self.other[1]), (self.low,self.other[2]), (self.up,self.other[3]), title = ";%s;%s;events / bin"%(self.var,self.other[0]), w = ev['weight'] *symmanti[0]/sumsymmanti )
        else:
            self.book.fill(var, self.var+'_symm', self.N, self.low, self.up, title = ";%s;events / bin"%self.var, w = ev['weight'] *symmanti[0]/sumsymmanti )
            self.book.fill(var, self.var+'_anti', self.N, self.low, self.up, title = ";%s;events / bin"%self.var, w = ev['weight'] *symmanti[1]/sumsymmanti )
            self.book.fill(var, self.var+'_flat', self.N, self.low, self.up, title = ";%s;events / bin"%self.var, w = ev['weight'] / sumsymmanti / (self.up-self.low) )
#####################################


## Deprecated
#####################################
class histogrammer(analysisStep) :

    def __init__(self,var,N,low,up,title="", funcString = "lambda x:x" , suffix = "") :
        for item in ["var","N","low","up","title","funcString"] : setattr(self,item,eval(item))
        self.oneD = type(var) != tuple
        self.hName = (var if self.oneD else "_vs_".join(reversed(var)))+suffix
        self.moreName = "%s(%s)"% ("(%s)"%funcString if funcString!="lambda x:x" else "", str(self.hName))
        self.funcStringEvaluated = False

    def uponAcceptance(self,eventVars) :
        if not self.funcStringEvaluated :
            self.func = eval(self.funcString)
            self.funcStringEvaluated = True

        value = eventVars[self.var] if self.oneD else \
                tuple(map(eventVars.__getitem__,self.var))
        if value is None or (not self.oneD and not all(value)) : return #temporary bug

        self.book.fill( self.func(value), self.hName, self.N, self.low, self.up, title=self.title)
#####################################
class iterHistogrammer(histogrammer) :

    def uponAcceptance(self,eventVars) :
        if not self.funcStringEvaluated :
            self.func = eval(self.funcString)
            self.funcStringEvaluated = True

        values = eventVars[self.var] if self.oneD else \
                 zip(*map(eventVars.__getitem__,self.var))

        for i in range(len(values)) :
            value = values[i]
            if value is None or (not self.oneD and None in value) : continue
            self.book.fill( self.func(value), self.hName, self.N, self.low, self.up, title=self.title)
