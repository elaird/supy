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
        for item in ["var","N","low","up","indices","index",'w'] :
            setattr(self,item,eval(item))

        self.moreName = var + self.wrapName() + ("[i[%d]]:%s"%(index,indices) if index!=None else "")
        self.title = ";%s%s;%s"%(xtitle if xtitle else var + ("[%s[%d]]"%(indices,index) if indices and index!=None else ""),
                                 self.wrapName(),
                                 "%s / bin"%(indices if indices and index==None else "events"))

    def uponAcceptance(self,eventVars) :
        val = eventVars[self.var]
        if val is None : return

        if not self.indices: 
            self.book.fill(self.wrap(val), self.moreName, self.N, self.low, self.up, title=self.title, w = (eventVars[self.w] if self.w else None))
            return

        indices = eventVars[self.indices]
        if self.index!=None :
            if self.index<len(indices) :
                self.book.fill(self.wrap(val[indices[self.index]]), self.moreName, self.N, self.low, self.up, title=self.title)
            return
        for i in indices :
            self.book.fill(self.wrap(val[i]), self.moreName, self.N, self.low, self.up, title=self.title)

    def wrapName(self) : return ""
    def wrap(self,val) : return val
#####################################
class pt(value) :
    def wrapName(self) : return ".pt"
    def wrap(self,val) : return val.pt()
class pz(value) :
    def wrapName(self) : return ".pz"
    def wrap(self,val) : return val.pz()
class phi(value) :
    def wrapName(self) : return ".phi"
    def wrap(self,val) : return val.phi()
class eta(value) :
    def wrapName(self) : return ".eta"
    def wrap(self,val) : return val.eta()
class absEta(value) :
    def wrapName(self) : return ".absEta"
    def wrap(self,val) : return abs(val.eta())
class mass(value) :
    def wrapName(self) : return ".mass"
    def wrap(self,val) : return val.M()
#####################################
class value2d(analysisStep) :
    def __init__(self, var=('',''),
                 indices='', index = None,
                 N=(100,100),lo=(0.0,0.0),hi=(1.0,1.0),title='',w=None) :
        for item in ['var','indices','index','N','lo','hi','title','w'] : setattr(self,item,eval(item))
        self.moreName = '_vs_'.join([var[1]+self.wrapNameY(), var[0]+self.wrapNameX()]) \
            + (":%s"%indices if indices and index==None else "") \
            + ("[i[%d]]:%s"%(index,indices) if index!=None else "")
        self.title = "%s;%s;%s" % (title if title else \
                                       ' vs '.join([self.wrapNameY(), self.wrapNameX()]) \
                                       + ("[%s]"%indices if indices and index==None else "") \
                                       + ("[%s[%d]]"%(indices,index) if indices and index!=None else ""),
                                   var[0] + self.wrapNameX(),
                                   var[1] + self.wrapNameY())

    def uponAcceptance(self,eventVars) :
        valX, valY = eventVars[self.var[0]], eventVars[self.var[1]]
        if valX is None or valY is None : return
        if not self.indices:
            self.book.fill((self.wrapX(valX), self.wrapY(valY)),
                           self.moreName,
                           self.N, self.lo, self.hi, title = self.title,
                           w = (eventVars[self.w] if self.w else None))
            return
        indices = eventVars[self.indices]
        if self.index!=None :
            if self.index<len(indices) :
                self.book.fill((self.wrapX(valX[indices[self.index]]), self.wrapY(valY[indices[self.index]])),
                               self.moreName,
                               self.N, self.lo, self.hi, title = self.title,
                               w = (eventVars[self.w] if self.w else None))
            return
        for i in indices :
            self.book.fill((self.wrapX(valX[i]), self.wrapY(valY[i])),
                           self.moreName,
                           self.N, self.lo, self.hi, title = self.title,
                           w = (eventVars[self.w] if self.w else None))
    def wrapNameX(self) : return ''
    def wrapNameY(self) : return ''
    def wrapX(self, val) : return val
    def wrapY(self, val) : return val
#####################################
class phiVsEta(value2d):
    def wrapNameX(self) : return '.eta'
    def wrapNameY(self) : return '.phi'
    def wrapX(self, val) : return val.eta()
    def wrapY(self, val) : return val.phi()
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
        self.book.fill(var, self.var, self.N, self.low, self.up, title = ";%s;events / bin"%self.var)
        if self.other :
            self.book.fill( (var,ev[self.other[0]]), self.var + self.other[0], (self.N,self.other[1]), (self.low,self.other[2]), (self.up,self.other[3]), title = ";%s;%s;events / bin"%(self.var,self.other[0]))
        symmanti = ev[self.weightVar + "SymmAnti"]
        if not symmanti : return
        sumsymmanti = sum(symmanti)
        self.book.fill(var, self.var+'_symm', self.N, self.low, self.up, title = ";%s;events / bin"%self.var, w = ev['weight'] *symmanti[0]/sumsymmanti )
        self.book.fill(var, self.var+'_anti', self.N, self.low, self.up, title = ";%s;events / bin"%self.var, w = ev['weight'] *symmanti[1]/sumsymmanti )
        self.book.fill(var, self.var+'_flat', self.N, self.low, self.up, title = ";%s;events / bin"%self.var, w = ev['weight'] / sumsymmanti / (self.up-self.low) )
        if self.other :
            self.book.fill( (var, ev[self.other[0]]), self.var+self.other[0]+'_symm', (self.N,self.other[1]), (self.low,self.other[2]), (self.up,self.other[3]), title = ";%s;%s;events / bin"%(self.var,self.other[0]), w = ev['weight'] *symmanti[0]/sumsymmanti )
            self.book.fill( (var, ev[self.other[0]]), self.var+self.other[0]+'_anti', (self.N,self.other[1]), (self.low,self.other[2]), (self.up,self.other[3]), title = ";%s;%s;events / bin"%(self.var,self.other[0]), w = ev['weight'] *symmanti[1]/sumsymmanti )
            self.book.fill( (var, ev[self.other[0]]), self.var+self.other[0]+'_flat', (self.N,self.other[1]), (self.low,self.other[2]), (self.up,self.other[3]), title = ";%s;%s;events / bin"%(self.var,self.other[0]), w = ev['weight'] / sumsymmanti / (self.up-self.low) )
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
