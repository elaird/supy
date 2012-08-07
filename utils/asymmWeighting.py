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


def A(y,M22) :
    '''Formula 10 from "Explicit formulae for heavy flavour production", R.K. Ellis and J.C. Sexton.

    Q(-p1) + Qbar(-p2) ==> q(p3) + qbar(p4) + g(p5)
    '''
    m2 = M22/2. # == p1.p1 == p2.p2
    Y = y/2.    # == [[pi.pj for pi in p] for pj in p]
    S = M22 + y[0,1] # == (p1+p2)^2
    Delta = [ Y[i,k] / Y[j,4] - Y[k,4]*2./S for i,j,k in [(0,1,2),(0,1,3),(1,0,2),(1,0,3)]]
    N = float(3)
    V = N*N-1

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

def common_factor(y,m22) :
    N = float(3)
    return (N*N-1)/(N*(m22+y[0,1])*y[2,3])

def common_subfactor(y,m22) :
    sq = [m22]+[y[i,j] for i,j in [(0,2),(1,2),(0,3),(1,3)]]
    return m22*(y[0,1]+y[2,3]) + np.dot(sq,sq)

def A__(y,m22) :
    N = float(3)
    cf = common_factor(y,m22)
    csf = common_subfactor(y,m22)
    return cf * (N*N-4) / y[0,4] * ( csf * y[0,2] / y[2,4]
                                     - 2 * m22 * y[1,3]   )
def _A_(y,m22) :
    N=float(3)
    V = N*N-1
    cf = common_factor(y,m22)
    csf = common_subfactor(y,m22)
    return cf * sum([csf * (N*N*y[0,2]/y[0,4]/y[2,4] - 0.5 * (y[0,1]/y[0,4]/y[1,4] + y[2,3]/y[2,4]/y[3,4])),
                     -m22 * sum([V-0.5,
                                 (1+m22/y[0,4])*(1+(m22+y[0,1])*V/y[0,4]),
                                 y[2,3] * sum([V/y[0,4],
                                               V/y[2,4],
                                               (0.5-V*y[3,4]/y[2,4])/(m22+y[0,1])]),
                                 y[2,4]**2/y[0,4]/y[1,4],
                                 2*y[0,2]/y[2,3]/y[1,4] * sum([ y[0,2]/y[1,4] * V * (m22+y[0,1]),
                                                                y[0,2] - y[0,3],
                                                                - (y[2,4]-y[3,4])*y[1,4]/(m22+y[0,1]),
                                                                V*y[2,4]*(y[1,4]*y[2,4]/y[0,2]/(m22+y[0,1]) - 2)
                                                                ])
                                 ]),
                     ])


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

        a = A(Y,self.M22)
        aswap = A(reindex(Y,(1,0,2,3,4)),self.M22)
        _a_ = sum(_A_( reindex(Y,I),self.M22) for I in [(0,1,2,3,4),(1,0,2,3,4),(0,1,3,2,4),(1,0,3,2,4)] )
        a__ = sum(i*A__( reindex(Y,I),self.M22) for i,I in zip([1,-1,-1,1],
                                                               [(0,1,2,3,4),(1,0,2,3,4),(0,1,3,2,4),(1,0,3,2,4)]))
        print "symm", _a_ - (0.5*(a+aswap))
        print "anti", a__ - (0.5*(a-aswap))
        print

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
