from core.wrappedChain import wrappedChain
from core import utils
import calculables
import ROOT as r
##############################
class TwoToTwo(wrappedChain.calculable) :
    def update(self,_) :
        self.value = 1 if list(self.source['genMotherIndex']).count(4)==2 else None
##############################
class genSumP4(wrappedChain.calculable) :
    def update(self,_) :
        genP4 = self.source['genP4']
        self.value = genP4.at(2) + genP4.at(3)
##############################
class wNonQQbar(wrappedChain.calculable) :
    def update(self,_) :
        self.value = None if self.source['genQQbar'] else 1
##############################
class wQQbar(wrappedChain.calculable) :
    def update(self,_) :
        self.value = 1 if self.source['genQQbar'] else None
##############################
class genQQbar(wrappedChain.calculable) :
    def update(self,_) :
        ids = list(self.source['genPdgId'])
        self.value = tuple(sorted([4,5],key = ids.__getitem__,reverse = True)) \
                     if not sum(ids[4:6]) else tuple()
##############################
class genIndexStrongerParton(wrappedChain.calculable) :
    def update(self,_) :
        self.value = max([(abs(self.source['genP4'][i].pz()),i) for i in [2,3]])[1]
##############################
class genMotherPdgId(wrappedChain.calculable) :
    def isFake(self) : return True
    def update(self,_) :
        self.value = map( self.motherId, self.source["genHasMother"], self.source["genMotherStored"], self.source["genMother"])
    def motherId(self, hasMom, momStored, mom) :
        return 0 if not hasMom else \
               mom if not momStored else \
               self.source["genPdgId"].at(mom)
##############################
class genStatus1P4(wrappedChain.calculable) :
    def update(self,_) :
        self.value = []
        for i in range(self.source["genP4"].size()) :
            if self.source["genStatus"].at(i)!=1 : continue
            self.value.append(self.source["genP4"][i])
##############################
class genMotherIndex(wrappedChain.calculable) :
    def isFake(self) : return True
    def update(self,_) :
        self.value = map( self.motherIndex, self.source["genHasMother"], self.source["genMotherStored"], self.source["genMother"])
    def motherIndex(self, hasMom, momStored, mom) :
        return -1 if not (hasMom and momStored) else mom
##############################
class genIndices(wrappedChain.calculable) :
    @property
    def name(self) : return "genIndices" + self.label

    def __init__(self, pdgs = None, label = None, status = None ) :
        self.label = label
        self.PDGs = frozenset(pdgs)
        self.status = frozenset(status)
        self.moreName = "pdgId in %s; status in %s" % (str(list(self.PDGs)), str(list(self.status)))

    def update(self,_) :
        pdg = self.source["genPdgId"]
        status = self.source["genStatus"]
        self.value = filter( lambda i: pdg.at(i) in self.PDGs and \
                             status.at(i) in self.status, range(pdg.size()) )
##############################
class genIndicesB(wrappedChain.calculable) :
    def update(self,_) :
        ids = self.source['genPdgId']
        self.value = filter(lambda i: abs(ids[i]) is 5, range(len(ids)))
##############################
class genIndicesWqq(wrappedChain.calculable) :
    def update(self,_) :
        ids = self.source['genPdgId']
        mom = self.source['genMotherPdgId']
        self.value = filter(lambda i: abs(mom[i]) is 24 and abs(ids[i]) < 5, range(len(ids)))
##############################
class genIndicesStatus3NoStatus3Daughter(wrappedChain.calculable) :
    def update(self,_) :
        status = self.source["genStatus"]
        mother = self.source["genMotherIndex"]

        status3List = filter( lambda i: status.at(i)==3, range(status.size()) )
        motherIndices = set([mother[i] for i in status3List])
        self.value = filter( lambda i: i not in motherIndices, status3List )
##############################
class genttCosThetaStar(wrappedChain.calculable) :
    def update(self,_) :
        assert self.source['wQQbar']

        self.value = ()
        ids = list(self.source['genPdgId'])
        if not (6 in ids and -6 in ids) :
            print "Fail ttbar"
            return
        
        mom = self.source['genMotherIndex']
        iTop = ids.index(6)
        iTbar = ids.index(-6)
        iQ,iQbar = sorted([mom[iTop],mom[iTop]+1], key = ids.__getitem__,reverse=True)
        if ids[iQ]+ids[iQbar] :
            print "Fail qqbar", iQ,iQbar
            return

        p4s = self.source['genP4']
        beta = (p4s[iQ]+p4s[iQbar]).BoostToCM()
        boost = r.Math.Boost(beta.x(), beta.y(), beta.z())
        cosTheta = r.Math.VectorUtil.CosTheta( boost(p4s[iQ]), boost(p4s[iTop]))
        cosThetaBar = r.Math.VectorUtil.CosTheta( boost(p4s[iQbar]), boost(p4s[iTbar]))
        self.value = (cosTheta,cosThetaBar)
##############################
class genMinDeltaRPhotonOther(wrappedChain.calculable) :
    @property
    def name(self) : return "genMinDeltaRPhotonOther"+self.label
    
    def __init__(self, label) :
        self.label = label
        
    def update(self,_) :
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
    @property
    def name(self) : return "genIsolation"+self.label
    
    def __init__(self, label = None, coneSize = None) :
        for item in ["label","coneSize"] :
            setattr(self,item,eval(item))
        
    def update(self, _) :
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
    @property
    def name(self) :
        return "category"+self.label

    def __init__(self, label) :
        self.label = label
        
    def update(self, _) :
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
    @property
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

    def update(self,_) :
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
######################################
class qDirProbPlus(calculables.secondary) :
    def __init__(self, var, limit, tag, sample, path = None) :
        for item in ['var','tag','sample', 'limit','path'] : setattr(self,item,eval(item))
        self.fixes = ('',var)
        self.dist = "qdir.%s"%self.var
        self.p = None

    def onlySamples(self) : return [self.sample]

    def setup(self,*_) :
        import numpy as np
        orig = self.fromCache( [self.sample], [self.dist], tag = self.tag)[self.sample][self.dist]
        if not orig : return

        edges = utils.edgesRebinned(orig, targetUncRel = 0.065)
        hist = orig.Rebin(len(edges)-1, "tmp", edges)
        vals  = [hist.GetBinContent(i) for i in range(1,len(edges))]
        del hist
        iZero = edges.index(0)
        R = np.array(vals[iZero:])
        L = np.array(vals[:iZero])[::-1]
        p = R / ( R + L )

        self.p = r.TH1D(self.name, ";|%s|;p of correct qDir"%self.var, len(edges[iZero:])-1, edges[iZero:])
        for i in range(len(p)) : self.p.SetBinContent(i+1,p[i])
        self.p.SetBinContent(len(edges[iZero:])+2, edges[-1])

        if self.path is not None :
            c = r.TCanvas()
            self.p.Draw('hist')
            utils.tCanvasPrintPdf(c,'%s/%s'%(self.path,'.'.join([self.name,self.sample,self.tag])))
            del c

    def update(self,_) :
        var = self.source[self.var]
        p = self.p.GetBinContent(self.p.FindFixBin(var)) if self.p else 0.5
        self.value = p if var > 0 else 1-p

    def uponAcceptance(self,ev) :
        if ev['isRealData'] : return
        qqbar = ev['genQQbar']
        if not qqbar : return
        qdir = 1 if ev['genP4'][qqbar[0]].pz()>0 else -1
        var = ev[self.var]
        self.book.fill(qdir*var, self.dist, 1000, -self.limit, self.limit, title = ";qdir * %s;events / bin"%self.var )
