import unittest,sys,os

testmodules = ["supy-bin","algos","wrappedchain","kinfit","asymmweight","supy-analysis","numpy-dep"]

abspath = __file__ if __file__[0]=='/' else os.getcwd() +"/"+ __file__
def whereami() : return '/'.join(abspath.split('/')[:-1])

if __name__ == "__main__" :
    def run(mod) :
        sys.path.insert(0,whereami())
        sys.path.insert(1,'/'.join((whereami(),mod)))
        os.chdir('/'.join((whereami(),mod)))
        msg = "|| %s ||"%mod
        print msg.join(2*'\n').join( 2 * [len(msg)*"="] )
        suite = unittest.TestLoader().loadTestsFromName(mod)
        unittest.TextTestRunner(verbosity= 2 if "-v" in sys.argv else 1).run(suite)
        print

    mods = [m for m in sys.argv if m in testmodules]
    if len(mods) == 1 :
        run(mods[0])
        sys.exit(0)
    for mod in mods if mods else testmodules :
        os.system('python %s %s %s'%(abspath,mod,"-v" if "-v" in sys.argv else ''))

else :
    from __compatibility__ import skip,skipIf,skipUnless,expectedFailure
