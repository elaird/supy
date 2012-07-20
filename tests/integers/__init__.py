def whereami() : return max('/'.join(__file__.split('/')[:-1]), '.')

import sys
sys.path.insert(0,whereami()) # hack to force the local supy configuration
import supy,configuration,unittest
sys.path = sys.path[1:]

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


class testIntegers(unittest.TestCase) :

    def setUp(self) :
        a = integers(supy.options.default("--loop 1 --quiet".split()))
        a.loop()
        a.mergeAllOutput()
        self.orgs = [a.organizer(rc) for rc in a.readyConfs]

    def runTest(self) :
        self.assertEqual( 2, len(self.orgs) )
        self.assertEqual( 3, min(len(org.steps) for org in self.orgs) )
        self.assertEqual( 4, max(len(org.steps) for org in self.orgs) )

        h1,h2 = tuple([org.steps[next(org.indicesOfStepsWithKey("njets"))]["njets"][0]
                       for org in self.orgs])
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
