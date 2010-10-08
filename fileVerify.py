import ROOT as r
import utils,sys,re
from collections import defaultdict

if len(sys.argv)<2 :
    print "usage:",sys.argv[0]," location"
    sys.exit()

location = sys.argv[1]

allFiles = utils.fileListFromSrmLs(location, pruneList=False)

def fileSortKey(f) :
    return eval(f.split('/')[-1].split('_')[2])

# CRAB old : filepathWithName_JOB_ATTEMPT.root
# CRAB new : filepathWithName_JOB_ATTEMPT_RANDOMSTRING.root
pattern  =  r"(_\d+_)(\d+)(_?\w*)(\.root$)"
recombine = "%s%s%d%s.root"

versionDict = defaultdict(list)
for file in allFiles :
    fields = re.split(pattern,file)
    versionDict[ (fields[0],fields[1]) ].append( (int(fields[2]), fields[3]) )

for key,val in versionDict.iteritems() :
    if len(val)==1: continue
    #entries = []
    for attempt in val :
        filename = recombine % (key+attempt)
        chain = r.TChain("chain")
        chain.Add(filename+"/susyTree/tree")
        #entries.append(chain.GetEntries())
        print filename.split('/')[-1], chain.GetEntries()
    print
