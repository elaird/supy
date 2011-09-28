import copy,array,os,collections
import ROOT as r
from analysisStep import analysisStep
import utils
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
        if value is None or (not self.oneD and not all(value)) : return #temporary bug

        self.book.fill( self.func(value), self.hName, self.N, self.low, self.up, title=self.title)
#####################################
class value(analysisStep) :
    def __init__(self, var,N,low,up, indices = "", index = None, xtitle = "") :
        for item in ["var","N","low","up","indices","index"] :
            setattr(self,item,eval(item))

        self.moreName = var + self.wrapName() + ("[i[%d]]:%s"%(index,indices) if index!=None else "")
        self.title = ";%s%s;%s"%(xtitle if xtitle else var + ("[%s[%d]]"%(indices,index) if indices and index!=None else ""),
                                 self.wrapName(),
                                 "%s / bin"%(indices if indices and index==None else "events"))

    def uponAcceptance(self,eventVars) :
        val = eventVars[self.var]
        if val is None : return

        if not self.indices: 
            self.book.fill(self.wrap(val), self.moreName, self.N, self.low, self.up, title=self.title)
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
class eta(value) :
    def wrapName(self) : return ".eta"
    def wrap(self,val) : return val.eta()
class mass(value) :
    def wrapName(self) : return ".mass"
    def wrap(self,val) : return val.M()
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
