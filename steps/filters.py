import copy,array,os,collections
import ROOT as r
from supy import analysisStep,utils
#####################################
class label(analysisStep) :
    def __init__(self,title) : self.moreName = title
    def select(self,eventVars) : return True
#####################################
class assertNotYetCalculated(analysisStep) :
    def __init__(self,var) : self.var = var
    def uponAcceptance(self, eV) : assert not dict.__getitem__(eV, self.var).updated
#####################################
class multiplicity(analysisStep) :
    def __init__(self,var, min = 0, max = None ) :
        self.moreName = "%d <= %s"%(min,var) + (" <= %d" % max if max!=None else "")
        self.var = var
        self.min = min
        self.max = max if max!=None else 1e6
    def select(self,eventVars) :
        return self.min <= len(eventVars[self.var]) <= self.max
#####################################
class value(analysisStep) :
    def __init__(self, var, min = None, max = None, indices = "", index = None) :
        for item in ["var","min","max","indices","index"] : setattr(self,item,eval(item))
        self.moreName = ( ("%.2f<="%min if min is not None else "") + var +
                          ("[i[%s]]" % str(index) if index is not None else "") + self.wrapName() + 
                          ("<=%.1f"%max if max is not None else "") +
                          ("; %s"%indices if indices else ""))

    def select(self,eventVars) :
        val = eventVars[self.var] if self.index==None else \
              eventVars[self.var][self.index] if not self.indices else \
              eventVars[self.var][eventVars[self.indices][self.index]] if self.index<len(eventVars[self.indices]) else None
        if val is None : return False
        val = self.wrap(val)
        return self.min <= val and ((self.max is None) or val <= self.max)

    def wrapName(self) : return ""
    def wrap(self,val) : return val
#####################################
class pt(value) :
    def wrapName(self) : return ".pt"
    def wrap(self,val) : return val.pt()
class absPz(value) :
    def wrapName(self) : return ".absPz"
    def wrap(self,val) : return abs(val.pz())
class eta(value) :
    def wrapName(self) : return ".eta"
    def wrap(self,val) : return val.eta()
class absEta(value) :
    def wrapName(self) : return ".absEta"
    def wrap(self,val) : return abs(val.eta())
#####################################
class OR(analysisStep) :
    def __init__(self, listOfSelectorSteps = []) :
        self.steps = listOfSelectorSteps
        self.moreName = '|'.join(["%s:%s"%(step.name,step.moreName) for step in self.steps])
    def select(self,eventVars) :
        for step in self.steps :
            if step.select(eventVars) : return True
        return False
#####################################
class product(analysisStep) :
    def __init__(self, variables, min, max):
        for item in ["variables","min","max"] : setattr(self,item,eval(item))
        self.threshold = threshold
        self.variables = variables
        self.moreName = "%s>=%.3f %s" % ("*".join(variables),threshold,suffix)

    def select (self,eventVars) :
        product = 1
        for var in self.variables : product *= eventVars[var]
        return product >= self.threshold
#####################################
