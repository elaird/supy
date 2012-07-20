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
        self.fail(msg = "test not completely written")

class testEdgesRebinned(unittest.TestCase) :
    def test(self) :
        '''supy.utils.algos.edgesRebinned'''
        self.fail("test not implemented")
        
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
