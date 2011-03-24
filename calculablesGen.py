from wrappedChain import wrappedChain
import ROOT as r
##############################
class genSumP4(wrappedChain.calculable) :
    def update(self,ignored) :
        genP4 = self.source['genP4']
        self.value = genP4.at(2) + genP4.at(3)
##############################
class genQQbar(wrappedChain.calculable) :
    def update(self,ignored) :
        ids = list(self.source['genPdgId'])
        self.value = tuple(sorted([2,3],key = ids.__getitem__,reverse = True)) \
                     if not sum(ids[2:4]) else tuple()
##############################
class genIndexStrongerParton(wrappedChain.calculable) :
    def update(self,ignored) :
        self.value = max([(abs(self.source['genP4'][i].pz()),i) for i in [2,3]])[1]
##############################
class genMotherPdgId(wrappedChain.calculable) :
    def isFake(self) : return True
    def update(self,ignored) :
        self.value = map( self.motherId, self.source["genHasMother"], self.source["genMotherStored"], self.source["genMother"])
    def motherId(self, hasMom, momStored, mom) :
        return 0 if not hasMom else \
               mom if not momStored else \
               self.source["genPdgId"].at(mom)
##############################
class genStatus1P4(wrappedChain.calculable) :
    def update(self,ignored) :
        self.value = []
        for i in range(self.source["genP4"].size()) :
            if self.source["genStatus"].at(i)!=1 : continue
            self.value.append(self.source["genP4"][i])
##############################
class genMotherIndex(wrappedChain.calculable) :
    def isFake(self) : return True
    def update(self,ignored) :
        self.value = map( self.motherIndex, self.source["genHasMother"], self.source["genMotherStored"], self.source["genMother"])
    def motherIndex(self, hasMom, momStored, mom) :
        return -1 if not (hasMom and momStored) else mom
##############################
class genIndices(wrappedChain.calculable) :
    def name(self) : return "genIndices" + self.label

    def __init__(self, pdgs = None, label = None, status = None ) :
        self.label = label
        self.PDGs = frozenset(pdgs)
        self.status = frozenset(status)
        self.moreName = "pdgId in %s; status in %s" % (str(list(self.PDGs)), str(list(self.status)))

    def update(self,ignored) :
        pdg = self.source["genPdgId"]
        status = self.source["genStatus"]
        self.value = filter( lambda i: pdg.at(i) in self.PDGs and \
                             status.at(i) in self.status, range(pdg.size()) )
##############################
class genIndicesStatus3NoStatus3Daughter(wrappedChain.calculable) :
    def update(self,ignored) :
        status = self.source["genStatus"]
        mother = self.source["genMotherIndex"]

        status3List = filter( lambda i: status.at(i)==3, range(status.size()) )
        motherIndices = set([mother[i] for i in status3List])
        self.value = filter( lambda i: i not in motherIndices, status3List )
##############################
class genMinDeltaRPhotonOther(wrappedChain.calculable) :
    def name(self) : return "genMinDeltaRPhotonOther"+self.label
    
    def __init__(self, label) :
        self.label = label
        
    def update(self,ignored) :
        st3Indices = self.source["genIndicesStatus3NoStatus3Daughter"]
        genP4s = self.source["genP4"]
        ids = self.source["genPdgId"]

        def minDeltaR(photonIndex) :
            candidates = [ (r.Math.VectorUtil.DeltaR(genP4s.at(photonIndex), genP4s.at(i)), ids.at(i))  for i in st3Indices]
            return min(filter(lambda x: x[1]!=22, candidates))

        photonIndices = self.source["genIndices"+self.label]
        self.value = min( [minDeltaR(photonIndex) for photonIndex in photonIndices] )[0] if len(photonIndices) else None
##############################
class genIsolations(wrappedChain.calculable) :
    def name(self) : return "genIsolation"+self.label
    
    def __init__(self, label = None, coneSize = None) :
        for item in ["label","coneSize"] :
            setattr(self,item,eval(item))
        
    def update(self, ignored) :
        genP4s = self.source["genP4"]
        nGen = genP4s.size()
        genIndices = self.source["genIndices"+self.label]
        self.value = {}
        for genIndex in genIndices :
            iso = 0.0
            for iParticle in range(nGen) :
                if iParticle==genIndex : continue
                if self.source["genStatus"].at(iParticle)!=1 : continue
                if self.source["genPdgId"].at(iParticle) in [-12, 12, -14, 14, -16, 16] : continue
                if r.Math.VectorUtil.DeltaR(genP4s.at(genIndex), genP4s.at(iParticle)) > self.coneSize : continue
                iso += genP4s.at(iParticle).pt()
            self.value[genIndex] = iso
##############################
class genPhotonCategory(wrappedChain.calculable) :
    def name(self) :
        return "category"+self.label

    def __init__(self, label) :
        self.label = label
        
    def update(self, ignored) :
        self.value = {}

        for index in self.source["genIndices"+self.label] :
            moId = self.source["genMotherPdgId"][index]
            if moId==22 :
                self.value[index] = "photonMother"
            elif abs(moId)<22 :
                self.value[index] = "quarkMother"
            else :
                self.value[index] = "otherMother"
##############################
class genParticleCounter(wrappedChain.calculable) :
    def name(self) : return "GenParticleCategoryCounts"

    def __init__(self) :
        self.value = {}
        self.pdgToCategory = {}

        #copied from PDG
        self.initPdgToCategory( 1, 6,"quark")
        self.initPdgToCategory(21,21,"gluon")

        self.initPdgToCategory(1000001,1000004,"squarkL")#left-handed
        self.initPdgToCategory(1000005,1000006,"squarkA")#ambiguous
        self.initPdgToCategory(1000011,1000016,"slepton")
        self.initPdgToCategory(2000001,2000004,"squarkR")#right-handed
        self.initPdgToCategory(2000005,2000006,"squarkA")#ambiguous
        self.initPdgToCategory(2000011,2000011,"slepton")
        self.initPdgToCategory(2000013,2000013,"slepton")
        self.initPdgToCategory(2000015,2000015,"slepton")
        self.initPdgToCategory(1000021,1000021,"gluino")
        self.initPdgToCategory(1000022,1000023,"chi0")
        self.initPdgToCategory(1000024,1000024,"chi+")
        self.initPdgToCategory(1000025,1000025,"chi0")
        self.initPdgToCategory(1000035,1000035,"chi0")
        self.initPdgToCategory(1000037,1000037,"chi+")
        self.initPdgToCategory(1000039,1000039,"gravitino")

        self.combineCategories(["squarkL","squarkR","squarkA"], "squark")
        self.combineCategories(["slepton","chi0","chi+","gravitino"], "otherSusy")

        self.badCategoryName = "noName"
        self.categories = list(set(self.pdgToCategory.values()))
        self.categories.append(self.badCategoryName)
        self.categories.sort()
        #self.printDict(self.pdgToCategory)

    def initPdgToCategory(self,lower,upper,label) :
        for i in range(lower,upper+1) :
            self.pdgToCategory[i]=label
        for i in range(-upper,-lower+1) :
            self.pdgToCategory[i]=label

    def combineCategories(self,someList,someLabel) :
        for key in self.pdgToCategory :
            if self.pdgToCategory[key] in someList :
                self.pdgToCategory[key]=someLabel
        
    def printDict(self,someDict) :
        for key in someDict :
            print key,someDict[key]

    def zeroCategoryCounts(self) :
        for key in self.categories :
            self.value[key]=0

    def isSusy(self, pdgId) :
        reducedPdgId = abs(pdgId)/1000000
        return reducedPdgId==1 or reducedPdgId==2 or (pdgId in [25,32,33,34,35,36,37])

    def incrementCategory(self,pdgId) :
        if pdgId in self.pdgToCategory:
            category=self.pdgToCategory[pdgId]
        else :
            category=self.badCategoryName
        self.value[category]+=1
        #print "found one:",iParticle,pdgId

    def update(self,ignored) :
        self.zeroCategoryCounts()
        if not self.source["genHandleValid"] : return
        nParticles = len(self.source["genPdgId"])

        #Susy counts
        for iParticle in range(nParticles) :
            #consider only status 3 particles
            if self.source["genStatus"].at(iParticle)!=3 : continue
            #which are SUSY particles
            if not self.isSusy(self.source["genPdgId"].at(iParticle)) : continue
            #whose mothers are not SUSY particles
            if self.isSusy(self.source["genMotherPdgId"].at(iParticle)) : continue
            self.incrementCategory(self.source["genPdgId"].at(iParticle))

        #initial state counts
        for iParticle in range(nParticles) :
            #consider only status 3 particles
            if self.source["genStatus"].at(iParticle)!=3 : continue
            #whose mothers are protons
            if self.source["genMotherPdgId"].at(iParticle)!=2212 : continue
            #whose mothers have index 0 or 1
            if self.source["genMotherIndex"].at(iParticle) not in [0,1] : continue
            self.incrementCategory(self.source["genPdgId"].at(iParticle))
