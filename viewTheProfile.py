#!/usr/bin/env python

import pstats,sys

inputFile= sys.argv[1] if len(sys.argv)>1 else 'resultProfile.out'
p = pstats.Stats(inputFile)

#p.sort_stats('cumulative').print_stats(20)
p.sort_stats('time').print_stats(20)
#p.sort_stats('time').print_callers()
#p.sort_stats('calls').print_stats(20)
