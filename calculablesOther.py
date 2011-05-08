from wrappedChain import *
import calculables,math
#####################################
class localEntry(wrappedChain.calculable) :
    def update(self,localEntry) :
        self.value = localEntry
#####################################
class entry(wrappedChain.calculable) :
    def update(self,localEntry) :
        self.value = self.source.entry
#####################################
class chain_access(wrappedChain.calculable) :
    def name(self) : return "chain"
    def update(self,ignored) : self.value = self.source._wrappedChain__chain
#####################################
class crock(wrappedChain.calculable) :
    def update(self,localEntry) : self.value = {}
#####################################
class ecalDeadTowerIsBarrel(wrappedChain.calculable) :
    def update(self,ignored) : self.value = map( self.isBarrel, self.source["ecalDeadTowerTrigPrimP4"] )
    def isBarrel(self, p4) : return abs(p4.eta()) < 1.48
#####################################
class lowestUnPrescaledTrigger(wrappedChain.calculable) :
    def __init__(self, sortedListOfPaths = []) :
        self.sortedListOfPaths = sortedListOfPaths
        self.cached = dict()
        self.moreName = "lowest unprescaled of "+','.join(self.sortedListOfPaths).replace("HLT_","")
        
    def update(self, ignored) :
        key = (self.source["run"],self.source["lumiSection"])
        if key not in self.cached :
            self.cached[key] = None
            for path in self.sortedListOfPaths :
                if self.source["prescaled"][path]==1 :
                    self.cached[key] = path
                    break
        self.value = self.cached[key]
##############################
class Mt(wrappedChain.calculable) :
    def name(self) :
        return "%sMt%s%s"%(self.fixes[0], self.fixes[1], self.met)
    
    def __init__(self, collection = None, met = None, byHand = True , allowNonIso = False, isSumP4=False) :
        self.met = met
        self.fixes = collection
        self.stash(["Indices","IndicesNonIso","P4"])
        self.byHand = byHand
        self.isSumP4 = isSumP4
        self.allowNonIso = allowNonIso
        self.moreName = "%s%s, %s, byHand=%d"%(collection[0], collection[1], met, byHand)

    def update(self, ignored) :
        if (not self.source[self.Indices]) and not (self.allowNonIso or self.source[self.indicesNonIso]) :
            self.value= -1.0
            return
        index = self.source[self.Indices][0] if self.source[self.Indices] else \
                self.source[self.IndicesNonIso][0]
        lep = self.source[self.P4][index]
        met = self.source[self.met] * (-1 if self.isSumP4 else 1)

        if self.byHand :
            self.value = math.sqrt( 2.0*lep.pt()*met.pt()*(1.0 - math.cos(r.Math.VectorUtil.DeltaPhi(lep, met))) )
        else :
            self.value = (lep+met).Mt()
#####################################
class jsonWeight(wrappedChain.calculable) :
    def __init__(self, fileName = "", acceptFutureRuns = False) :
        self.moreName = "run:ls in %s"%fileName
        self.acceptFutureRuns = acceptFutureRuns
        if self.acceptFutureRuns : self.moreName += " OR future runs"

        self.json = {}
        self.runs = []
        self.maxRunInJson = -1
        if fileName :
            file = open(fileName)
            self.makeIntJson(eval(file.readlines()[0].replace("\n","")))
            file.close()

    def makeIntJson(self, json) :
        for key,value in json.iteritems() :
            self.json[int(key)] = value
        self.maxRunInJson = max(self.json.keys())
        self.runs = self.json.keys()

    def inJson(self) :
        run = self.source["run"]
        if self.acceptFutureRuns and run>self.maxRunInJson : return True
        if not (run in self.runs) : return False
        lumiRanges = self.json[run]
        ls = self.source["lumiSection"]
        for lumiRange in lumiRanges :
            if (ls>=lumiRange[0] and ls<=lumiRange[1]) : return True
        return False

    def update(self, ignored) :
        self.value = 1.0 if self.inJson() else None
#####################################
