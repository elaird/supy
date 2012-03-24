import os, ROOT as r
from supy import utils,analysisStep

class displayer(analysisStep) :

    def reset(self) :
        self.canvas.Clear()
    
    def display(self, eventVars) :
        """Implement drawing etc. in self.display.
        It may be necessary to return ROOT objects to prevent them from getting garbage-collected.
        """
        return locals()

    def uponAcceptance(self, eventVars) :
        self.reset()
        stuff = self.display(eventVars)
        self.writeCanvas()

    def writeCanvas(self) :
        someDir = r.gDirectory
        self.outputFile.cd()
        self.canvas.Write("canvas_%d"%self.canvasIndex)
        self.canvasIndex+=1
        someDir.cd()

    def setup(self, chain, fileDir) :
        someDir = r.gDirectory
        self.outputFile = r.TFile(self.outputFileName, "RECREATE")
        someDir.cd()

        self.canvas = utils.canvas("canvas")
        self.canvas.SetFixedAspectRatio()
        self.canvasIndex = 0

    def endFunc(self, chains) :
        self.reset()
        self.outputFile.Write()
        self.outputFile.Close()
        del self.canvas

    def outputSuffix(self) :
        return "_displays.root"

    def mergeFunc(self, products) :
        def pdfFromRoot(listOfInFileNames, outFileName) :
            if not len(listOfInFileNames) : return
            options = "pdf"
            dummyCanvas = utils.canvas("display")
            dummyCanvas.Print(outFileName+"[", options)
            for inFileName in listOfInFileNames :
                inFile = r.TFile(inFileName)
                keys = inFile.GetListOfKeys()
                for key in keys :
                    someObject = inFile.Get(key.GetName())
                    if someObject.ClassName()!="TCanvas" : print "Warning: found an object which is not a TCanvas in the display root file"
                    someObject.Print(outFileName, options)
                inFile.Close()
                os.remove(inFileName)                    
            dummyCanvas.Print(outFileName+"]", options)
            print "The display file \""+outFileName+"\" has been written."    
        
        pdfFromRoot(products["outputFileName"], self.outputFileName.replace(".root", ".pdf"))
        print utils.hyphens
