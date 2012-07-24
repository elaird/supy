import math,unittest,supy,ROOT as r
from supy.tests import skip,skipIf
try: import numpy as np
except: np=None

class test_leastsqHadronicTop2(unittest.TestCase) :
    def setUp(self) : pass
    @skip("not yet implemented")
    def test(self) : pass

class test_leastsqHadronicTop(unittest.TestCase) :
    def setUp(self) : pass
    @skip("not yet implemented")
    def test(self) : pass

class test_leastsqLeptonicTop2(unittest.TestCase) :
    def setUp(self) :
        from supy.utils.fitKinematic import leastsqLeptonicTop2
        self.fitter_ = leastsqLeptonicTop2

    def assertEqualNP( self, A, B) :
        self.assertEqual(A.shape,B.shape)
        epsilon = (A-B).dot(3*[1]).dot(3*[1])
        self.assertAlmostEqual(0,epsilon, places = 7, msg = "%f"%epsilon)

    @skipIf(np==None, "System lacks numpy")
    def test(self) :
        LV = r.Math.LorentzVector(r.Math.PxPyPzM4D("double"))
        f = self.fitter_(LV(0,10,0,0.5), 0.1, LV(1,0,0,0), [0,0], np.eye(2), lv = LV)
        self.assertTrue( np.all( f.D == np.array([[0,-1,0],[1,0,0],[0,0,0]]) ), msg = "\nf.D = \n%s"%str(f.D) )

    @skipIf(np==None, "System lacks numpy")
    def test_rotation_matrices(self) :
        self.assertEqualNP( self.fitter_.R(0,0), np.eye(3) )
        self.assertEqualNP( self.fitter_.R(1,0), np.eye(3) )
        self.assertEqualNP( self.fitter_.R(2,0), np.eye(3) )

        self.assertEqualNP( self.fitter_.R(2,math.pi), np.diag([-1,-1,1]) )
        self.assertEqualNP( self.fitter_.R(1,math.pi), np.diag([-1,1,-1]) )
        self.assertEqualNP( self.fitter_.R(0,math.pi), np.diag([1,-1,-1]) )

        self.assertEqualNP( self.fitter_.R(2,0.5*math.pi), np.array([[0,-1,0],
                                                                     [1,0,0],
                                                                     [0,0,1]]))
        self.assertEqualNP( self.fitter_.R(1,0.5*math.pi), np.array([[0,0,-1],
                                                                     [0,1,0],
                                                                     [1,0,0]]))
        self.assertEqualNP( self.fitter_.R(0,0.5*math.pi), np.array([[1,0,0],
                                                                     [0,0,-1],
                                                                     [0,1,0]]))

        self.assertEqualNP( self.fitter_.R(2,-0.5*math.pi), np.array([[0,1,0],
                                                                      [-1,0,0],
                                                                      [0,0,1]]))
        self.assertEqualNP( self.fitter_.R(1,-0.5*math.pi), np.array([[0,0,1],
                                                                      [0,1,0],
                                                                      [-1,0,0]]))
        self.assertEqualNP( self.fitter_.R(0,-0.5*math.pi), np.array([[1,0,0],
                                                                      [0,0,1],
                                                                      [0,-1,0]]))

    @skipIf(np==None, "System lacks numpy")
    def test_cofactor(self) :
        A = np.arange(9).reshape((3,3))
        self.assertEqual( -3, self.fitter_.cofactor(A,(0,0)) )
        self.assertEqual( -12, self.fitter_.cofactor(A,(1,1)) )
        self.assertEqual( -3, self.fitter_.cofactor(A,(2,2)) )
        self.assertEqual( 6, self.fitter_.cofactor(A,(0,1)) )
        self.assertEqual( 6, self.fitter_.cofactor(A,(1,0)) )
        self.assertEqual( -3, self.fitter_.cofactor(A,(0,2)) )
        self.assertEqual( -3, self.fitter_.cofactor(A,(2,0)) )
        self.assertEqual( 6, self.fitter_.cofactor(A,(1,2)) )
        self.assertEqual( 6, self.fitter_.cofactor(A,(2,1)) )
