import time
from core.analysisStep import analysisStep
#####################################
class progressPrinter(analysisStep) :

    def __init__(self,suppressionFactor=2,suppressionOffset=300):
        self.nTotal=0
        self.num=1
        self.suppressionFactor=suppressionFactor
        self.suppressionOffset=suppressionOffset
        self.moreName = "factor=%d, offset=%d"%(self.suppressionFactor,self.suppressionOffset)

    def uponAcceptance (self,eventVars) :
        self.nTotal+=1
        if self.nTotal!=self.num : return
        self.num=self.suppressionFactor*self.num
        toPrint="event "+str(self.nTotal).rjust(self.integerWidth," ")
        toPrint=toPrint.ljust(self.docWidth+self.moreWidth+1)+time.ctime()
        if (self.num==self.suppressionFactor or self.num>self.suppressionOffset) and not self.quietMode :
            print toPrint
#####################################
class printstuff(analysisStep) :

    def __init__(self,stuff []) :
        self.stuff = stuff
        self.moreName = "print all in %s" % str(stuff)
        print '\t'.join(stuff)
        
    def uponAcceptance(self,ev) :
        print '\t'.join([str(ev[s]) for s in self.stuff])
#####################################
