import unittest

if __name__ == "__main__" :
    for mod in ["integers"] :
        suite = unittest.TestLoader().loadTestsFromName(mod)
        unittest.TextTestRunner(verbosity=2).run(suite)
