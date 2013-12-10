import unittest


class test3Integers(unittest.TestCase) :

    def setUp(self) :
        import integers,supy
        a = integers.integers(supy.options.default("--loop 1 --quiet".split()))
        a.loop()
        a.mergeAllOutput()
        self.orgs = [a.organizer(rc) for rc in a.readyConfs]

    def test(self) :
        '''Check that setBranchAddress has no effect on analysis results.'''
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


class test4_skim_eff(unittest.TestCase):
    def writeTFile(self, min=None, max=None):
        import array
        import ROOT as r
        f = r.TFile(self.fileName(min, max), "RECREATE")
        dirName, treeName = configuration.mainTree()
        f.mkdir(dirName)
        f.cd(dirName)
        t = r.TTree(treeName, "title")
        a = array.array('i', [0])
        t.Branch(self.var(), a, '%s/I' % self.var())
        for run in range(min, max):
            a[0] = run
            t.Fill()
        f.Write()
        f.Close()

    def setUp(self):
        import skimEff
        for item in ["fileName", "var", "params"]:
            setattr(self, item, getattr(skimEff, item))

        for min, max in self.params():
            self.writeTFile(min, max)

        import supy
        a = skimEff.skimEff(supy.options.default("--loop 1 --quiet".split()))
        a.loop()
        a.mergeAllOutput()
        self.orgs = [a.organizer(rc) for rc in a.readyConfs]

    def tearDown(self):
        import os
        for min, max in self.params():
            os.remove(self.fileName(min, max))

    def test(self):
        '''Check that skim efficiency is correct for weighted events.'''
        self.assertEqual(len(self.orgs), 1)
        master1, valueFilter, master2 = self.orgs[0].steps

        values = [x[0] for x in valueFilter.yields]
        uncs   = [x[1] for x in valueFilter.yields]

        for i in range(1, len(values)):
            v1 = values[i-1]
            v2 = values[i]
            self.assertAlmostEqual(v1, v2, places=7, msg="values (%d):  %g != %g" % (i, v1, v2))

            v1 = uncs[i-1]
            v2 = uncs[i]
            self.assertAlmostEqual(v1, v2, places=7, msg="uncs (%d):  %g != %g" % (i, v1, v2))
