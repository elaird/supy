import configuration,supy,unittest

class testNoNumpy(unittest.TestCase) :
    '''Testing that supy still loads when "import numpy" raises an ImportError.'''
    def test(self) : self.assertRaises(ImportError,self.importNumpy)
    def importNumpy(self) : import numpy
