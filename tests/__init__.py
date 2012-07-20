import unittest,sys

class temporaryImports(set) :
    '''All modules imported under "with" expression are unloaded upon exit.'''
    def __enter__(self) : self.update(sys.modules)
    def __exit__(self,type,value,traceback) :
        for name in set(sys.modules)-self : del sys.modules[name]


if __name__ == "__main__" :
    for mod in ["algos","integers"] :
        with temporaryImports() as _ :
            msg = "|| %s ||"%mod
            size = len(msg)
            print '\n'.join(['','',size*"=",msg,size*"=",''])
            suite = unittest.TestLoader().loadTestsFromName(mod)
            unittest.TextTestRunner(verbosity=2).run(suite)
            print "\n\n"
