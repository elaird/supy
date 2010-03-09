import pstats

inputFile='resultProfile.out'
p = pstats.Stats(inputFile)

#p.sort_stats('cumulative').print_stats(20)
p.sort_stats('time').print_stats(20)
#p.sort_stats('time').print_callers()
#p.sort_stats('calls').print_stats(20)
