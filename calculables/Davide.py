from core.wrappedChain import *
import calculables,math,collections,bisect,itertools
from core import utils

class Indices(wrappedChain.calculable) :
    """
    This is a calculable to build the collection of jets that have
    some pt min and eta max. It can be used also for other
    collections, as long as they have a pt and eta.
    """
    def __init__(self, collection = None, ptMin = None, etaMax = None):
        self.moreName = "pt>%f;|eta|<%f" % (ptMin, etaMax)
        for item in ["ptMin", "etaMax" ] :
            setattr(self, item, eval(item))
        self.fixes = collection
        self.stash(["pt", "eta"])

    def update(self, _) :
        pts = self.source[self.pt]  # prefix, suffix
        etas = self.source[self.eta]
        self.value = []
        for i in range(pts.size()):
            if pts.at(i)<self.ptMin: continue #put a break if too slow and coll is sorted
            if abs(etas.at(i))>self.etaMax: continue
            self.value.append(i)

class P4(wrappedChain.calculable) :
    """
    Calculable to build Lorentz vectors from the standard D3PD collections.
    """
    def __init__(self, collection = None,):
        self.fixes = collection
        self.stash(["pt", "eta", "phi", "m"])
    def update(self, _) :
        self.value = [utils.LorentzV(pt, eta, phi, m) for pt,eta,phi,m in zip(self.source[self.pt],
                                                                              self.source[self.eta],
                                                                              self.source[self.phi],
                                                                              self.source[self.m])]

class M01(wrappedChain.calculable) :
    """
    Calculable to compute the invariant mass of the first two objects
    in a collection.
    """
    def __init__(self, collection = None,):
        self.fixes = collection
        self.stash(["P4", "Indices"])
    def update(self, _) :
        P4 = self.source[self.P4]
        indices = self.source[self.Indices]
        jet0 = P4[indices[0]]
        jet1 = P4[indices[1]]
        self.value = (jet0+jet1).M()
        # self.value = sum([P4[indices[i]] for i in [0,1]]).M()
