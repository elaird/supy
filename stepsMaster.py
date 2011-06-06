from analysisStep import analysisStep
import utils,os
#####################################
class Master(analysisStep) :
    def __init__(self, xs, xsPostWeights, lumi, lumiWarn) :
        self.maxPtHat = None
        for item in ["xs", "xsPostWeights", "lumi", "lumiWarn"] :
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

    def endFunc(self, chains) :
        self.select({"weight":1.0})
        self.book.fill(0.0, "nJobsHisto", 1, -0.5, 0.5, title = ";dummy axis;N_{jobs}")        
        if self.xs   : self.book.fill(0.0, "xsHisto",   1, -0.5, 0.5, title = ";dummy axis;#sigma (pb)", w = self.xs)
        if self.xsPostWeights : self.book.fill(0.0, "xsPostWeightsHisto",   1, -0.5, 0.5, title = ";dummy axis;#sigma (pb)", w = self.xsPostWeights)
        if self.lumi : self.book.fill(0.0, "lumiHisto", 1, -0.5, 0.5, title = "%s;dummy axis;integrated luminosity (pb^{-1})"%\
                                      ("" if not self.lumiWarn else "WARNING: lumi value is probably wrong!"), w = self.lumi)

    @staticmethod
    def outputSuffix() : return "_plots.root"
    
    def mergeFunc(self, products) :
        def printComment(lines) :
            skip = ['Source file','Target path','Found subdirectory']
            line = filter( lambda line: not any(item in line for item in skip), lines.split('\n'))[0]
            print line.replace("Target","The output") + " has been written." 

        def cleanUp(stderr, files) :
            assert not stderr, "hadd had this stderr: %s"%stderr
            for fileName in files : os.remove(fileName)

        hAdd = utils.getCommandOutput("hadd -f %s %s"%(self.outputFileName, " ".join(products["outputFileName"])))
        
        printComment(hAdd["stdout"])
        cleanUp(hAdd["stderr"], products["outputFileName"])
