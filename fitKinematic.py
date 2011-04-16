import numpy,math,utils

class hadronicTop(object) :
    '''Fit three jets to the hypothesis t -> bqq.

    Indices 0 is the b-jet.
    Resolutions should be given in units of sigma(pT)/pT.'''

    def chi2(self, key = None) :
        if key==None : return sum( [self.chi2(key) for key in ["J","W","T"]])
        elif key=="J": return sum([ d*d*r for d,r in zip( self.J.delta, self.J.invRes2 ) ])
        elif key=="W": return self.W.invWidth2 * ( self.W.mass - (self.J.fitted[1] + self.J.fitted[2]).M() )**2
        elif key=="T": return self.T.invWidth2 * ( self.T.mass - sum( self.J.fitted, utils.LorentzV()).M() )**2

    def __init__(self, jetP4s, jetResolutions, massT = 172.5, widthT = 6.0, massW = 80.1, widthW = 1.0 ) :
        assert len(jetP4s) == 3 == len(jetResolutions), "Please specify 3 and only 3 jets."
        J,W,T = tuple( utils.vessel() for i in range(3) )

        J.raw = jetP4s
        J.invRes2 = [ r**(-2) for r in jetResolutions ]
        m2 = [(J.raw[i]+J.raw[j]).M2() for i,j in [tuple(set([0,1,2])-set([k])) for k in [0,1,2]]]

        T.rawMass2 = sum( jetP4s, utils.LorentzV()).M2()
        T.mass = massT ;   T.invWidth2 = widthT**(-2) ;   T.R = massT / math.sqrt(T.rawMass2) ; T.L = 0.5 * T.invWidth2 / T.rawMass2
        W.mass = massW ;   W.invWidth2 = widthW**(-2) ;   W.R = massW / math.sqrt(m2[0])      ; W.Lambda =  W.invWidth2 * m2[0]     

        for item in ["J","T","W","m2"] : setattr(self,item,eval(item))
        J.delta = numpy.linalg.solve( self.matrix(), -self.constants() )
        J.fitted = [ r * (1+d) for r,d in zip(J.raw,J.delta) ]

    def matrix(self) :
        m = []
        m.append([     self.element(0,i) for i in range(3)       ])
        m.append([ m[0][1], self.element(1,1), self.element(1,2) ])
        m.append([ m[0][2],            m[1,2], self.element(2,2) ])
        return numpy.array(m)

    def constants(self) : return numpy.array([self.constant(i) for i in range(3)])
    def constant(self, i, key = None):
        if key==None : return sum( [self.constant(i,key) for key in ["W","T"]] )
        elif key=="W": return ( 1 - self.W.R ) * self.W.Lambda
        elif key=="T": return ( 1 - self.T.R ) * self.T.invWidth2 * (sum(self.m2)-self.m2[i])

    def element(self,i,j, key = None) :
        if key==None : return sum( [self.element(i,j,key) for key in ["J","W","T"]] )
        elif key=="J": return [ 0, 2*self.J.invRes2[i] ][i==j]
        elif key=="W": return self.W.Lambda * [ 1-0.5*self.W.R,  0.5*self.W.R ][i==j] if i and j else 0
        elif key=="T":
            T = self.T
            sumM2 = sum(self.m2)
            m2_i = sumM2 - self.m2[i]
            m2_j = sumM2 - self.m2[j]
            term2 = [(1-T.R) * T.invWidth2 * (sumM2 - self.m2[i] - self.m2[j] ) , 0 ][i==j]
            return term2  +  m2_i * m2_j * T.L * T.R
