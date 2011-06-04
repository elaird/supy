from bisect import bisect
#####################################
class analysisStep(object) :
    """generic analysis step"""

    integerWidth = 10
    docWidth = 30
    moreWidth = 40
    moreName = ""
    moreName2 = ""

    disabled = False
    quietMode = False
    
    def go(self,eventVars) :
        if self.disabled :
            return True
        
        if not self.isSelector :
            self.uponAcceptance(eventVars)
            return True

        passed = bool(self.select(self.tracer(eventVars) if self.tracer else eventVars))
        self.increment(passed)
        return passed
    def increment(self, passed, w = None) : self.book.fill(passed, "counts", 2, 0, 2, w = w)
    def setup(self, inputChain, fileDirectory) : return
    def endFunc(self, chains) : return
    def mergeFunc(self, products) : return
    def name(self) : return self.__class__.__name__
    def name1(self) : return self.name().ljust(self.docWidth)+self.moreName.ljust(self.moreWidth)
    def name2(self) : return "" if self.moreName2=="" else "\n"+"".ljust(self.docWidth)+self.moreName2.ljust(self.moreWidth)
    def varsToPickle(self) : return []

    def setOutputFileStem(self, stem) : self._outputFileStem = stem
    def outputSuffix(self) : return "_%s.txt"%self.name()

    @property
    def outputFileName(self) : return "%s%s"%(self._outputFileStem, self.outputSuffix())
    @property
    def isSelector(self) : return hasattr(self,"select")
    @property
    def nFail(self) :  return int(self.nFromCountsHisto(1))
    @property
    def nPass(self) :  return int(self.nFromCountsHisto(2))

    def nFromCountsHisto(self, bin) :
        if not self.book : return 0.0
        if "counts" not in self.book : return 0.0
        if not self.book["counts"] : return 0.0
        return self.book["counts"].GetBinContent(bin)
    
    def requiresNoSetBranchAddress(self) : return False
    def disable(self) : self.disabled = True
    def makeQuiet(self) : self.quietMode = True
        
    def printStatistics(self) :
        passString="-" if self.disabled else str(self.nPass)
        failString="-" if self.disabled else str(self.nFail)

        statString = "" if not hasattr(self,"select") else \
                     "  %s %s" % ( passString.rjust(self.integerWidth), ("("+failString+")").rjust(self.integerWidth+2) )
        print "%s%s%s" % (self.name1(),self.name2(),statString)
#####################################
