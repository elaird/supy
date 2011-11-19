from core.wrappedChain import *
import calculables,math,collections,bisect,itertools
from core import utils

class Indices(wrappedChain.calculable) :
    def __init__(self, collection = None, ptMin = None, etaMax = None):
        self.moreName = "pt>%f;|eta|<%f" % (ptMin, etaMax)
        for item in ["collection", "ptMin", "etaMax" ] :
            setattr(self, item, eval(item))

    def update(self, _) :
        pts = self.source["%spt%s"%self.collection]  # prefix, suffix
        etas = self.source["%seta%s"%self.collection]
        self.value = []
        
        for i in range(pts.size()):
            if pts.at(i)<self.ptMin: continue #put a break if too slow and coll is sorted
            if abs(etas.at(i))>self.etaMax: continue
            self.value.append(i)
    @property
    def name(self) : return "%sIndices%s" % self.collection

class P4(wrappedChain.calculable) :
    def __init__(self, collection = None,):
        for item in ["collection"] :
            setattr(self, item, eval(item))
    def update(self, _) :
        self.value = [utils.LorentzV(pt, eta, phi, m) for pt,eta,phi,m in zip(self.source['%spt%s'%self.collection],
                                                                              self.source['%seta%s'%self.collection],
                                                                              self.source['%sphi%s'%self.collection],
                                                                              self.source['%sm%s'%self.collection])]
    @property
    def name(self) : return "%sP4%s" % self.collection

class M01(wrappedChain.calculable) :
    def __init__(self, collection = None,):
        for item in ["collection"] :
            setattr(self, item, eval(item))
    def update(self, _) :
        P4 = self.source["%sP4%s" % self.collection]
        indices = self.source["%sIndices%s" % self.collection]
        jet0 = P4[indices[0]]
        jet1 = P4[indices[1]]
        self.value = (jet0+jet1).M()
        # self.value = sum([P4[indices[i]] for i in [0,1]]).M()

    @property
    def name(self) : return "%sM01%s" % self.collection


