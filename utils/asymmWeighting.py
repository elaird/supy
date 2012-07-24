import math
from supy import utils
try: import numpy as np
except: pass

def reindex(y,tup) : return y[tup,][:,tup]

def twiceDots(p, diag=False) :
    '''Matrix of twice the 4-vector dot products.'''
    indices = range(len(p))
    y = np.array( [ [ 2 * utils.Dot(p[i],p[j]) if i<j else
                      p[i].M2()                if i==j and diag else
                      0         for j in indices] for i in indices])
    return y.T + y

class Asymm_hard(object) :
    '''See reference: Kuhn&Rodrigo98, arXiv:hep-ph/9807420v1'''
    @staticmethod
    def kernel() : assert False, "Define this method in child."

    @staticmethod
    def constant(alpha_s = 1.1, d2abc = 40./3, Nc = 3.) :
        return alpha_s**3 * d2abc / (4*math.pi* 16 * Nc**2 )

    def xs(self, A = 1.0) :
        return (self.symm + self.anti*A) * self.constant()

    def weight(self, targetAsymmetry, nominalAsymmetry = 1.0) :
        return (self.symm + self.anti * targetAsymmetry) /\
               (self.symm + self.anti * nominalAsymmetry)

    def __init__(self, massQ = 172.5 , momenta = [] ) :
        self.M22 = 2*massQ**2
        if momenta : self.setMomenta(momenta)

    def setMomenta(self,p) :
        '''p is [LorentzV]'''
        Y = twiceDots(p)
        kernels = [ self.kernel( reindex(Y,I), self.M22 ) for I in self.indices ]
        self.anti = np.dot(kernels, [(-1)**((I[0]==0)^(I[2]==2)) for I in self.indices])
        self.symm = sum(kernels)
        return self

class Asymm_qqbar_hard(Asymm_hard) :
    '''q(0) + qbar(1) ==> Q(2) + Qbar(3) + g(4)'''
    @staticmethod
    def kernel(Y,M22) :
        sq = np.array( [M22] + [Y[ij] for ij in [(0,2),(0,3),(1,2),(1,3)]])
        num = 2*M22*Y[1,3] + (Y[0,2]/Y[0,4]) * (sq.dot(sq) + M22*(Y[2,3]+Y[0,1]))
        den = Y[0,1] * Y[2,4] * ( Y[2,3] + M22 )
        return num / den
    indices = [ (0,1,2,3,4), (1,0,2,3,4), (0,1,3,2,4), (1,0,3,2,4)]
    
class Asymm_qg_hard(Asymm_hard) :
    '''q(0) + g(1) ==> Q(2) + Qbar(3) + q(4)'''
    @staticmethod
    def kernel(Y,M22) :
        sq = np.array( [M22] + [Y[ij] for ij in [(0,2),(0,3),(2,4),(3,4)]])
        num = 2*M22*(Y[3,4]+Y[0,3]) + (Y[0,2]/Y[0,1] - Y[2,4]/Y[1,4]) * (sq.dot(sq) + M22*(Y[2,3]+Y[0,4]))
        den = Y[0,4] * Y[1,2] * ( Y[2,3] + M22 )
        return num / den
    indices = [ (0,1,2,3,4), (0,1,3,2,4) ]
