import supy,configuration

def whereami() : return max('/'.join(__file__.split('/')[:-1]), '.')

class integers(supy.analysis) :
    def parameters(self) :
        return {"setBranchAddress": self.vary({"sba":[],
                                               "no-sba":[supy.steps.other.noSetBranchAddress()]
                                               }) }
    def listOfSteps(self,config) :
        return config["setBranchAddress"]+[supy.steps.histos.value('njets',18,-2,15)]

    def listOfCalculables(self,config) :
        return supy.calculables.zeroArgs(supy.calculables)

    def listOfSampleDictionaries(self) :
        exampleDict = supy.samples.SampleHolder()
	exampleDict.add('integers','["%s/integers.root"]'%whereami(),lumi=0.009)
        return [exampleDict]

    def listOfSamples(self,config) :
        return supy.samples.specify(names = "integers")
