def whereami() : return max('/'.join(__file__.split('/')[:-1]), '.')

import sys
sys.path.insert(0,whereami()) # hack to force the local supy configuration
import supy,configuration,unittest,integers
sys.path = sys.path[1:]

class test1LocalConfiguration(unittest.TestCase) :
    def test(self) :
        '''Check that we load the local configuration.py'''
        self.assertEqual( ("djtuple","tree"), configuration.mainTree())
        self.assertTrue( hasattr(supy.__analysis__.configuration, "localpath"))
        self.assertEqual( "tests/integers", supy.__analysis__.configuration.localpath() )

class test2Integers(unittest.TestCase) :

    def setUp(self) :
        a = integers.integers(supy.options.default("--loop 1 --quiet".split()))
        a.loop()
        a.mergeAllOutput()
        self.orgs = [a.organizer(rc) for rc in a.readyConfs]

    def test(self) :
        '''Check that setBranchAddress has no effect on results.'''
        nSteps = [len(org.steps) for org in self.orgs]
        self.assertEqual( 2, len(nSteps) )
        self.assertEqual( 3, min(nSteps) )
        self.assertEqual( 4, max(nSteps) )

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
