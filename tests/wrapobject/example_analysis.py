import supy, ROOT as r

class example_analysis(supy.analysis) :
    
    def listOfSteps(self,config) :
        return [
            supy.steps.printer.progressPrinter(),
            supy.steps.histos.absEta('particle', 10, 0.0, 10.0),
            ]
    
    def listOfCalculables(self,config) :
        return ( supy.calculables.zeroArgs(supy.calculables) +
                 [supy.calculables.other.fixedValue('Two',2) ]
                 )
    
    def listOfSampleDictionaries(self) :
        exampleDict = supy.samples.SampleHolder()
        exampleDict.add("Example_Data", '["/tmp/supy-dev/supy/tests/wrappedchain/nonflat_typetree.root"]', lumi = 1.0e-5 ) #/pb
        return [exampleDict]
    
    def listOfSamples(self,config) :
        return (supy.samples.specify(names = "Example_Data", color = r.kBlack, markerStyle = 20))
    
    def conclude(self,pars) :
        #make a pdf file with plots from the histograms created above
        org = self.organizer(pars)
        org.scale()
        supy.plotter( org,
                      pdfFileName = self.pdfFileName(org.tag),
                      ).plotAll()
