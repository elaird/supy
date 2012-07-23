import unittest,sys,os

class temporaryImports(set) :
    '''All modules imported under "with" expression are unloaded upon exit.'''
    def __enter__(self) : self.update(sys.modules)
    def __exit__(self,type,value,traceback) :
        for name in set(sys.modules)-self : del sys.modules[name]


abspath = __file__ if __file__[0]!='.' else os.getcwd() + __file__[1:]
def whereami() : return '/'.join(abspath.split('/')[:-1])

if __name__ == "__main__" :
    for mod in ["supy-bin","algos","wrappedchain"] :
        sys.path.insert(0,whereami())
        with temporaryImports() as _ :
            path = "%s/%s"%(whereami(),mod)
            sys.path.insert(1,path)
            os.chdir(path)
            msg = "|| %s ||"%mod
            print msg.join(2*'\n').join( 2 * [len(msg)*"="] )
            suite = unittest.TestLoader().loadTestsFromName(mod)
            unittest.TextTestRunner(verbosity=2).run(suite)
            sys.path = sys.path[:1] + sys.path[2:]
            print
        print
    print
