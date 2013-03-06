import supy,configuration
from supy.tests import skip,expectedFailure
import array,os,unittest
import ROOT as r

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
    @expectedFailure
    def testV_Ulong(self)  : 
        '''vector<ulong> (maketree fail: bad test)'''
        self.loop( var = 'v_ulong' )


    #number[] leaves
    def testA_Short(self)  : self.loop( var = 'a_short' )
    def testA_Int(self)    : self.loop( var = 'a_int' )
    def testA_Float(self)  : self.loop( var = 'a_float' )
    def testA_Double(self) : self.loop( var = 'a_double' )
    def testA_Uint(self)    : self.loop( var = 'a_uint' )

    @expectedFailure
    def testA_Long(self) :
        '''long[] not identified by sbaF, no hope for sbaT.'''
        self.loop( var = 'a_long' )
    @expectedFailure
    def testA_Bool(self)   :
        '''bool[] (maketree fail)'''
        self.loop( var = 'a_bool' )
    @expectedFailure
    def testA_Byte(self)   : 
        '''char[] (maketree fail)'''
        self.loop( var = 'a_char' )
    @expectedFailure
    def testA_Ubyte(self)  : 
        '''uchar[] (maketree fail)'''
        self.loop( var = 'a_uchar' )
    @expectedFailure
    def testA_Ushort(self)  : 
        '''ushort[] (maketree fail)'''
        self.loop( var = 'a_ushort' )
    @expectedFailure
    def testA_Ulong(self)    : 
        '''ulong[] (maketree fail)'''
        self.loop( var = 'a_ulong' )

    def loop(self, N = 100, var = "") :
        from itertools import izip
        for i,sbaF,sbaT in izip(xrange(N),self.sbaF.entries(N),self.sbaT.entries(N)) :
            F = sbaF[var] if not hasattr(sbaF[var],'__len__') else [j for j in sbaF[var] if j]
            T = sbaT[var] if not hasattr(sbaT[var],'__len__') else [j for j in sbaT[var] if j]
            self.assertEqual(F,T)

class testEmptyTree(unittest.TestCase):
    def fileName(self, index=None):
        return "/".join([supy.whereami(), configuration.localpath(), "%d.root" % index])

    def writeTFiles(self):
        for iList, runList in enumerate(self.runs):
            f = r.TFile(self.fileName(iList), "RECREATE")
            t = r.TTree(self.treeName, "title")
            a = array.array('i', [0])
            t.Branch(self.varName, a, '%s/I'%self.varName)
            for run in runList:
                a[0] = run
                t.Fill()
            f.Write()
            f.Close()

    def setUp(self):
        self.oldErrorIgnoreLevel = r.gErrorIgnoreLevel
        r.gErrorIgnoreLevel = 9999  # suppress messages about missing/broken
                                    # files (purposefully created below)
        self.treeName = "tree"
        self.varName = "run"
        self.runs = [[0,1,2,3],
                     [],
                     [222],
                     [],
                     [444],
                     [],
                     [],
                     [4],
                     [5,6],
                     [],
                     [],
                     ]

        self.writeTFiles()
        chain = r.TChain(self.treeName)
        for iList in range(len(self.runs)):
            fileName = self.fileName(iList)
            if iList==2:
                toRemove = fileName
            if iList==4:
                toBreak = fileName
            chain.Add("/".join([fileName, self.treeName]))

        os.remove(toRemove)  # make a file inaccessible
        os.system("echo 0 > %s" % toBreak)  # make a file unreadable

        self.wc = supy.wrappedChain(chain)

    def tearDown(self):
        r.gErrorIgnoreLevel = self.oldErrorIgnoreLevel

    def test(self):
        runs = []
        for iEntry, dct in enumerate(self.wc.entries(nEntries=None)):
            runs.append(dct[self.varName])
        self.assertEqual(runs, range(7))

if __name__ == '__main__':
    unittest.main()
