import supy,configuration

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
        localDict = supy.samples.SampleHolder()
        filePath = "%s/%s/integers.root"%(supy.whereami(),configuration.localpath())
	localDict.add('integers','["%s"]'%filePath, lumi=0.009)
        return [localDict]

    def listOfSamples(self,config) :
        return supy.samples.specify(names = "integers")
