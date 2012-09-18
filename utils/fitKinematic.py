import math, __init__ as utils,ROOT as r
try:
    import scipy.optimize as opt
    import scipy.linalg as LA
    import numpy as np
except: pass

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
                 massT = 172.0, massW = 80.4, lv = utils.LorentzV ) :

        def doInv() :
            eig,R_ = next( (np.minimum(1e6,np.maximum(1,e)),rot) for e,rot in [ LA.eigh(nuErr2) ] )
            self.invSig2nu = np.vstack( [np.vstack( [LA.inv(R_.dot(np.diag(eig).dot(R_.T))), [0,0]] ).T, [0,0,0]])
            self.nuinv = R_.T * np.vstack(2*[1./np.sqrt(eig)]).T
            self.binv = 1./bResolution
        doInv()

        self.LorentzV = lv
        self.Bm2, self.Wm2, self.Tm2 = b.M2(), massW**2, massT**2

        def doMatrices() :
            bXYZ = [b.x(),b.y(),b.z()]
            R_z = self.R(2, -mu.phi() )
            R_y = self.R(1,  0.5*math.pi - mu.theta() )
            R_x = next( self.R(0,-math.atan2(z,y)) for x,y,z in (R_y.dot( R_z.dot( bXYZ ) ),))
            self.R_T = np.dot( R_z.T, np.dot( R_y.T, R_x.T ) )
            self.Nu = np.outer([nuXY[0],nuXY[1],0],[0,0,1])
            self.B = np.outer( bXYZ, [0,0,1])

            self.D = np.diag([1,-1,0])[(1,0,2),]
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
            M = next( N.T + N for N in [ self.X.dot( self.D ) ] )
            eig = next( e.real for e in LA.eigvals(self.Unit.dot(M),overwrite_a=True) if not e.imag)
            Y = M - eig*self.Unit
            swapXY = abs(Y[0,0]) > abs(Y[1,1]) # choose denomenator further from zero, ignoring case where both are zero (perp. lines vert+horiz)
            if swapXY : Y = Y[(1,0,2),][:,(1,0,2)]
            c22 = self.cofactor(Y,(2,2))
            x0_,y0_ = (self.cofactor(Y,(0,2)) / c22 , self.cofactor(Y,(1,2)) / c22) if c22 else (None,None)
            sols = [ np.array( (x, y1_+x*S)[::(-1)**swapXY] +  (1,))
                     for S,y1_ in ( [(Y[0,1]/Y[1,1], (Y[1,2] + pm)/Y[1,1]) for pm in sqrt(-self.cofactor(Y,(0,0)))]    if c22>=0 else # parallel ||
                                    [(S, y0_-S*x0_) for S in [ (-Y[0,1]+pm)/Y[1,1] for pm in sqrt(-c22) ]] )                      # intersecting /|
                     for x in [ ( pm_ - S*y1_ ) / ( 1+S**2 ) for pm_ in sqrt( 1 + S**2 - y1_**2 ) ] ]
            return max(sorted(sols, key = chi2 ), [np.array([0,0,1])], key=len)

        self.solutions = solutions() if Z else [np.array([0,0,1])]
        return [deltaB * self.binv] + list(self.nuinv.dot( DeltaNu.dot(self.solutions[0])[:2]))

    def fit(self) :
        (self.deltaB,),_ = opt.leastsq(self.residuals,[0], ftol=5e-2, factor = 1, diag = [0.1], epsfcn=0.01)
        self.fitB = self.rawB*(1+self.deltaB)

        self.residuals([0])
        x,y,z = self.Ellipse.dot(self.solutions[0])
        self.rawNu = self.LorentzV(); self.rawNu.SetPxPyPzE(x,y,z,0); self.rawNu.SetM(0)

        res = self.residuals([self.deltaB])
        x,y,z = self.Ellipse.dot(self.solutions[0])
        self.fitNu = self.LorentzV(); self.fitNu.SetPxPyPzE(x,y,z,0); self.fitNu.SetM(0)

        return res

class ttbarDileptonSolver(object) :
    '''Find valid neutrino solutions under hypothesis 2x(t->bW->blv) using exact mass constraints.'''

    def __init__(self, bb_ = (None,None), mumu_ = (None,None), met = (None,None), massT2=172.5**2, massW2=80.4**2, lv = utils.LorentzV ) :
        S = np.array([[-1, 0,met[0]],
                      [ 0,-1,met[1]],
                      [ 0, 0, 1]])

        nus = utils.vessel()
        nus.ellipse  = tuple( self.Ellipse(b,mu,massT2,massW2) for b,mu in zip(bb_,mumu_) )
        nus.ellipseT = tuple( np.vstack([e[:2],[0,0,1]]) for e in nus.ellipse )
        nus.ellipseT_inv = tuple( np.linalg.inv(eT) for eT in nus.ellipseT )
        nus.nT_inv   = tuple( eT.dot(eT.T) for eT in nus.ellipseT )
        nus.nT = tuple( np.linalg.inv(nTi) for nTi in nus.nT_inv )

        nT_p = S.T.dot(nT[1]).dot(S)
        eig = next( e.real for e in np.linalg.eig( nus.nT_inv[0].dot(nT_p) ) if not e.imag )
        G = nT_p - eig * nus.nT[0]

        nus.vs = [ tuple( nus.ellipse[0].dot(nus.ellipseT_inv[0]).dot(nuT),
                          nus.ellipse[1].dot(nus.ellipseT_inv[1]).dot(S.dot(nuT)))
                   for nuT in self.intersections( G, nus.nT[0] ) ]

        self.nunu_s = [ (lv(),lv()) for _ in nus.vs ]
        for (nu,n_),(vu,v_) in zip(self.nunu_s,nus.vs) :
            nu.SetPxPyPzE(vu[0],vu[1],vu[2],0); nu.SetM(0)
            n_.SetPxPyPzE(v_[0],v_[1],v_[2],0); n_.SetM(0)

        self.bb_ = bb_
        self.mumu_ = mumu_
        self.met = met

    @staticmethod
    def cofactor(A,(i,j)) :
        a = A[not i:2 if i==2 else None:2 if i==1 else 1,
              not j:2 if j==2 else None:2 if j==1 else 1]
        return (-1)**(i+j) * (a[0,0]*a[1,1] - a[1,0]*a[0,1])

    @classmethod
    def intersections(cls, degenerate, ellipse ) :
        swapXY = degenerate[0,0] > degenerate[1,1]
        G = degenerate[(1,0,2),][:,(1,0,2)] if swapXY else degenerate
        E = ellipse[(1,0,2)][:,(1,0,2)] if swapXY else ellipse
        c22 = cls.cofactor(G,(2,2))

        def sqrt(x) : return [] if x<0 else [0] if x==0 else (lambda r: [-r,r])(math.sqrt(x))
        def parallel() : return [ (-G[0,1]/G[1,1], (pm - G[1,2])/G[1,1] ) for pm in sqrt(-cls.cofactor(G,(0,0)))]
        def intersecting() :
            x0,y0 = cls.cofactor(G,(0,2))/c22, cls.cofactor(G,(1,2))/c22
            return [ (m, y0-m*x0) for m in [-(G[0,1]+pm)/G[1,1] for pm in sqrt(-c22)]]
        def xintersect(slope,offset) :
            m = np.array([1,slope,0])
            b = np.array([0,offset,1])
            A = m.T.dot(E.dot(m))
            B = m.T.dot(E.dot(b)) / A
            C = b.T.dot(E.dot(b)) / A
            return [pm-B for pm in sqrt(B**2-C)]

        return [ np.array( (x, slope*x+offset)[::(-1)**swapXY] + (1,))
                 for slope,offset in ( parallel() if c22>=0 else intersecting() )
                 for x in xintersect(slope,offset) ]

    @staticmethod
    def R(axis, angle) :
        c,s = math.cos(angle),math.sin(angle)
        R = c * np.eye(3)
        for i in [-1,0,1] : R[ (axis-i)%3, (axis+i)%3 ] = i*s + (1 - i*i)
        return R

    @classmethod
    def R_T(cls,b,mu) :
        bXYZ = [b.x(),b.y(),b.z()]
        R_z = cls.R(2, -mu.phi() )
        R_y = cls.R(1,  0.5*math.pi - mu.theta() )
        R_x = next( cls.R(0,-math.atan2(z,y)) for x,y,z in (R_y.dot( R_z.dot( bXYZ ) ),))
        return np.dot( R_z.T, np.dot( R_y.T, R_x.T ) )

    @classmethod
    def Ellipse(cls,b,mu,massT2,massW2) :

        Q = 0.5 * (massT2 - massW2 - b.M2())
        c = r.TMath.VectorUtil.CosTheta(b,mu)
        s = math.sqrt(1-c*c)
        mu_p,b_p = mu.p(), b.p()

        x0 = -0.5 * massW2 / mu_p
        y0 = - (x0*c + Q/b_p) / s
        m = (b.E()/b_p -c) / s

        y1 = -x0 / m
        x1 = x0 + (y1-y0) / m
        Z2 = y1*(y1 - 2*y0) - x0*x0 - massW2

        Z = 0 if Z2<=0 else math.sqrt(Z2)
        R_T = cls.R_T(b,mu)

        return R_T.dot( np.array([[Z/m, 0, x1-mu_p],
                                  [ Z,  0,   y1   ],
                                  [ 0,  Z,   0    ]]) )
