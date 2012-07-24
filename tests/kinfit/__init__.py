import math,supy,configuration,unittest,supy.utils.fitKinematic as FK
from supy.tests import skip,expectedFailure

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
        self.fitter_ = FK.leastsqLeptonicTop2

    def hasNumpy(self) : self.assertTrue( hasattr(FK,'np'), msg = "System lacks numpy" )
    def assertEqualNP( self, A, B) :
        self.assertEqual(A.shape,B.shape)
        epsilon = (A-B).dot(3*[1]).dot(3*[1])
        self.assertAlmostEqual(0,epsilon, places = 7, msg = "%f"%epsilon)

    @skip("not yet implemented")
    def test(self) : pass

    def test_rotation_matrices(self) :
        self.hasNumpy()
        import numpy as np
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

    def test_cofactor(self) :
        self.hasNumpy()
        import numpy as np
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
