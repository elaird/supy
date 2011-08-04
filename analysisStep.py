import traceback,sys
#####################################
class analysisStep(object) :
    """Base class for analysis steps.

    Methods before __call__ can be reimplemented.
    """

    integerWidth,docWidth,moreWidth = 10,40,50
    moreName = moreName2 = ""
    disabled = quietMode = False
    __invert = False
    
    def setup(self, inputChain, fileDirectory) : return
    def mergeFunc(self, products) : return
    def endFunc(self, chains) : return
    def varsToPickle(self) : return []
    def outputSuffix(self) : return "_%s.txt"%self.name

    def __call__(self,eventVars) :
        try:
            if self.disabled : return True
            tev = self.tracer(eventVars) if self.tracer else eventVars
            if not self.isSelector : return self.uponAcceptance(tev) or True
            passed = bool(self.select(tev)) ^ self.__invert
            self.increment(passed)
            return passed
        except Exception as e:
            traceback.print_tb(sys.exc_info()[2], limit=20, file=sys.stdout)
            print e.__class__.__name__,":", e, "\nProblem with %s\n%s\n"%(type(self),self.moreName)
            sys.exit(0)

    @property
    def name(self) : return self.__class__.__name__
    @property
    def moreNames(self) : return next(iter(filter(None,[self.moreName+self.moreName2,self.name])))
    @property
    def outputFileName(self) : return "%s%s"%(self.__outputFileStem, self.outputSuffix())
    @property
    def inputFileName(self) : return "%s%s"%(self.__inputFileStem, self.outputSuffix())
    @property
    def isSelector(self) : return hasattr(self,"select")
    @property
    def nFail(self) : return self.book["counts"].GetBinContent(1) if "counts" in self.book else 0.0
    @property
    def nPass(self) : return self.book["counts"].GetBinContent(2) if "counts" in self.book else 0.0
    @property
    def invert(self) :
        self.__invert = True
        self.moreName += " [INVERTED]"
        return self

    def increment(self, passed, w = None) : self.book.fill(passed, "counts", 2, 0, 2, w = w)
    def setOutputFileStem(self, stem) : self.__outputFileStem = stem
    def setInputFileStem(self, stem) : self.__inputFileStem = stem
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
