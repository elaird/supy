import supy

class integers(supy.analysis) :
    
    def mainTree(self) :
        return ("djtuple", "tree")

    def listOfSteps(self,config) :
        return [
            supy.steps.printer.progressPrinter(),
            supy.steps.histos.value('njets',18,-2,15),
            ]
    
    def listOfCalculables(self,config) :
        return supy.calculables.zeroArgs(supy.calculables)
    
    def listOfSampleDictionaries(self) :
        exampleDict = supy.samples.SampleHolder()
	exampleDict.add('integers','["integers.root"]',lumi=0.009)
        return [exampleDict]
    
    def listOfSamples(self,config) :
        return supy.samples.specify(names = "integers")

options = supy.tests.defaultOptions()
options.loop = 1
integers(options).loop()
