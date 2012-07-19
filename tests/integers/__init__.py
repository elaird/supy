import supy,configuration
from supy import tests

#hack
print "WARNING: hack in tests/integers/__init__.py"
configuration.hadd = lambda :"hadd"
configuration.nCoresDefault = lambda :1

def histoMatch(h1, h2, tolerance = 1.0e-6) :
    funcs = [lambda x:x.ClassName(),
             lambda x:x.GetNbinsX(),
             lambda x:x.GetXaxis().GetXmin(),
             lambda x:x.GetXaxis().GetXmax(),
             ]
    for f in funcs :
        assert f(h1)==f(h2)
    for iBinX in range(2+h1.GetNbinsX()) :
        x = h1.GetBinCenter(iBinX)
        c1 = h1.GetBinContent(iBinX)
        c2 = h2.GetBinContent(iBinX)
        assert abs(c1-c2)<tolerance,"MISMATCH in bin %d (x=%g): %g != %g"%(iBinX, x, c1, c2)

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
                ] + ([supy.steps.other.noSetBranchAddress()] if not config["setBranchAddress"] else [])
    
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
        fail = "\n\n".join([str(x) for x in orgs])
        assert len(orgs)==2,fail

        lst = [len(org.steps) for org in orgs]
        #master added at beginning and end
        assert max(lst)==5,fail
        assert min(lst)==4,fail

        histos = tuple([org.steps[2]["njets"][0] for org in orgs])
        histoMatch(*histos)

tests.run(analysis = integers, options = {"loop": 1})
