import supy,configuration,unittest
from supy import tests

class integers(supy.analysis) :
    def parameters(self) :
        return {"setBranchAddress": self.vary({"sba":True, "no-sba":False}), }
    
    def listOfSteps(self,config) :
        return [supy.steps.printer.progressPrinter(),
                supy.steps.histos.value('njets',18,-2,15),
                ] + ([supy.steps.other.noSetBranchAddress()] if not config["setBranchAddress"]
                     else [])
    
    def listOfCalculables(self,config) :
        return supy.calculables.zeroArgs(supy.calculables)
    
    def listOfSampleDictionaries(self) :
        exampleDict = supy.samples.SampleHolder()
	exampleDict.add('integers','["integers.root"]',lumi=0.009)
        return [exampleDict]
    
    def listOfSamples(self,config) :
        return supy.samples.specify(names = "integers")

class integersTestSequence(unittest.TestCase) :

    def setUp(self) :
        an = tests.run( analysis = integers, options = {"loop": 1} )
        self.orgs = [an.organizer(rc) for rc in an.readyConfs]

    def runTest(self) :
        self.assertEqual( 2, len(self.orgs) )
        self.assertEqual( 5, max(len(org.steps) for org in self.orgs) )
        self.assertEqual( 4, min(len(org.steps) for org in self.orgs) )

        h1,h2 = tuple([org.steps[2]["njets"][0] for org in self.orgs])
        self.assertEqual( self.specs(h1), self.specs(h2) )

        error = "MISMATCH in bin %d (x=%g): %g != %g"
        for i,(c1,c2) in enumerate( zip( self.contents(h1), self.contents(h2) ) ) :
            self.assertAlmostEqual( c1, c2, places = 7,
                                    msg = error%(i,h1.GetBinCenter(i),c1,c2) )

    @staticmethod
    def specs(h) : return ( h.ClassName(),
                            h.GetNbinsX(),
                            h.GetXaxis().GetXmin(),
                            h.GetXaxis().GetXmax())
    @staticmethod    
    def contents(h) : return [h.GetBinContent(i) for i in range(2+h.GetNbinsX())]

if __name__ == '__main__':
    unittest.main()
