import unittest
import supy.utils.algos as algos

class testUnionProbability(unittest.TestCase) :
    def test(self) :
        '''supy.utils.algos.unionProbability'''
        self.assertEqual( 1.0, algos.unionProbability([1.]) , msg = "1")
        self.assertEqual( 1.0, algos.unionProbability([1.0,0.0]) , msg = "2")
        self.assertEqual( 1.0, algos.unionProbability([1.0,0.5]) , msg = "3")
        self.assertEqual( 0.75, algos.unionProbability(2*[0.5]) , msg = "4" )
        self.assertEqual( 2*0.4 - 0.4**2, algos.unionProbability(2*[0.4]), msg = "5")
        self.assertEqual( 3*0.3 - 3*0.3**2 + 0.3**3, algos.unionProbability(3*[0.3]) , msg = "6")
        self.assertAlmostEqual( 0.6 - 0.02 -0.03 -0.06 + 0.1*0.2*0.3,
                                algos.unionProbability( [0.1,0.2,0.3] ) , places = 8, msg = "7" )

class testTopologicalSort(unittest.TestCase) :
    def test(self) :
        '''supy.utils.algos.topologicalSort'''
        self.assertEqual( [0,1,2], algos.topologicalSort([(0,1),(0,2),(1,2)]))
        self.assertEqual( [0,2,1], algos.topologicalSort([(0,1),(0,2),(2,1)]))
        self.assertEqual( [0,2,1], algos.topologicalSort([(0,1),(0,2),(2,1)]))

        self.assertRaises( AssertionError, algos.topologicalSort, [(0,2),(2,0)] )
        self.assertRaises( AssertionError, algos.topologicalSort, [(0,1),(1,2),(2,0)] )

class testDilution(unittest.TestCase) :
    def test(self) :
        '''supy.utils.algos.dilution'''
        self.assertTrue(hasattr(algos, "np"), msg = "System lacks numpy")
        self.assertEqual( 1.0, algos.dilution([1,0],[0,1]) )
        self.assertEqual( 1.0, algos.dilution([1,1,0],[0,0,1]) )
        self.assertEqual( 1.0, algos.dilution([1,0,0],[0,0,1]) )
        self.assertEqual( 0.0, algos.dilution([1],[1]) )
        self.assertEqual( 0.0, algos.dilution([1,1],[1,1]) )
        self.assertEqual( 0.5, algos.dilution([1,1,0],[0,1,1]))
        self.assertEqual( 0.5, algos.dilution([1,0,1],[0,1,1]))
        self.assertAlmostEqual( 1./3, algos.dilution([1,1],[0,1]), places = 9 )
        self.assertAlmostEqual( algos.dilution([1,0],[1,1]),
                                algos.dilution([1,1],[1,0]), places = 9 )

class testEdgesRebinned(unittest.TestCase) :
    def test(self) :
        '''supy.utils.algos.edgesRebinned'''
        import ROOT as r
        h = r.TH1D("h","h",10,0,20)
        for i in range(12):
            h.SetBinContent(i,i)
            h.SetBinError(i,0.01*i)

        for uncpow in range(6) :
            for pivot in range(4,9) :
                self.onetest( h, unc = 10.**(-uncpow), pivot = pivot )

    def onetest(self, h, unc, pivot) :
        xbins = algos.edgesRebinned( h, targetUncRel = unc, pivot = pivot )
        left = [pivot - xbin for xbin in xbins if xbin < pivot][::-1]
        right = [xbin - pivot for xbin in xbins if xbin > pivot]
        s = max(0, min(len(left),len(right)) - 1 )
        self.assertEqual(left[:s],right[:s])

        k = h.Rebin(2, "k", xbins )
        leftUnc = [ k.GetBinError(i)/k.GetBinContent(i) if k.GetBinContent(i) else 0 
                    for i in range(1,1+k.GetNbinsX()) if k.GetBinCenter(i) < pivot]

        rightUnc = [ k.GetBinError(i)/k.GetBinContent(i) if k.GetBinContent(i) else 0 
                     for i in range(1,1+k.GetNbinsX()) if k.GetBinCenter(i) > pivot]

        msg = '\n\t'.join(["",
                           "pivot: %f"%pivot,
                           "unc: %f"%unc,
                           "leftUnc: %s"%str(leftUnc),
                           "rightUnc: %s"%str(rightUnc),
                           ])

        if len(leftUnc)>1 : self.assertEqual([L<=unc for L in leftUnc], 
                                              [True]*len(leftUnc), msg = msg)
        if len(rightUnc)>1 : self.assertEqual([R<=unc for R in rightUnc], 
                                               [True]*len(rightUnc), msg = msg)

class testLongestPrefix(unittest.TestCase) :
    def test(self) :
        '''supy.utils.algos.longestPrefix'''
        self.assertEqual( "", algos.longestPrefix([""]) )
        self.assertEqual( "", algos.longestPrefix(["","supy","susycaf"]) )
        self.assertEqual( "su", algos.longestPrefix(["supy","susycaf"]) )
        self.assertEqual( "Joe", algos.longestPrefix(["Joeseph Stalk","Joesephine Winkler","Joe Biden"]))

class testcContract(unittest.TestCase) :
    def test(self) :
        '''supy.utils.algos.contract'''
        self.assertEqual("", algos.contract([""]))
        self.assertEqual("{,su{py,sycaf}}", algos.contract(["","supy","susycaf"]))
        self.assertEqual("su{py,sycaf}", algos.contract(["supy","susycaf"]))
        self.assertEqual( "Joe{seph{ Stalk,ine Winkler}, Biden}", algos.contract(["Joeseph Stalk","Joesephine Winkler","Joe Biden"]))

if __name__ == "__main__" :
    unittest.main()
