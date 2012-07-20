import unittest,sys,os

class temporaryImports(set) :
    '''All modules imported under "with" expression are unloaded upon exit.'''
    def __enter__(self) : self.update(sys.modules)
    def __exit__(self,type,value,traceback) :
        for name in set(sys.modules)-self : del sys.modules[name]


def whereami() : return max('/'.join(__file__.split('/')[:-1]), '.')

if __name__ == "__main__" :
    for mod in ["algos","arguments","integers"] :
        with temporaryImports() as _ :
            path = "%s/%s"%(whereami(),mod)
            sys.path.insert(0,path)
            os.chdir(path)
            msg = "|| %s ||"%mod
            print msg.join(2*'\n').join( 2 * [len(msg)*"="] )
            suite = unittest.TestLoader().loadTestsFromName(mod)
            unittest.TextTestRunner(verbosity=2).run(suite)
            print
        print
    print
