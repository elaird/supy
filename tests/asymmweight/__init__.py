import math,unittest,supy,configuration,os,itertools,ROOT as r
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
            

class asymm_hard(unittest.TestCase) :
    @skipIf(np==None,"System lacks numpy")
    def test(self) :
        '''supy.utils.asymmWeighting.Asymm_hard'''
        import ROOT as r
        from supy.utils.asymmWeighting import Asymm_qqbar_hard

        LV = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))
        q = LV(18.2,3.9,1.0,0)
        qbar = LV(5.0,-4.3,1.9,0)
        Q = LV(160.9,1.0,0.3,174.0)
        Qbar = LV(103.2,0.8,2.4,174.1)
        g = LV(120.7,0.1,-2.1,0)
        qqbarQQbarg = [q,qbar,Q,Qbar,g]

        asym = Asymm_qqbar_hard()
        asym.setMomenta(qqbarQQbarg)
        symm,anti = asym.symm,asym.anti
        asym.setMomenta([qbar,q,Q,Qbar,g])
        self.assertAlmostEqual(symm, asym.symm)
        self.assertAlmostEqual(anti, -asym.anti)
        asym.setMomenta([qbar,q,Qbar,Q,g])
        self.assertAlmostEqual(symm, asym.symm)
        self.assertAlmostEqual(anti, asym.anti)
        asym.setMomenta([q,qbar,Qbar,Q,g])
        self.assertAlmostEqual(symm, asym.symm)
        self.assertAlmostEqual(anti, -asym.anti)

    def testConstant(self) :
        self.assertEqual(1.1**3 *10 / (432*math.pi),
                         supy.utils.asymmWeighting.Asymm_hard.constant())

    @skipIf(np==None,"System lacks numpy")
    def testKernelQQbar(self) :
        '''supy.utils.asymmWeighting.Asymm_qqbar_hard.kernel'''
        Y = np.ones(25).reshape((5,5))
        k = supy.utils.asymmWeighting.Asymm_qqbar_hard.kernel(Y,1)
        self.assertEqual(k, 9./2)

    @skipIf(np==None,"System lacks numpy")
    def testKernelQg(self) :
        '''supy.utils.asymmWeighting.Asymm_qg_hard.kernel'''
        Y = np.ones(25).reshape((5,5))
        k = supy.utils.asymmWeighting.Asymm_qg_hard.kernel(Y,1)
        self.assertEqual(k, 2)
