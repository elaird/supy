import math, __init__ as utils,ROOT as r
try:
    import scipy.optimize as opt
    import scipy.linalg as LA
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
        a = A[not i:2 if i==2 else None:2 if i==1 else 1,
              not j:2 if j==2 else None:2 if j==1 else 1]
        return (-1)**(i+j) * (a[0,0]*a[1,1] - a[1,0]*a[0,1])

    def __init__(self, b, bResolution, mu, nuXY, nuErr2,
                 massT = 172.0, massW = 80.4) :

        def doInv() :
            eig,R_ = next( ((np.maximum(1,e),rot) for e,rot in [ LA.eigh(nuErr2) ]) )
            self.invSig2nu = np.vstack( [np.vstack( [LA.inv(R_.dot(np.diag(eig).dot(R_.T))), [0,0]] ).T, [0,0,0]])
            self.nuinv = R_.T * np.vstack(2*[1./np.sqrt(eig)]).T
            self.binv = 1./bResolution
        doInv()

        self.Bm2, self.Wm2, self.Tm2 = b.M2(), massW**2, massT**2

        def doMatrices() :
            bXYZ = [b.x(),b.y(),b.z()]
            R_z = self.R(2, -mu.phi() )
            R_y = self.R(1,  0.5*math.pi - mu.theta() )
            R_x = next( self.R(0,-math.atan2(z,y)) for x,y,z in (R_y.dot( R_z.dot( bXYZ ) ),))
            self.R_T = np.dot( R_z.T, np.dot( R_y.T, R_x.T ) )
            self.Nu = np.outer([nuXY[0],nuXY[1],0],[0,0,1])
            self.B = np.outer( bXYZ, [0,0,1])

            self.D = np.reshape([0,-1,0,1]+5*[0],(3,3))
            self.Unit = np.diag([1,1,-1])
        doMatrices()

        def doConstants() :
            c = r.Math.VectorUtil.CosTheta(mu,b)
            s = math.sqrt(1-c*c)
            b_p, b_e = b.P(), b.E()

            self.mu_p = mu.P()
            self.x0 = -self.Wm2 / (2*self.mu_p)
            self.denom = b_e - c*b_p
            self.y1 = - s*self.x0*b_p / self.denom
            self.x1_0 = self.x0*b_e / self.denom - self.y1**2/self.x0
            self.Z2_0 = self.x0**2 - self.Wm2 - self.y1**2
        doConstants()

        self.rawB = b
        self.mu = mu

        self.residualsBSLWT = self.fit()
        def doFinish() :
            _,self.fitW,self.fitT = np.cumsum([mu,self.fitNu,self.fitB])
            _,self.rawW,self.rawT = np.cumsum([mu,self.rawNu,self.rawB])
            self.residualsBSLWT += [(massW - self.fitW.M())/0.01, (massT - self.fitT.M())/0.01 ]
            self.chi2 = np.dot( self.residualsBSLWT, self.residualsBSLWT )
            self.bound = True
        doFinish()

    def residuals(self,params) :
        deltaB, = params
        x1 = self.x1_0 + 0.5*(self.Tm2 - self.Wm2 - self.Bm2*(1+deltaB)**2) / (self.denom*(1+deltaB))
        Z2 = self.Z2_0 - 2*self.x0*x1
        Z = 0 if Z2 < 0 else math.sqrt( Z2 )
        self.Ellipse = self.R_T.dot( [[-Z*self.y1/self.x0,  0,  x1 - self.mu_p ],
                                      [ Z,                  0,         self.y1 ],
                                      [ 0,                  Z,               0 ]] )
        DeltaNu = self.Nu - deltaB*self.B - self.Ellipse
        self.X = DeltaNu.T.dot( self.invSig2nu.dot( DeltaNu ) )

        def chi2(t) : return t.T.dot(self.X.dot(t))
        def sqrt(s) : return [] if s<=0 else (lambda r: [-r,r])(math.sqrt(s))
        def solutions() :
            sols = []
            M = next( N.T + N for N in [ self.X.dot( self.D ) ] )
            eig = next( e.real for e in LA.eigvals(self.Unit.dot(M),overwrite_a=True) if not e.imag)
            Y = M - eig*self.Unit
            c22 = self.cofactor(Y,(2,2))
            x0_,y0_ = self.cofactor(Y,(0,2)) / c22 , self.cofactor(Y,(1,2)) / c22
            for S in [ (-Y[0,1]+pm)/Y[1,1] for pm in sqrt(-c22) ] :
                y1_ = y0_ - S*x0_
                x_ = [ ( pm_ - S*y1_ ) / ( 1+S**2 ) for pm_ in sqrt( 1 + S**2 - y1_**2 ) ]
                sols += [np.array([ x, y1_+x*S, 1]) for x in x_]
            return sorted(sols, key = chi2 )

        self.solutions = solutions() if Z else [np.array([0,0,1])]
        return [deltaB * self.binv] + list(self.nuinv.dot( DeltaNu.dot(self.solutions[0])[:2]))

    def fit(self) :
        res = self.residuals([0])
        x,y,z = self.Ellipse.dot(self.solutions[0])
        self.rawNu = utils.LorentzV(); self.rawNu.SetPxPyPzE(x,y,z,0); self.rawNu.SetM(0)
        
        if not (self.solutions[0][0] or self.solutions[0][1]) :
            self.deltaB = 0
            self.fitNu = self.rawNu
        else:
            (self.deltaB,),_ = opt.leastsq(self.residuals,[0], ftol=5e-2, factor = 1, diag = [0.1], epsfcn=0.01)
            res = self.residuals([self.deltaB])
            x,y,z = self.Ellipse.dot(self.solutions[0])
            self.fitNu = utils.LorentzV(); self.fitNu.SetPxPyPzE(x,y,z,0); self.fitNu.SetM(0)

        self.fitB = self.rawB*(1+self.deltaB)
        return res

