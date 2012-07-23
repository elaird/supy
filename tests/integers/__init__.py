import supy,configuration,unittest

class test1LocalConfiguration(unittest.TestCase) :
    def test(self) :
        '''Check that we load the local configuration.py'''
        self.assertEqual( ("djtuple","tree"), configuration.mainTree())
        self.assertTrue( hasattr(supy.__analysis__.configuration, "localpath"))
        self.assertEqual( "tests/integers", supy.__analysis__.configuration.localpath() )

class test2Integers(unittest.TestCase) :
    def setUp(self) :
        import maketree,ROOT as r
        maketree.writeTree()
        def tchain(name) :
            chain = r.TChain(name)
            chain.Add("/".join( (maketree.filePath(),) + configuration.mainTree() ) )
            return chain

        self.sbaF = supy.wrappedChain(tchain("sbaF"), useSetBranchAddress = False)
        self.sbaT = supy.wrappedChain(tchain("sbaT"), useSetBranchAddress = True)

    def testBool(self) : self.loop( var = 'bool' )
    def testByte(self) : self.loop( var = 'byte' )
    def testUbyte(self) : self.loop( var = 'ubyte' )
    def testShort(self) : self.loop( var = 'short' )
    def testUshort(self) : self.loop( var = 'ushort' )
    def testInt(self) : self.loop( var = 'int' )
    def testUint(self) : self.loop( var = 'uint' )
    def testLong(self) : self.loop( var = 'long' )
    def testUlong(self) : self.loop( var = 'ulong' )
    def testFloat(self) : self.loop( var = 'float' )
    def testDouble(self) : self.loop( var = 'double' )

    def loop(self, N = 100, var = "") :
        from itertools import izip
        error = "MISMATCH in event %d: sbaF['"+var+"'] = %s != %s = sbaT['"+var+"']"
        for i,sbaF,sbaT in izip(xrange(N),self.sbaF.entries(N),self.sbaT.entries(N)) :
            self.assertEqual(sbaF[var],sbaT[var],  msg = error%(i,str(sbaF[var]),str(sbaT[var])))

class test3Integers(unittest.TestCase) :

    def setUp(self) :
        import integers
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

if __name__ == '__main__':
    unittest.main()
