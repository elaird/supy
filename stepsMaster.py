from analysisStep import analysisStep
import utils,os
#####################################
class master(analysisStep) :
    def __init__(self, finalOutputPlotFileName, lumi, lumiWarn) :
        self.moreName = ""
        self.filterPtHat = False
        for item in ["finalOutputPlotFileName", "lumi", "lumiWarn"] :
            setattr(self, item, eval(item))
        
    def activatePtHatFilter(self, maxPtHat) :
        self.filterPtHat = True
        self.maxPtHat = maxPtHat
        self.moreName += "(pthat<%.1f)"%self.maxPtHat
    
    def select (self,eventVars) :
        return (not self.filterPtHat) or eventVars["genpthat"]<self.maxPtHat

    def endFunc(self, otherChainDict) :
        self.book().fill(0.0, "nJobsHisto", 1, -0.5, 0.5, title = ";dummy axis;N_{jobs}")        
        if self.xs   : self.book().fill(0.0, "xsHisto",   1, -0.5, 0.5, title = ";dummy axis;#sigma (pb)", w = self.xs)
        if self.lumi : self.book().fill(0.0, "lumiHisto", 1, -0.5, 0.5, title = "%s;dummy axis;integrated luminosity (pb^{-1})"%\
                                        ("" if not self.lumiWarn else "WARNING: lumi value is probably wrong!"), w = self.lumi)

    def notify(self, outputPlotFileName, xs) :
        for item in ["outputPlotFileName", "xs"] :
            setattr(self, item, eval(item))
        
    def varsToPickle(self) :
        return ["outputPlotFileName"]

    def mergeFunc(self, listOfProducts, someLooper) :
        def printComment(lines) :
            for line in lines.split("\n") :
                if 'Source file' in line or \
                   'Target path' in line or \
                   'Found subdirectory' in line : continue
                print line.replace("Target","The output")+" has been written."
                break

        def cleanUp(stderr, files) :
            assert not stderr, "hadd had a problem."
            for fileName in files :
                os.remove(fileName)

        files = [p["outputPlotFileName"] for p in listOfProducts]
        hAdd = utils.getCommandOutput("hadd -f %s %s"%(self.finalOutputPlotFileName, " ".join(files)))
        
        printComment(hAdd["stdout"])
        cleanUp(hAdd["stderr"], files)
