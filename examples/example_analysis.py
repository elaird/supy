import supy, ROOT as r

class example_analysis(supy.analysis) :
    
    def listOfSteps(self,config) :
        return [
            supy.steps.printer.progressPrinter(),
            supy.steps.histos.value('run',20,0,1e4),
            supy.steps.histos.value('bx',20,0,1e4),
            supy.steps.histos.value('Two',10,0,10),
            ]
    
    def listOfCalculables(self,config) :
        return ( supy.calculables.zeroArgs(supy.calculables) +
                 [supy.calculables.other.fixedValue('Two',2) ]
                 )
    
    def listOfSampleDictionaries(self) :
        exampleDict = supy.samples.SampleHolder()
        exampleDict.add("Example_Skimmed_900_GeV_Data", '["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_Data.root"]', lumi = 1.0e-5 ) #/pb
        exampleDict.add("Example_Skimmed_900_GeV_MC", '["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_MC.root"]',       xs = 1.0e8 ) #pb
        return [exampleDict]
    
    def listOfSamples(self,config) :
        return (supy.samples.specify(names = "Example_Skimmed_900_GeV_Data", color = r.kBlack, markerStyle = 20) +
                supy.samples.specify(names = "Example_Skimmed_900_GeV_MC", color = r.kRed, effectiveLumi = 0.5) )
    
    def conclude(self,pars) :
        #make a pdf file with plots from the histograms created above
        org = self.organizer(pars)
        org.scale()
        supy.plotter( org,
                      psFileName = self.psFileName(org.tag),
                      samplesForRatios = ("Example_Skimmed_900_GeV_Data","Example_Skimmed_900_GeV_MC"),
                      sampleLabelsForRatios = ("data","sim"),
                      ).plotAll()
