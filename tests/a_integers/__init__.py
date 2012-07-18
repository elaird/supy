import supy

def dump(orgs = []) :
    out = "\n"
    for org in orgs :
        out += " ".join([org.tag, ":", str(org), "\n"])
        for s in org.steps :
            out += " ".join([s.name,s.title,"\n"])
        out += "\n"
    return out

class integers(supy.analysis) :
    def parameters(self) :
        return {"setBranchAddress": self.vary({"sba":True, "no-sba":False}), }
    
    def mainTree(self) :
        return ("djtuple", "tree")

    def useCachedFileLists(self) :
        return False

    def listOfSteps(self,config) :
        return [supy.steps.printer.progressPrinter(),
                supy.steps.histos.value('njets',18,-2,15),
                ] + [supy.steps.other.noSetBranchAddress()] if not config["setBranchAddress"] else []
    
    def listOfCalculables(self,config) :
        return supy.calculables.zeroArgs(supy.calculables)
    
    def listOfSampleDictionaries(self) :
        exampleDict = supy.samples.SampleHolder()
	exampleDict.add('integers','["integers.root"]',lumi=0.009)
        return [exampleDict]
    
    def listOfSamples(self,config) :
        return supy.samples.specify(names = "integers")

    def concludeAll(self) :
        orgs = map(lambda x:self.organizer(x), self.readyConfs)
        fail = dump(orgs)
        assert len(orgs)==2,fail

        lst = [len(org.steps) for org in orgs]
        assert max(lst)==4,fail
        assert min(lst)==3,fail

supy.tests.run(analysis = integers, options = {"loop": 1})
