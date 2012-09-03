import unittest
from supy.tests import skip,skipIf
try: import numpy as np
except: np=None

class testUnionProbability(unittest.TestCase) :
    def test(self) :
        '''supy.utils.algos.unionProbability'''
        from supy.utils.algos import unionProbability
        self.assertEqual( 1.0, unionProbability([1.]) , msg = "1")
        self.assertEqual( 1.0, unionProbability([1.0,0.0]) , msg = "2")
        self.assertEqual( 1.0, unionProbability([1.0,0.5]) , msg = "3")
        self.assertEqual( 0.75, unionProbability(2*[0.5]) , msg = "4" )
        self.assertEqual( 2*0.4 - 0.4**2, unionProbability(2*[0.4]), msg = "5")
        self.assertEqual( 3*0.3 - 3*0.3**2 + 0.3**3, unionProbability(3*[0.3]) , msg = "6")
        self.assertAlmostEqual( 0.6 - 0.02 -0.03 -0.06 + 0.1*0.2*0.3,
                                unionProbability( [0.1,0.2,0.3] ) , places = 8, msg = "7" )

class testTopologicalSort(unittest.TestCase) :
    def test(self) :
        '''supy.utils.algos.topologicalSort'''
        from supy.utils.algos import topologicalSort
        self.assertEqual( [0,1,2], topologicalSort([(0,1),(0,2),(1,2)]))
        self.assertEqual( [0,2,1], topologicalSort([(0,1),(0,2),(2,1)]))
        self.assertEqual( [0,2,1], topologicalSort([(0,1),(0,2),(2,1)]))

        self.assertRaises( AssertionError, topologicalSort, [(0,2),(2,0)] )
        self.assertRaises( AssertionError, topologicalSort, [(0,1),(1,2),(2,0)] )

class testDilution(unittest.TestCase) :
    @skipIf(np==None,"System lacks numpy")
    def test(self) :
        '''supy.utils.algos.dilution'''
        from supy.utils.algos import dilution
        self.assertEqual( 1.0, dilution([1,0],[0,1]) )
        self.assertEqual( 1.0, dilution([1,1,0],[0,0,1]) )
        self.assertEqual( 1.0, dilution([1,0,0],[0,0,1]) )
        self.assertEqual( 0.0, dilution([1],[1]) )
        self.assertEqual( 0.0, dilution([1,1],[1,1]) )
        self.assertEqual( 0.5, dilution([1,1,0],[0,1,1]))
        self.assertEqual( 0.5, dilution([1,0,1],[0,1,1]))
        self.assertAlmostEqual( 1./3, dilution([1,1],[0,1]), places = 9 )
        self.assertAlmostEqual( dilution([1,0],[1,1]),
                                dilution([1,1],[1,0]), places = 9 )

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
        from supy.utils.algos import edgesRebinned
        xbins = edgesRebinned( h, targetUncRel = unc, pivot = pivot )
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
        from supy.utils.algos import longestPrefix
        self.assertEqual( "", longestPrefix([""]) )
        self.assertEqual( "", longestPrefix(["","supy","susycaf"]) )
        self.assertEqual( "su", longestPrefix(["supy","susycaf"]) )
        self.assertEqual( "Joe", longestPrefix(["Joeseph Stalk","Joesephine Winkler","Joe Biden"]))

class testContract(unittest.TestCase) :
    def test(self) :
        '''supy.utils.algos.contract'''
        from supy.utils.algos import contract
        self.assertEqual("", contract([""]))
        self.assertEqual("{,su{py,sycaf}}", contract(["","supy","susycaf"]))
        self.assertEqual("su{py,sycaf}", contract(["supy","susycaf"]))
        self.assertEqual( "Joe{seph{ Stalk,ine Winkler}, Biden}", contract(["Joeseph Stalk","Joesephine Winkler","Joe Biden"]))

class testRootDot(unittest.TestCase) :
    def test(self) :
        '''supy.utils.root.Dot'''
        from supy.utils.root import Dot
        import random,ROOT as r
        LV = r.Math.LorentzVector(r.Math.PxPyPzM4D('double'))
        random.seed(201207241726)
        for i in range(1,30) :
            a_,b_ = zip(*[( i**2*random.random(),i**2*random.random()) for _ in range(4)])
            A = LV(*a_)
            B = LV(*b_)
            self.assertAlmostEqual( A.Dot(B), Dot(A,B) , places = 9)

class testQuadraticInterpolation(unittest.TestCase) :
    @skip("Test not implemented")
    def test(self) :
        '''supy.utils.algos.quadraticInterpolation'''
        from supy.utils.algos import quadraticInterpolation

class testPairs(unittest.TestCase) :
    def test(self) :
        import itertools
        def pairs(l) : return itertools.combinations(l, 2)
        self.assertEqual( set(pairs([])),        set([]) )
        self.assertEqual( set(pairs([1])),       set([]) )
        self.assertEqual( set(pairs([1,2])),     set([(1,2)]) )
        self.assertEqual( set(pairs([1,2,3])),   set([(1,2), (1,3), (2,3)]) )
        self.assertEqual( set(pairs([2,4,8,6])), set([(2,4), (2,6), (2,8), (4,6), (4,8), (8,6)]) )

if __name__ == "__main__" :
    unittest.main()
