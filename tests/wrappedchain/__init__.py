import supy,configuration,unittest

class testLeaves(unittest.TestCase) :
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

if __name__ == '__main__':
    unittest.main()
