import unittest,sys

if hasattr(unittest,'skip') :
    from unittest import skip,skipIf,skipUnless,expectedFailure
else:
    print "skip* and expectedFailure compatibility mode!"
    sys.stdout.flush()

    class expectedFailure(object):
        def __init__(self, f): self.f = f
        def __call__(self, *args):
            print 'expect fail ' if '-v' in sys.argv else  'x',
            sys.stdout.flush()

    class skipIf(object):
        def __init__(self, condition, reason) :
            self.reason = reason
            self.condition = condition
        def __call__(self, f):
            def wrapped_f(*args):
                if self.condition :
                    print 'skipped ' if '-v' in sys.argv else 's',
                    sys.stdout.flush()
                else : f(*args)
            return wrapped_f

    def skip(reason) : return skipIf(True, reason)
    def skipUnless(condition, reason) : return( not condition, reason )
