import configuration,unittest,traceback,sys

class testNumpyDependence(unittest.TestCase) :
    def testOverride(self) :
        '''Check that we override numpy and scipy.'''
        for mod in ['numpy','scipy'] :
            self.assertRaises(ImportError,(lambda : __import__(mod)))

    def testSupy(self) :
        '''Check that supy still loads.'''
        try: import supy
        except ImportError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            fileName,lineNumber,_,statement = traceback.extract_tb(exc_traceback)[-2]
            msg = "\n\t\t".join(["Unprotected import statement,",
                                 "%s:%d"%(fileName,lineNumber),
                                 statement])
            self.fail(msg)
