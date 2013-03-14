import os
import unittest
import supy.utils


class testCompiler(unittest.TestCase):
    def test_gcc(self):
        dct = supy.utils.getCommandOutput("g++ foo.cxx")
        self.assertEqual('', dct["stderr"])
        self.assertEqual(0, dct["returncode"])

if __name__ == '__main__':
    unittest.main()
