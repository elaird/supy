from bisect import bisect
#####################################
class analysisStep(object) :
    """Base class for analysis steps.

    Methods before __call__ can be reimplemented.
    """

    integerWidth,docWidth,moreWidth = 10,40,50
    moreName = moreName2 = ""
    disabled = quietMode = False
    
    def setup(self, inputChain, fileDirectory) : return
    def mergeFunc(self, products) : return
    def endFunc(self, chains) : return
    def varsToPickle(self) : return []
    def outputSuffix(self) : return "_%s.txt"%self.name

    def __call__(self,eventVars) :
        if self.disabled : return True
        if not self.isSelector : return self.uponAcceptance(eventVars) or True
        passed = bool(self.select(self.tracer(eventVars) if self.tracer else eventVars))
        self.increment(passed)
        return passed
    def increment(self, passed, w = None) : self.book.fill(passed, "counts", 2, 0, 2, w = w)

    @property
    def name(self) : return self.__class__.__name__
    @property
    def outputFileName(self) : return "%s%s"%(self.__outputFileStem, self.outputSuffix())
    @property
    def isSelector(self) : return hasattr(self,"select")
    @property
    def nFail(self) :  return self.nFromCountsHisto(1)
    @property
    def nPass(self) :  return self.nFromCountsHisto(2)

    def nFromCountsHisto(self, bin) :
        if "counts" not in self.book : return 0.0
        return self.book["counts"].GetBinContent(bin)
    
    def setOutputFileStem(self, stem) : self.__outputFileStem = stem
    def requiresNoSetBranchAddress(self) : return False
    def disable(self) : self.disabled = True
    def makeQuiet(self) : self.quietMode = True
        
    def name1(self) : return self.name.ljust(self.docWidth)+self.moreName.ljust(self.moreWidth)
    def name2(self) : return "" if self.moreName2=="" else "\n"+"".ljust(self.docWidth)+self.moreName2.ljust(self.moreWidth)
    def printStatistics(self) :
        passString="-" if self.disabled else str(int(self.nPass))
        failString="-" if self.disabled else str(int(self.nFail))

        statString = "" if not hasattr(self,"select") else \
                     "  %s %s" % ( passString.rjust(self.integerWidth), ("("+failString+")").rjust(self.integerWidth+2) )
        print "%s%s%s" % (self.name1(),self.name2(),statString)
#####################################
