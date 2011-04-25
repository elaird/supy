from analysisStep import analysisStep
import utils,os
#####################################
class Master(analysisStep) :
    def __init__(self, xs, lumi, lumiWarn) :
        self.moreName = ""
        self.filterPtHat = False
        for item in ["xs", "lumi", "lumiWarn"] :
            setattr(self, item, eval(item))
        
    def activatePtHatFilter(self, maxPtHat, lostXs) :
        self.xs -= lostXs
        self.filterPtHat = True
        self.maxPtHat = maxPtHat
        self.moreName += "(pthat<%.1f)"%self.maxPtHat

    def setBookWeights(self, weight) :
        for book in self.books: book.weight = weight
        
    def select (self, eventVars) :
        self.setBookWeights(eventVars["weight"])
        return (not self.filterPtHat) or eventVars["genpthat"]<self.maxPtHat

    def endFunc(self, otherChainDict) :
        self.setBookWeights(1.0)
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
