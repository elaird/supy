from bisect import bisect
#####################################
class analysisStep(object) :
    """generic analysis step"""

    integerWidth=10
    docWidth=30
    moreWidth=40
    moreName=""
    moreName2=""

    ignoreInAccounting=False
    disabled=False
    quietMode=False
    splitMode=False
    needToConsiderPtHatThresholds=False
    
    def go(self,eventVars) :
        if self.disabled :
            return True
        
        if not self.isSelector :
            self.uponAcceptance(eventVars)
            return True

        passed = bool(self.select(eventVars))
        self.book(eventVars).fill(passed,"counts",2,0,2)
        return passed
    
    def name(self) :
        return self.__class__.__name__

    def name1(self) :
        return self.name().ljust(self.docWidth)+self.moreName.ljust(self.moreWidth)

    def name2(self) :
        return "" if self.moreName2=="" else "\n"+"".ljust(self.docWidth)+self.moreName2.ljust(self.moreWidth)

    def varsToPickle(self) :
        return []

    def disable(self) :
        self.disabled=True
        
    def ignore(self) :
        self.nPass = 0
        self.nFail = 0
        self.ignoreInAccounting = True

    def makeQuiet(self) :
        self.quietMode=True
        
    def setSplitMode(self) :
        self.splitMode=True
        
    def printStatistics(self) :
        passString="-" if self.disabled else str(self.nPass)
        failString="-" if self.disabled else str(self.nFail)

        statString = "" if not hasattr(self,"select") else \
                     "  %s %s" % ( passString.rjust(self.integerWidth), ("("+failString+")").rjust(self.integerWidth+2) )
        print "%s%s%s" % (self.name1(),self.name2(),statString)

    def book(self,eventVars) :
        if not self.needToConsiderPtHatThresholds :
            return self.books[None]
        else :
            if not eventVars["genGenInfoHandleValid"] :
                raise Exception("pt hat is needed but its handle is not valid")
            index=bisect(self.ptHatThresholds,eventVars["genpthat"])
            return self.books[index]
#####################################
