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


class test5_skimmer_options(unittest.TestCase):
    import skimOptions

    def writeTFile(self):
        import array
        import ROOT as r

        var = skimOptions.var()
        f = r.TFile(skimOptions.fileName(), "RECREATE")
        dirName, treeName = configuration.mainTree()
        pairs = [configuration.mainTree()] + configuration.otherTreesToKeepWhenSkimming()
        for i, (dirName, treeName) in enumerate(pairs):
            f.mkdir(dirName)
            f.cd(dirName)
            t = r.TTree(treeName, "title")
            a = array.array('i', [0])
            t.Branch(var, a, '%s/I' % var)
            for run in range(i, i + 100):
                a[0] = run
                t.Fill()
            f.Write()
        f.Close()

    def setUp(self):
        self.writeTFile()

        import supy
        opts = supy.options.default("--loop 1 --quiet".split())
        a = skimOptions.skimOptions(opts)
        a.loop()
        a.mergeAllOutput()
        self.orgs = [a.organizer(rc) for rc in a.readyConfs]

    def tearDown(self):
        import os
        os.remove(skimOptions.fileName())

    def checkOneTree(self, f, tag, dirName, treeName, checkN=True,
                     varNames=[], antiVarNames=[]):
        coords = "%s:%s/%s" % (f.GetName(), dirName, treeName)
        msg = "%s: %s" % (tag, coords)

        self.assertTrue(f.cd(dirName), msg=msg)
        tree = f.Get(coords)
        self.assertTrue(tree, msg=msg)

        if checkN:
            n = tree.GetEntries()
            if tag.endswith("all"):
                self.assertTrue(n, msg=msg)
            elif tag.endswith("zero"):
                self.assertEqual(n, 0, msg=msg)

        for var in varNames:
            self.assertTrue(tree.GetBranch(var), msg=msg)

        for var in antiVarNames:
            self.assertFalse(tree.GetBranch(var), msg=msg)

    def test(self):
        '''Run the skimmer with a variety of options; check resulting skims.'''

        import ROOT as r

        for org in self.orgs:
            fileName = org.samples[0]["outputFileName"].replace("_plots.root", "_1_0_skim.root")
            f = r.TFile(fileName)
            self.assertTrue(f, msg=fileName)
            if org.tag[0] == "m":
                self.checkOneTree(f, org.tag, *configuration.mainTree(), varNames=["run"])
            if org.tag[1] == "o":
                for (dirName, treeName) in configuration.otherTreesToKeepWhenSkimming():
                    self.checkOneTree(f, org.tag, dirName, treeName, checkN=False)
            if org.tag[2] == "e":
                varNames = [] if org.tag.endswith("zero") else ["run2"]
                antiVarNames = [] if org.tag[0] == "m" else ["run"]
                self.checkOneTree(f, org.tag, *configuration.mainTree(),
                                  varNames=varNames, antiVarNames=antiVarNames)
            f.Close()
