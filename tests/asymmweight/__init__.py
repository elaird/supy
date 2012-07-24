import unittest,supy,configuration,os,itertools,ROOT as r
from supy.tests import expectedFailure,skipIf
try: import numpy as np
except: np=None

class twiceDots(unittest.TestCase) :
    @skipIf(np==None,"System lacks numpy")
    def test(self) :
        '''supy.utils.asymmWeighting.twiceDots'''
        from supy.utils.asymmWeighting import twiceDots
        LV = r.Math.LorentzVector(r.Math.PxPyPzM4D('double'))
        A = LV(0,0,0,1)

        self.assertTrue( np!=None )
        for i in range(1,5) :
            tdA = twiceDots(i*[A])
            self.assertEqual( (i,i), tdA.shape )
            self.assertEqual( i*[0], [tdA[j][j] for j in range(i)])
            for el in [tdA[j][k] for j in range(i) for k in range(i) if j!=k] :
                self.assertEqual( 2, el)
            tdA = twiceDots(i*[A], diag=True)
            for el in [tdA[j][k] for j in range(i) for k in range(i)] :
                self.assertEqual( 2, el)

class reindex(unittest.TestCase) :
    @skipIf(np==None,"System lacks numpy")
    def test(self) :
        '''supy.utils.asymmWeighting.reindex'''
        from supy.utils.asymmWeighting import reindex
        y = np.arange(16).reshape((4,4))
        self.assertTrue( np.all( y == reindex(y, (0,1,2,3)) ) )
        for i in itertools.permutations((0,1,2,3),4) :
            Y = reindex(y,i)
            for j,k in [(j,k) for j in range(4) for k in range(4)] :
                self.assertEqual( y[i[j],i[k]], Y[j,k])
            

class qqbar_hard(unittest.TestCase) :
    def setUp(self) : pass
    @expectedFailure
    def test(self) :
        self.fail("not yet implemented")
