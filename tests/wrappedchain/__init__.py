import supy,configuration,unittest
from unittest import skip,expectedFailure

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

    #numeric leaves
    def test_Bool(self)   : self.loop( var = 'bool' )
    def test_Short(self)  : self.loop( var = 'short' )
    def test_Ushort(self) : self.loop( var = 'ushort' )
    def test_Int(self)    : self.loop( var = 'int' )
    def test_Uint(self)   : self.loop( var = 'uint' )
    def test_Long(self)   : self.loop( var = 'long' )
    def test_Ulong(self)  : self.loop( var = 'ulong' )
    def test_Float(self)  : self.loop( var = 'float' )
    def test_Double(self) : self.loop( var = 'double' )

    @expectedFailure
    def test_Byte(self) :
        '''byte : sbaF reads char | sbaT reads signed word.'''
        self.loop( var = 'char' )

    @expectedFailure
    def test_Ubyte(self) :
        '''ubyte : sbaF => char | sbaT => unsigned word.'''
        self.loop( var = 'uchar' )

    #std::vector<number> leaves
    def testV_Bool(self)   : self.loop( var = 'v_bool' )
    def testV_Byte(self)   : self.loop( var = 'v_char' )
    def testV_Ubyte(self)  : self.loop( var = 'v_uchar' )
    def testV_Short(self)  : self.loop( var = 'v_short' )
    def testV_Ushort(self) : self.loop( var = 'v_ushort' )
    def testV_Int(self)    : self.loop( var = 'v_int' )
    def testV_Uint(self)   : self.loop( var = 'v_uint' )
    def testV_Long(self)   : self.loop( var = 'v_long' )
    def testV_Float(self)  : self.loop( var = 'v_float' )
    def testV_Double(self) : self.loop( var = 'v_double' )

    @unittest.skip("vector<ulong> (assignment fails in maketree)")
    def testV_Ulong(self)  : self.loop( var = 'v_ulong' )


    #number[] leaves
    def testA_Short(self)  : self.loop( var = 'a_short' )
    def testA_Int(self)    : self.loop( var = 'a_int' )
    def testA_Float(self)  : self.loop( var = 'a_float' )
    def testA_Double(self) : self.loop( var = 'a_double' )

    @unittest.expectedFailure
    def testA_Long(self) :
        '''long[] not identified by sbaF, no hope for sbaT.'''
        self.loop( var = 'a_uint' )

    @unittest.skip("bool[] (maketree fail)")
    def testA_Bool(self)   : self.loop( var = 'v_bool' )
    @unittest.skip("char[] (maketree fail)")
    def testA_Byte(self)   : self.loop( var = 'v_char' )
    @unittest.skip("uchar[] (maketree fail)")
    def testA_Ubyte(self)  : self.loop( var = 'v_uchar' )
    @unittest.skip("ushort[] (maketree fail)")
    def testA_Ushort(self)  : self.loop( var = 'a_ushort' )
    @unittest.skip("uint[] (maketree fail)")
    def testA_Uint(self)    : self.loop( var = 'a_uint' )
    @unittest.skip("ulong[] (maketree fail)")
    def testA_Ulong(self)    : self.loop( var = 'a_uint' )



    def loop(self, N = 100, var = "") :
        from itertools import izip
        for i,sbaF,sbaT in izip(xrange(N),self.sbaF.entries(N),self.sbaT.entries(N)) :
            F = sbaF[var] if not hasattr(sbaF[var],'__len__') else [j for j in sbaF[var] if j]
            T = sbaT[var] if not hasattr(sbaT[var],'__len__') else [j for j in sbaT[var] if j]
            self.assertEqual(F,T)

if __name__ == '__main__':
    unittest.main()
