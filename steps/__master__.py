import supy,os,configuration
#####################################
class master(supy.analysisStep) :
    def __init__(self, xs, xsPostWeights, lumi, lumiWarn) :
        for item in ["xs", "xsPostWeights", "lumi", "lumiWarn"] : setattr(self, item, eval(item))

    @property
    def nProcessed(self):
        # See select() below, which results in either
        # a) incrementing wFail by 1; or
        # b) incrementing wPass by weight, and incrementing wFail by 1 - weight.
        # In either case, a unit of content is added to (wPass + wFail).
        return self.wPass + self.wFail

    @property
    def failString(self):
        # %g handles 'float epsilon less than nearest int' better than %d
        return "[-]" if self.disabled else "[n=%g]" % self.nProcessed

    def select (self, eventVars) :
        weight = eventVars["weight"]
        if weight is None : self.book.weight = 1
        else: self.increment(False, 1-weight)
        return weight is not None
    # 'None' weight counts toward the total cross section with weight = 1,
    # but is not processed further.  This is useful for sub-sampling and pthat-filtering

    def endFunc(self, chains) :
        self.book.fill(0.0, "nJobsHisto", 1, -0.5, 0.5, title = ";dummy axis;N_{jobs}", w = 1.0)
        if self.xs   : self.book.fill(0.0, "xsHisto",   1, -0.5, 0.5, title = ";dummy axis;#sigma (pb)", w = self.xs)
        if self.xsPostWeights : self.book.fill(0.0, "xsPostWeightsHisto",   1, -0.5, 0.5, title = ";dummy axis;#sigma (pb)", w = self.xsPostWeights)
        if self.lumi : self.book.fill(0.0, "lumiHisto", 1, -0.5, 0.5, title = "%s;dummy axis;integrated luminosity (pb^{-1})"%\
                                      ("" if not self.lumiWarn else "WARNING: lumi value is probably wrong!"), w = self.lumi)

    @staticmethod
    def outputSuffix() : return "_plots.root"
    
    def mergeFunc(self, products) :
        def printComment(lines) :
            if self.quietMode : return
            skip = ['Source file','Target path','Found subdirectory']
            line = next(L for L in lines.split('\n') if not any(item in L for item in skip))
            print line.replace("Target","The output") + " has been written."

        def cleanUp(stderr, files) :
            okList = configuration.haddErrorsToIgnore()
            assert (stderr in okList), "hadd had this stderr: '%s'"%stderr
            if stderr : print stderr
            for fileName in files : os.remove(fileName)

        if not all(os.path.exists(fileName) for fileName in products["outputFileName"]) : return
        hAdd = supy.utils.getCommandOutput("%s -f %s %s"%(configuration.hadd(),self.outputFileName, " ".join(products["outputFileName"])))

        printComment(hAdd["stdout"])
        cleanUp(hAdd["stderr"], products["outputFileName"])
