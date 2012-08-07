import math
from root import Dot
try: import numpy as np
except: pass

def reindex(y,tup) : return y[tup,][:,tup]

def twiceDots(p, diag=False) :
    '''Matrix of twice the 4-vector dot products.'''
    indices = range(len(p))
    y = np.array( [ [ 2 * Dot(p[i],p[j]) if i<j else
                      p[i].M2()                if i==j and diag else
                      0         for j in indices] for i in indices])
    return y.T + y

class Asymm_hard(object) :
    def weight(self, targetAsymmetry, nominalAsymmetry = 1.0) :
        return (self.symm + self.anti * targetAsymmetry) /\
               (self.symm + self.anti * nominalAsymmetry)

    def __init__(self, massQ = 172.5 , momenta = [] ) :
        self.M22 = 2*massQ**2
        if momenta : self.setMomenta(momenta)

    def setMomenta(self,p, check = False) :
        '''p is [LorentzV]'''
        a = A( self.reindexed(twiceDots(p)), self.M22, check)
        self.symm = a.symm
        self.anti = a.anti
        return self

class Asymm_qqbar_hard(Asymm_hard) :
    '''q(0) + qbar(1) ==> Q(2) + Qbar(3) + g(4)'''
    @staticmethod
    def reindexed(Y) :
        return reindex(Y, (3,2,1,0,4)) * [1,1,-1,-1,1] * [[1],[1],[-1],[-1],[1]]

class Asymm_qg_hard(Asymm_hard) :
    '''q(0) + g(1) ==> Q(2) + Qbar(3) + q(4)'''
    @staticmethod
    def reindexed(Y) :
        return reindex(Y, (3,2,4,1,0)) * [1,1,1,-1,-1] * [[1],[1],[1],[-1],[-1]]

class A(object) :
    '''Formula 10 from "Explicit formulae for heavy flavour production", R.K. Ellis and J.C. Sexton.

    Q(-p0) + Qbar(-p1) ==> q(p2) + qbar(p3) + g(p4)
    '''
    def __init__(self, y, m22, check=False ) :
        N = 3.
        V = N*N-1
        S = m22+y[0,1]
        self.cf = (N*N-1)/(N*S*y[2,3]) # common factor / common subfactor
        self.csf = m22*(y[0,1]+y[2,3]) + np.dot(*2*([m22]+[y[i,j] for i,j in [(0,2),(1,2),(0,3),(1,3)]],))
        for item in ['N','S','V','m22'] : setattr(self,item,eval(item))

        ys = [reindex(y,I) for I in [(0,1,2,3,4),(1,0,2,3,4),(0,1,3,2,4),(1,0,3,2,4)]]
        self.symm = sum(self.__symm__(y_) for y_ in ys)
        self.anti = sum(self.__anti__(y_)*i for y_,i in zip(ys,[1,-1,-1,1]))

        if check : self.check()

    def __anti__(self,y) :
        return ( self.N**2 - 4 ) / y[0,4] * ( self.csf * y[0,2] / y[2,4]
                                              - 2 * self.m22 * y[1,3]   )

    def __symm__(self,y) :
        m22,N,V,S,csf = [getattr(self,item) for item in ['m22','N','V','S','csf']]
        return ( csf * ( N*N*y[0,2]/y[0,4]/y[2,4]
                         - 0.5 * y[0,1]/y[0,4]/y[1,4]
                         - 0.5 * y[2,3]/y[2,4]/y[3,4])
                 -m22 * sum([ V - 0.5,
                              ( 1 + m22 / y[0,4] ) * ( 1 + S*V / y[0,4] ),
                              y[2,4]**2 / y[0,4] / y[1,4],
                              y[2,3] * ( V / y[0,4] +
                                         V / y[2,4] +
                                         ( 0.5 - V * y[3,4] / y[2,4] ) / S ),
                              2*y[0,2]/y[2,3]/y[1,4] * ( V * S * y[0,2] / y[1,4] +
                                                         y[0,2] - y[0,3] +
                                                         (y[3,4] - y[2,4] ) * y[1,4] / S +
                                                         V * y[2,4] * ( y[1,4] * y[2,4] / y[0,2] / S - 2 ) )
                              ])
                 )

    def check(self) :
        a = self.explicit(y,m22)
        aswap = self.explicit(reindex(y,(1,0,2,3,4)),m22)
        def almostEqual(a,b) : return abs(a-b) / (a+b) < 1e-11
        assert almostEqual(self.cf * self.symm,0.5*(a+aswap))
        assert almostEqual(self.cf * self.anti,0.5*(a-aswap))

    @staticmethod
    def explicit(y,M22) :
        N = 3.
        V = N*N-1
        S = M22 + y[0,1]
        m2 = 0.5*M22    # m2 == p0.p0 == p1.p1
        Y = 0.5*y       # Y  == [[pi.pj for pi in p] for pj in p]
        Delta = [ Y[i,k] / Y[j,4] - Y[k,4]*2./S for i,j,k in [(0,1,2),(0,1,3),(1,0,2),(1,0,3)]]

        sq = [m2] + [Y[i,j] for i,j in [(0,2),(1,2),(0,3),(1,3)]]
        f1 = (np.dot(sq,sq) + m2 * (Y[0,1] + Y[2,3])) / (2*S*Y[2,3])

        return sum([ f1 * 4*V*V/N * (Y[0,2]/Y[0,4]/Y[2,4]+
                                     Y[1,3]/Y[1,4]/Y[3,4]),
                     f1 * 4*V/N * sum([2*Y[0,3]/Y[0,4]/Y[3,4],
                                       2*Y[1,2]/Y[1,4]/Y[2,4],
                                       -Y[0,2]/Y[0,4]/Y[2,4],
                                       -Y[1,3]/Y[1,4]/Y[3,4],
                                       -Y[0,1]/Y[0,4]/Y[1,4],
                                       -Y[2,3]/Y[2,4]/Y[3,4],
                                       ]),
                     -(N*N-4)*V/N * M22/S/Y[2,3] * ( (Y[0,2]-Y[0,3])/Y[1,4] - (Y[1,2]-Y[1,3])/Y[0,4]),
                     4*V*V*m2/N * sum([ (Y[2,4]**2 + Y[3,4]**2)/(Y[2,4]*Y[3,4]*S*S),
                                        -0.5*sum(1./Y[i,4] for i in range(4))/S,
                                        -0.25*( 1./Y[0,4] + 1./Y[1,4] + m2/Y[0,4]**2 + m2/Y[1,4]**2 + 4./S ) / Y[2,3],
                                        -0.25*sum(Delta[i]**2 for i in range(4))/Y[2,3]**2
                                        ]),
                     -2*V/N * m2/S/Y[2,3] * sum([1,
                                                 2*Y[2,3]/S,
                                                 m2/Y[0,4]+m2/Y[1,4],
                                                 (Y[2,4]**2+Y[3,4]**2)/Y[0,4]/Y[1,4],
                                                 (Y[0,2]-Y[0,3]) * (Delta[0]-Delta[1]) / Y[2,3],
                                                 (Y[1,2]-Y[1,3]) * (Delta[2]-Delta[3]) / Y[2,3]
                                                 ])
                     ])
