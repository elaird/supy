import unittest,sys

class temporaryImports(set) :
    '''All modules imported under "with" expression are unloaded upon exit.'''
    def __enter__(self) : self.update(sys.modules)
    def __exit__(self,type,value,traceback) :
        for modname in set(sys.modules)-self : del sys.modules[modname]


if __name__ == "__main__" :
    for mod in ["integers"] :
        with temporaryImports() as _ :
            suite = unittest.TestLoader().loadTestsFromName(mod)
            unittest.TextTestRunner(verbosity=2).run(suite)
