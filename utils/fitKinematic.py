import math, __init__ as utils,ROOT as r
try:
    import scipy.optimize as opt
except: pass
try:
    import numpy as np
except:
    pass

widthTop = 13.1/2
###########################
class leastsqLeptonicTop(object) :
    '''Fit jet, lepton, and missing energy to the hypothesis t-->blv.'''

    def __init__(self, b, bResolution, mu, nuXY, nuErr, 
                 massT = 172.0, widthT = widthTop, massW = 80.4, zPlus = True ) :

        for key,val in zip(['',                     'XY',   'Z',   'E',      'T2',    'T',   'Phi'],
                           [mu,np.array([mu.x(),mu.y()]),mu.z(),mu.e(),mu.Perp2(),mu.Pt(),mu.Phi()]) : setattr(self,"mu"+key,val)

        for key,val in zip(['massW2','massT','invT','bound','sign','rawB','nuXY','fitNu'],
                           [massW**2,massT,1./widthT,False,[-1,1][zPlus],b,nuXY,utils.LorentzV()]) : setattr(self,key,val)

        self.bXY = np.array([b.x(),b.y()])

        eig,self.Einv = np.linalg.eig(nuErr)
        self.E = self.Einv.T
        self.inv = 1./np.append([bResolution],np.sqrt(np.maximum(1,eig)))

        self.setFittedNu(nuXY)
        _,self.rawW,self.rawT = np.cumsum([mu,self.fitNu,self.rawB])
        
        self.residualsBSLT = self.fit()
        self.chi2 = self.residualsBSLT.dot(self.residualsBSLT)
        _,self.fitW,self.fitT = np.cumsum([mu,self.fitNu,self.fitB])

    def setFittedNu(self,nuXY) :
        P = self.massW2 + 2* nuXY.dot(self.muXY)
        self.discriminant = 1 - 4 * self.muT2 * nuXY.dot(nuXY) / P**2
        nuZ = 0.5 * P / self.muT2 * (self.muZ + self.sign*self.muE*math.sqrt(max(0,self.discriminant)))
        self.fitNu.SetPxPyPzE(nuXY[0],nuXY[1],nuZ,0)
        self.fitNu.SetM(0)

    def setBoundaryFittedNu(self,phi) :
        nuT = 0.5 * self.massW2 / (self.muT * (1 - math.cos(self.muPhi-phi)))
        self.setFittedNu( nuT * np.array([math.cos(phi), math.sin(phi)]) )
        
    def fit(self) :
        def lepResiduals(d) : # deltaB, dS, dL
            self.fitB = self.rawB * (1+d[0])
            self.setFittedNu(self.nuXY - d[0]*self.bXY + self.Einv.dot(d[1:]))
            return np.append( self.inv * d,
                              self.invT * (self.massT - (self.mu + self.fitNu + self.fitB ).M()) )
        
        def lepBoundResiduals(x) : # deltaB, phi
            self.fitB = self.rawB * (1+x[0])
            self.setBoundaryFittedNu(x[1])
            nuXY = [self.fitNu.x(),self.fitNu.y()]
            dS,dL = self.E.dot(nuXY - self.nuXY + x[0]*self.bXY)
            return np.append( self.inv * [x[0],dS,dL],
                              self.invT * (self.massT - (self.mu + self.fitNu + self.fitB).M()) )

        deltas,_ = opt.leastsq(lepResiduals, 3*[0], epsfcn=0.01, ftol=1e-2, factor = 1, diag = [0.1,1,1])
        if 0 <= self.discriminant : return lepResiduals(deltas)
        self.bound = True
        best,_ = opt.leastsq(lepBoundResiduals, [0, math.atan2(self.nuXY[1],self.nuXY[0])], epsfcn=0.01, ftol=1e-3)
        return lepBoundResiduals(best)
        
###########################
class leastsqHadronicTop(object) :
    '''Fit three jets to the hypothesis t-->bqq.

    Index 2 is the b-jet.
    Resolutions are expected in units of sigma(pT)/pT.'''

    def __init__(self, jetP4s, jetResolutions, massT = 172.0, widthT = widthTop, massW = 80.4, widthW = 2.085/2 ) :
        for key,val in zip(['massT','massW','invT','invW'],
                           [massT,massW,1./widthT,1./widthW]) : setattr(self,key,val)
        
        self.rawJ = jetP4s;
        self.invJ = 1./np.array(jetResolutions)
        self.fit()
        _,self.fitW,self.fitT = np.cumsum(self.fitJ)
        _,self.rawW,self.rawT = np.cumsum(self.rawJ)

    def fit(self) :
        def hadResiduals(d) :
            _,W,T = np.cumsum(self.rawJ * (1+d))
            return np.append((d*self.invJ), [ (self.massW-W.M())*self.invW,
                                              (self.massT-T.M())*self.invT])

        self.deltaJ,_ = opt.leastsq(hadResiduals,3*[0],epsfcn=0.01, ftol=1e-3)
        self.fitJ = self.rawJ * (1+self.deltaJ)
        self.residualsPQBWT = hadResiduals(self.deltaJ)
        self.chi2 = self.residualsPQBWT.dot(self.residualsPQBWT)
###########################
class leastsqHadronicTop2(object) :
    '''Fit three jets to the hypothesis t-->bqq.

    Index 2 is the b-jet.
    Resolutions are expected in units of sigma(pT)/pT.'''

    def __init__(self, jetP4s, jetResolutions, massT = 172.0, massW = 80.4) :
        self.Wm2,self.Tm2 = massW**2,massT**2
        self.rawJ = jetP4s;
        self.invJ = 1./np.array(jetResolutions)
        self.fit()
        _,self.fitW,self.fitT = np.cumsum(self.fitJ)
        _,self.rawW,self.rawT = np.cumsum(self.rawJ)

    @staticmethod
    def delta(P, givenQ, motherMass2) :
        p_m2 = P.M2()
        dot = P.E() * givenQ.E() - P.P() * givenQ.P() * r.Math.VectorUtil.CosTheta(P,givenQ) # PtEtaPhiM coordinate LVs fail to implement ::Dot()
        dmass = motherMass2 - givenQ.M2()
        if not p_m2 : return  0.5 * dmass / dot - 1
        disc = math.sqrt(dot**2 + p_m2*dmass)
        return  min((+disc-dot-p_m2)/p_m2,
                    (-disc-dot-p_m2)/p_m2, key = abs )

    def fit(self) :
        def hadResiduals(d0) :
            j0 = self.rawJ[0]*(1+d0[0])
            d1 = self.delta(self.rawJ[1], j0,                       self.Wm2)
            d2 = self.delta(self.rawJ[2], j0 + self.rawJ[1]*(1+d1), self.Tm2)
            self.deltaJ = np.array( [d0[0], d1, d2])
            return self.invJ * self.deltaJ

        opt.leastsq(hadResiduals,[0],epsfcn=0.01, ftol=1e-3, factor = 10)
        self.residualsPQBWT = np.append( hadResiduals(self.deltaJ), [0.,0.] )
        self.chi2 = self.residualsPQBWT.dot(self.residualsPQBWT)
        self.fitJ = self.rawJ * (1+self.deltaJ)
###########################


class leastsqLeptonicTop2(object) :
    '''Fit jet, lepton, and missing energy to the hypothesis t-->blv with exact mass constraints.

    A_munu = np.array([[  0, 0,               x0],
                       [  0, 1,                0],
                       [ x0, 0, Wm2 - x0**2]])
    R = np.array([[c, -s, 0],
                  [s,  c, 0],
                  [0,  0, 1]])
    A_b = R.dot(np.array([[  b_m2/b_e2, 0,          -Q*b_p/b_e2],
                          [          0, 1,                    0],
                          [-Q*b_p/b_e2, 0, Wm2 - Q**2/b_e2]])).dot(R.transpose())
    '''

    @staticmethod
    def R(axis, angle) :
        c,s = math.cos(angle),math.sin(angle)
        R = c * np.eye(3)
        for i in [-1,0,1] : R[ (axis-i)%3, (axis+i)%3 ] = i*s + (1 - i*i)
        return R

    @staticmethod
    def cofactor(A,(i,j)) :
        return (-1)**(i+j) * np.linalg.det(
            A[np.array([_ for _ in range(A.shape[0]) if _!=i])[:,np.newaxis],
              np.array([_ for _ in range(A.shape[1]) if _!=j])] )

    def __init__(self, b, bResolution, mu, nuXY, nuErr2, 
                 massT = 172.0, massW = 80.4) :

        nuErr2 = next( rot.dot(np.diag(np.maximum(1,E)).dot(rot.T)) for E,rot in [np.linalg.eig(nuErr2)])

        self.E,self.inv = next( (Rinv.T,
                                  1./np.append([bResolution],np.sqrt(np.maximum(1,eig)))) 
                                 for eig,Rinv in [np.linalg.eig(nuErr2)])

        self.invSig2nu = np.vstack( [np.vstack( [np.linalg.inv(nuErr2), [0,0]] ).T, [0,0,0]])

        self.Bm2, self.Wm2, self.Tm2 = b.M2(), massW**2, massT**2

        R_z = self.R(2, -mu.phi() )
        R_y = self.R(1,  0.5*math.pi - mu.theta() )
        R_x = next( self.R(0,-math.atan2(z,y)) for x,y,z in (R_y.dot( R_z.dot( [b.x(),b.y(),b.z()]) ),))
        self.R_T = np.dot( R_z.T, np.dot( R_y.T, R_x.T ) )

        c = r.Math.VectorUtil.CosTheta(mu,b)
        s = math.sqrt(1-c*c)
        b_p, b_e = b.P(), b.E()

        self.mu_p = mu.P()
        self.x0 = -self.Wm2 / (2*self.mu_p)
        self.denom = b_e - c*b_p
        self.y1 = - s*self.x0*b_p / self.denom
        self.x1_0 = self.x0*b_e / self.denom - self.y1**2/self.x0

        self.nuXY = nuXY
        self.rawB = b
        self.bXY = np.array([b.x(), b.y()])
        self.mu = mu
        self.Z2_0 = self.x0**2 - self.Wm2 - self.y1**2

        self.residualsBSLT = np.append( self.fit(), [0])
        self.chi2 = np.dot( self.residualsBSLT, self.residualsBSLT )
        _,self.fitW,self.fitT = np.cumsum([mu,self.fitNu,self.fitB])
        _,self.rawW,self.rawT = np.cumsum([mu,self.rawNu,self.rawB])
        self.bound = True

    def residuals(self,params) :
        def nuResiduals(deltaB) : return self.E.dot( self.nuXY - deltaB*self.bXY - self.nu[:2] )
        deltaB,tau = params
        x1 = self.x1_0 + 0.5*(self.Tm2 - self.Wm2 - self.Bm2*(1+deltaB)**2) / (self.denom*(1+deltaB))
        Z2 = self.Z2_0 - 2*self.x0*x1
        Z = 0 if Z2 < 0 else math.sqrt( Z2 )

        S = self.invSig2nu
        E = np.dot( self.R_T, [[-Z*self.y1/self.x0,  0,  x1 - self.mu_p ],
                               [ Z,                  0,         self.y1 ],
                               [ 0,                  Z,               0 ]] )
        V = [[ 0, 0, self.nuXY[0]],
             [ 0, 0, self.nuXY[1]],
             [ 0, 0, 0]]

        self.M = (V-E).T.dot( self.invSig2nu.dot( V-E ) )
        P = next( N.T + N for N in [ self.M.dot( [[ 0,-1, 0 ],
                                                  [ 1, 0, 0 ],
                                                  [ 0, 0, 0 ]] ) ] )
        U = np.diag([1,1,-1])
        eig = next( e.real for e in next(es for es,_ in [np.linalg.eig(U.dot(P))]) if not e.imag)
        D = P - eig*U

        self.solutions = []
        if Z :
            m22 = self.cofactor(D,(2,2))
            x0_,y0_ = np.array([self.cofactor(D,(0,2)),self.cofactor(D,(1,2))]) / m22
            slopes = [ (-D[0,1]+i*math.sqrt(-m22))/D[1,1] for i in [-1,1]]
            for s in slopes :
                x0s = x0_*s
                b = s*(x0s-y0_)
                disc = b**2 - (1+s*s)*(y0_**2 + x0s**2 - 2*y0_*x0s-1)
                if disc<=0 : continue
                x_ = [(s*(x0s-y0_) + i*math.sqrt(disc))/(1+s*s) for i in [-1,1]]
                y_ = [(x-x0_)*s + y0_ for x in x_]
                self.solutions += [np.array([x,y,1]) for x,y in zip(x_,y_)]
            self.solutions.sort(key = lambda x : np.dot( x.T, self.M.dot(x) ) )

        self.nu = E.dot([math.cos(tau),
                         math.sin(tau),
                         1])
        if Z2 < 0 :
            return self.inv * np.append([deltaB + (0.01 if deltaB>0 else -0.01)], nuResiduals(deltaB)) * (1-Z2)**3
        return self.inv * np.append([deltaB],nuResiduals(deltaB))

    def fit(self) :
        tau_init = min([(t, self.residuals([0,t])) for t in np.arange(0,1.8*math.pi,math.pi/3)], key = lambda x: x[1].dot(x[1]))[0]
        params,_ = opt.leastsq(self.residuals,[0,tau_init], ftol=1e-2, factor = 1, diag = [0.1,0.2], epsfcn=0.01)
        self.deltaB,self.tau = params
        self.fitB = self.rawB*(1+self.deltaB)
        res = self.residuals(params)
        x,y,z = self.nu
        self.fitNu = utils.LorentzV(); self.fitNu.SetPxPyPzE(x,y,z,0); self.fitNu.SetM(0)
        self.rawNu = utils.LorentzV(); self.rawNu.SetPxPyPzE(self.nuXY[0],self.nuXY[1],0,0); self.rawNu.SetM(0)

        print
        if self.solutions :
            for x in [np.array([math.cos(self.tau),math.sin(self.tau),1])]+self.solutions :
                print x.T.dot( self.M.dot(x) )
        return res

    def signExpectation(self,  had, hadIsTop = False, nSamples = 16, qDirFunc = lambda H,L : 0) :
        nu = utils.LorentzV()
        samples = []
        had_y = had.Rapidity()
        bmu = self.mu + self.fitB

        for tau in np.arange(self.tau, self.tau + 2*math.pi, 2*math.pi/nSamples)[::-1] :
            res = self.residuals([self.deltaB,tau])
            chi2 = np.dot(res,res)
            x,y,z = self.nu;
            nu.SetPxPyPzE(x,y,z,0); nu.SetM(0)
            lep = bmu + nu
            samples.append( (math.exp(-0.5*chi2),
                             qDirFunc(had,lep) * (-1)**hadIsTop * ( 1 if lep.Rapidity() > had_y else -1 ) ) )

        xw = sum(p*sdy for p,sdy in samples)
        w = sum(p for p,sdy in samples)
        return xw / w if w else 0


class leastsqCombinedTop(object) :
    '''Fit four jets, lepton, MET, and gluons to the hypothesis xtt-->xbqqblv using the three parameters [delta0,delta3,tau].

    Indices [0,1] are the light jets.
    Index 2 is the hadronic b-jet.
    Index 3 is the leptonic b-jet.
    Resolutions are expected in units of sigma(pT)/pT.'''

    @staticmethod
    def R(axis, angle) :
        c,s = math.cos(angle),math.sin(angle)
        R = c * np.eye(3)
        for i in [-1,0,1] : R[ (axis-i)%3, (axis+i)%3 ] = i*s + (1 - i*i)
        return R

    def __init__(self, jetP4s, jetResolutions, mu, nuXY, nuErr2,
                 gluons = [], massT = 172.0, massW = 80.4) :
        b = jetP4s[3]
        self.Wm2,self.Tm2 = massW**2,massT**2
        self.Bm2, self.Wm2, self.Tm2 = b.M2(), massW**2, massT**2
        self.rawJ = jetP4s;
        self.gluons = gluons

        self.R_nuE,self.inv = next( (Rinv.T,
                                     1./np.append( jetResolutions ,np.sqrt(np.maximum(1,eig)))) 
                                    for eig,Rinv in [np.linalg.eig(nuErr2)])

        R_z = self.R(2, -mu.phi() )
        R_y = self.R(1,  0.5*math.pi - mu.theta() )
        R_x = next( self.R(0,-math.atan2(z,y)) for x,y,z in (R_y.dot( R_z.dot( [b.x(),b.y(),b.z()]) ),))
        self.R_T = np.dot( R_z.T, np.dot( R_y.T, R_x.T ) )

        c = r.Math.VectorUtil.CosTheta(mu,b)
        s = math.sqrt(1-c*c)
        b_p, b_e = b.P(), b.E()

        self.mu_p = mu.P()
        self.x0 = -self.Wm2 / (2*self.mu_p)
        self.denom = b_e - c*b_p
        self.y1 = - s*self.x0*b_p / self.denom
        self.x1_0 = self.x0*b_e / self.denom - self.y1**2/self.x0

        self.jetXY = np.array([[j.x(), j.y()] for j in self.rawJ])
        self.mu = mu
        self.nuXY = nuXY
        self.rawNu = utils.LorentzV(); self.rawNu.SetPxPyPzE(self.nuXY[0],self.nuXY[1],0,0); self.rawNu.SetM(0)
        self.fitNu = utils.LorentzV();
        self.residuals = self.fit()
        self.chi2 = np.dot( self.residuals, self.residuals )

        _,self.fitHadW,self.fitHadT = np.cumsum(self.fitJ[:3])
        _,self.rawHadW,self.rawHadT = np.cumsum(self.rawJ[:3])
        _,self.fitLepW,self.fitLepT = np.cumsum([mu,self.fitNu,self.fitJ[3]])
        _,self.rawLepW,self.rawLepT = np.cumsum([mu,self.rawNu,self.rawJ[3]])

    @staticmethod
    def delta(P, givenQ, motherMass2) :
        p_m2 = P.M2()
        dot = P.E() * givenQ.E() - P.P() * givenQ.P() * r.Math.VectorUtil.CosTheta(P,givenQ) # PtEtaPhiM coordinate LVs fail to implement ::Dot()
        dmass = motherMass2 - givenQ.M2()
        if not p_m2 : return  0.5 * dmass / dot - 1
        disc = math.sqrt(dot**2 - p_m2*(2*dot + p_m2 - dmass))
        return  min((-dot+disc)/p_m2,
                    (-dot-disc)/p_m2, key = abs )

    def nuDeltaXY(self) : return self.R_nuE.dot( self.nuXY - np.dot(self.deltaJ, self.jetXY) - self.nu[:2] )

    def fit(self) :

        Z2_0 = self.x0**2 - self.Wm2 - self.y1**2

        def residuals(pars) :
            d0,deltaB,tau = pars

            j0 = self.rawJ[0]*(1+d0)
            d1 = self.delta(self.rawJ[1], j0,                       self.Wm2)
            d2 = self.delta(self.rawJ[2], j0 + self.rawJ[1]*(1+d1), self.Tm2)
            self.deltaJ = np.array( [d0, d1, d2, deltaB])

            x1 = self.x1_0 + 0.5*(self.Tm2 - self.Wm2 - self.Bm2*(1+deltaB)**2) / (self.denom*(1+deltaB))
            Z2 = Z2_0 - 2*self.x0*x1
            if Z2 < 0 :
                Zpenalty = math.sqrt(-Z2)
                self.nu = self.R_T.dot( [x1-self.mu_p, self.y1, 0] )
            else :
                Zpenalty = 0
                Z = math.sqrt( Z2 )
                c = math.cos(tau)
                self.nu = self.R_T.dot( [ x1 - self.mu_p - Z*c*self.y1/self.x0,
                                          self.y1 + Z*c,
                                          Z*math.sin(tau) ])

            x,y,z = self.nu
            self.fitNu.SetPxPyPzE(x,y,z,0); self.fitNu.SetM(0)
            self.fitJ = self.rawJ * (1+self.deltaJ)
            lepT = np.sum([self.fitNu,self.mu,self.fitJ[3]])
            hadT = np.sum(self.fitJ[:3])

            self.ttx = sum(self.gluons, lepT + hadT)
            sqrtSumPX = math.sqrt(sum([abs(g.x()) for g in self.gluons], abs(lepT.x()) + abs(hadT.x())))
            sqrtSumPY = math.sqrt(sum([abs(g.y()) for g in self.gluons], abs(lepT.y()) + abs(hadT.y())))

            return np.append( self.inv * np.append( self.deltaJ, self.nuDeltaXY() ),
                              [self.ttx.x()/sqrtSumPX,
                               self.ttx.y()/sqrtSumPY,
                               min( (self.ttx.M() - abs(self.ttx.z())) / math.sqrt(self.ttx.M()) , 0),
                               Zpenalty])


        tau_init = min([(t, residuals([0,0,t])) for t in np.arange(0,1.9*math.pi,math.pi/4)], key = lambda x: x[1].dot(x[1]))[0]
        params,_ = opt.leastsq(residuals,[0,0,tau_init], ftol=1e-3, factor = 1, diag = [10,0.1,0.2], epsfcn=0.01)
        return residuals(params)
