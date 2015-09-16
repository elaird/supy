from optparse import OptionParser
parser = OptionParser("usage: %prog analysis-file.py [options]")
def argOrTrue(option, opt, value, parser) :
    peek = next(iter(parser.rargs),None)
    if peek and peek[0]!='-' : del parser.rargs[0]
    setattr(parser.values, option.dest, peek if peek and peek[0]!='-' else True)
parser.add_option("--loop",    dest = "loop",    default = 0,     type="int", metavar="N",help = "loop over events using N cores (0 means do not loop)")
parser.add_option("--slices",  dest = "slices",  default = 1,     type="int", metavar="S",help = "S>0: split each sample into S slices\t\t\t S<0: split each sample into slices containing S events")
parser.add_option("--by-events",dest="byEvents", default = False, action  = "store_true", help = "--slices by events rather than by files")
parser.add_option("--profile", dest = "profile", default = False, action  = "store_true", help = "profile the code")
parser.add_option("--batch",   dest = "batch",   default = False, action  = "store_true", help = "submit to batch queue")
parser.add_option("--resubmit",dest = "resubmit",default = False, action  = "store_true", help = "resubmit non-completed jobs")
parser.add_option("--tag",     dest = "tag",     default = "",    metavar = "PAR_PAR_PAR",help = "specific combo of multiparameters")
parser.add_option("--sample",  dest = "sample",  default = None,                          help = "specific sample")
parser.add_option("--update",  dest = "update",  default = None,  action = "store_true",  help = "update all secondary calculables")
parser.add_option("--updates", dest = "update",  default = None,  metavar = "sc1,sc2,..", help = "update specified secondary calculables")
parser.add_option("--report",  dest = "report",  default = None,  action = "store_true",  help = "report all secondary calculables")
parser.add_option("--reports", dest = "reports", default = None,  action = "callback", callback = argOrTrue, metavar = "sc1,sc2,..", help = "report specified secondary calculables")
parser.add_option("--jobid",   dest = "jobId",   default = None,  metavar = "id",         help = "[for internal use only]")
parser.add_option("--site",    dest = "site",    default = None,  metavar = "prefix",     help = "[for internal use only]")
parser.add_option("--tags",    dest = "tags",    default = None,  action = "callback", callback = argOrTrue, help = "run specified tags only, or list tags")
parser.add_option("--samples", dest = "samples", default = None,  action = "callback", callback = argOrTrue, help = "run specified samples only, or list samples")
parser.add_option("--omit",    dest = "omit",    default = "",    metavar = "sample1,...", help = "omit specified samples")
parser.add_option("--nocheck", dest = "nocheck", default = False, action = "store_true",   help = "skip the cache check of secondary calcs")
parser.add_option("--quiet",   dest = "quiet",   default = False, action = "store_true",   help = "force quiet mode")
parser.add_option("--skip",    dest = "skip",    default = 0,     type="int",              help = "number of events to skip before looping")

def opts() :
    options,args = parser.parse_args()

    if len(args)!=1 or ".py" not in args[0]:
        parser.print_help()
        exit()

    assert 0 <= options.loop
    assert options.slices
    assert (options.jobId==None or options.batch==False), "options jobid and batch cannot be used simultaneously"
    if options.batch:
        assert options.loop, "--batch requires --loop"
    return options, args[0]

def default(options = []) :
    options,args = parser.parse_args(options)
    return options
