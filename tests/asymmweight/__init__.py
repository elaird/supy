import unittest,supy,configuration,os,itertools
import supy.utils.asymmWeighting as AW
from supy.tests import expectedFailure

import ROOT as r
configuration.initializeROOT(r,configuration.cppFiles())
supy.utils.generateDictionaries(configuration.cppROOTDictionariesToGenerate(), dir=os.getcwd())

def hasNumpy(testClass) :
    testClass.assertTrue( hasattr(AW,'np'), msg = "System lacks numpy" )

class twiceDots(unittest.TestCase) :
    def test(self) :
        hasNumpy(self)
        import numpy as np
        A = supy.utils.LorentzV()
        A.SetM(1)

        for i in range(1,5) :
            tdA = AW.twiceDots(i*[A])
            self.assertEqual( (i,i), tdA.shape )
            self.assertEqual( i*[0], [tdA[j][j] for j in range(i)])
            for el in [tdA[j][k] for j in range(i) for k in range(i) if j!=k] :
                self.assertEqual( 2, el)
            tdA = AW.twiceDots(i*[A], diag=True)
            for el in [tdA[j][k] for j in range(i) for k in range(i)] :
                self.assertEqual( 2, el)

class reindex(unittest.TestCase) :
    def test(self) :
        hasNumpy(self)
        import numpy as np
        y = np.arange(16).reshape((4,4))
        self.assertTrue( np.all( y == AW.reindex(y, (0,1,2,3)) ) )
        for i in itertools.permutations((0,1,2,3),4) :
            Y = AW.reindex(y,i)
            for j,k in [(j,k) for j in range(4) for k in range(4)] :
                self.assertEqual( y[i[j],i[k]], Y[j,k])
            

class qqbar_hard(unittest.TestCase) :
    def setUp(self) : pass
    @expectedFailure
    def test(self) :
        self.fail("not yet implemented")
