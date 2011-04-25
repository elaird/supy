from analysisStep import analysisStep
import utils,os
#####################################
class Master(analysisStep) :
    def __init__(self, xs, lumi, lumiWarn) :
        self.moreName = ""
        self.maxPtHat = None
        for item in ["xs", "lumi", "lumiWarn"] :
            setattr(self, item, eval(item))
        
    def activatePtHatFilter(self, maxPtHat) :
        self.maxPtHat = maxPtHat
        self.moreName += "(pthat<%.1f)"%self.maxPtHat

    def select (self, eventVars) :
        weight = eventVars["weight"]
        if self.maxPtHat and self.maxPtHat<eventVars["genpthat"] : weight = None
        for book in self.books: book.weight = weight
        if weight is None : self.books[0].weight = 1
        return weight is not None
    # 'None' weight counts toward the total cross section with weight = 1,
    # but is not processed.  This is useful for sub-sampling and pthat-filtering

    def endFunc(self, otherChainDict) :
        self.select({"weight":1.0})
        self.book.fill(0.0, "nJobsHisto", 1, -0.5, 0.5, title = ";dummy axis;N_{jobs}")        
        if self.xs   : self.book.fill(0.0, "xsHisto",   1, -0.5, 0.5, title = ";dummy axis;#sigma (pb)", w = self.xs)
        if self.lumi : self.book.fill(0.0, "lumiHisto", 1, -0.5, 0.5, title = "%s;dummy axis;integrated luminosity (pb^{-1})"%\
                                        ("" if not self.lumiWarn else "WARNING: lumi value is probably wrong!"), w = self.lumi)

    @staticmethod
    def outputSuffix() :
        return "_plots.root"
    
    def mergeFunc(self, products) :
        def printComment(lines) :
            for line in lines.split("\n") :
                if 'Source file' in line or \
                   'Target path' in line or \
                   'Found subdirectory' in line : continue
                print line.replace("Target","The output")+" has been written."
                break

        def cleanUp(stderr, files) :
            assert not stderr, "hadd had this stderr: %s"%stderr
            for fileName in files :
                os.remove(fileName)

        hAdd = utils.getCommandOutput("hadd -f %s %s"%(self.outputFileName(), " ".join(products["outputFileName"])))
        
        printComment(hAdd["stdout"])
        cleanUp(hAdd["stderr"], products["outputFileName"])
