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

    def test_Bool(self)   : self.loop( var = 'bool' )   
    def test_Byte(self)   : self.loop( var = 'char' )   
    def test_Ubyte(self)  : self.loop( var = 'uchar' )  
    def test_Short(self)  : self.loop( var = 'short' )  
    def test_Ushort(self) : self.loop( var = 'ushort' ) 
    def test_Int(self)    : self.loop( var = 'int' )    
    def test_Uint(self)   : self.loop( var = 'uint' )   
    def test_Long(self)   : self.loop( var = 'long' )   
    def test_Ulong(self)  : self.loop( var = 'ulong' )  
    def test_Float(self)  : self.loop( var = 'float' )  
    def test_Double(self) : self.loop( var = 'double' ) 

    def testV_Bool(self)   : self.loop( var = 'v_bool' )   
    def testV_Byte(self)   : self.loop( var = 'v_char' )   
    def testV_Ubyte(self)  : self.loop( var = 'v_uchar' )  
    def testV_Short(self)  : self.loop( var = 'v_short' )  
    def testV_Ushort(self) : self.loop( var = 'v_ushort' ) 
    def testV_Int(self)    : self.loop( var = 'v_int' )    
    def testV_Uint(self)   : self.loop( var = 'v_uint' )   
    def testV_Long(self)   : self.loop( var = 'v_long' )   
    def testV_Ulong(self)  : self.loop( var = 'v_ulong' )  
    def testV_Float(self)  : self.loop( var = 'v_float' )  
    def testV_Double(self) : self.loop( var = 'v_double' ) 


    def loop(self, N = 100, var = "") :
        from itertools import izip
        for i,sbaF,sbaT in izip(xrange(N),self.sbaF.entries(N),self.sbaT.entries(N)) :
            F = sbaF[var] if not hasattr(sbaF[var],'__len__') else [j for j in sbaF[var]]
            T = sbaT[var] if not hasattr(sbaT[var],'__len__') else [j for j in sbaT[var]]
            self.assertEqual(F,T)

if __name__ == '__main__':
    unittest.main()
