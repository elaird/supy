import unittest,supy

class test1LocalConfiguration(unittest.TestCase) :
    def test(self) :
        '''Check that we load the local configuration.py'''
        self.assertTrue( hasattr(supy.__analysis__.configuration, "localpath"))
        self.assertEqual( "tests/supy-bin", supy.__analysis__.configuration.localpath() )

class test2SupyNoArgs(unittest.TestCase) :
    def test(self) :
        '''Check that supy runs when given no arguments'''
        dct = supy.utils.getCommandOutput("supy")
        self.assertTrue( "returncode" in dct )
        self.assertEqual(0, dct["returncode"])

        self.assertTrue( "stderr" in dct )
        self.assertTrue( not dct["stderr"] )

if __name__ == '__main__':
    unittest.main()
