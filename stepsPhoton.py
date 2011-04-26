import ROOT as r
import math
from analysisStep import analysisStep
#####################################
class photonPtSelector(analysisStep) :

    def __init__(self,cs,photonPtThreshold,photonIndex):
        self.photonIndex = photonIndex
        self.photonPtThreshold = photonPtThreshold
        self.cs = cs
        self.indicesName = "%sIndices%s" % self.cs
        self.p4sName = "%sP4%s" % self.cs
        self.moreName = "%s%s; pT[index[%d]]>=%.1f GeV" % (self.cs[0], self.cs[1], photonIndex, photonPtThreshold)

    def select (self,eventVars) :
        indices = eventVars[self.indicesName]
        if len(indices) <= self.photonIndex : return False
        p4s = eventVars[self.p4sName]
        return self.photonPtThreshold <= p4s.at(indices[self.photonIndex]).pt()
#####################################
class photonSelector(analysisStep) :

    def __init__(self, cs, jetCs, referenceThresholds, index) :
        for item in ["index", "cs", "jetCs"] :
            setattr(self, item, eval(item))

        self.fraction = referenceThresholds["photonPt"]/referenceThresholds["ht"]
        self.indicesName = "%sIndices%s" % self.cs
        self.p4sName = "%sP4%s" % self.cs
        self.moreName = "%s%s; pT[index[%d]]>=%4.3f * %sHtBin%s" % (self.cs[0], self.cs[1], index, self.fraction, self.jetCs[0], self.jetCs[1])

    def select (self,eventVars) :
        indices = eventVars[self.indicesName]
        if len(indices) <= self.index : return False
        value = eventVars[self.p4sName].at(indices[self.index]).pt()
        return self.fraction*eventVars["%sHtBin%s"%self.jetCs] <= value
#####################################
class photonEtaSelector(analysisStep) :

    def __init__(self,cs,photonEtaThreshold,photonIndex):
        self.photonIndex = photonIndex
        self.photonEtaThreshold = photonEtaThreshold
        self.cs = cs
        self.indicesName = "%sIndices%s" % self.cs
        self.p4sName = "%sP4%s" % self.cs
        self.moreName = "%s%s; |eta[index[%d]]|<=%.2f" % (self.cs[0], self.cs[1], photonIndex, photonEtaThreshold)

    def select (self,eventVars) :
        indices = eventVars[self.indicesName]
        if len(indices) <= self.photonIndex : return False
        p4s = eventVars[self.p4sName]
        return self.photonEtaThreshold > abs(p4s.at(indices[self.photonIndex]).eta())
#####################################
class photonSelectionHistogrammer(analysisStep) :
    
    def __init__(self, nametag="", matchDeltaRMax = None, prompt = False) :
        self.deltaRMax = matchDeltaRMax
        self.nametag = nametag
        self.prompt = prompt

        #            (eta, pt)
        self.bins2 = (40, 80 );  self.bins3 = tuple(list(self.bins2)+[self.bins2[1]])
        self.low2 =  (0,  0  );  self.low3  = tuple(list(self.low2) +[self.low2[1]] )
        self.up2 =   (5,  400);  self.up3   = tuple(list(self.up2) + [self.up2[1]]  )

        self.moreName = "%s; match deltaR<%.1f; %s" % (nametag, matchDeltaRMax, "prompt" if prompt else "")

    def uponAcceptance(self,ev) :
        p4Reco = ev["photonP4Pat"]
        p4Gen = ev["genP4"]
                
        iGensZ = ev["genIndicesZ"]
        iRecos = ev["photonIndicesPat"] if not self.prompt else ev["promptPhotonIndicesPat"]
        iGens = ev["genIndicesPhoton"] if not self.prompt else \
                filter( lambda i : ev["genStatus"][i] == 3,  ev["genIndicesPhoton"])

        iRiGMatches = []
        for igen in iGens :
            for ireco in iRecos :
                if self.deltaRMax > r.Math.VectorUtil.DeltaR( p4Reco.at(ireco), p4Gen.at(igen)) :
                    iRiGMatches.append( (ireco,igen) )
        # resolve multi matches

        for gen in map( p4Gen.at, iGensZ) : self.book.fill( (abs(gen.eta()),gen.pt()), "%sGenZs"%self.nametag, self.bins2, self.low2, self.up2 )
        for gen in map( p4Gen.at, iGens) : self.book.fill( (abs(gen.eta()),gen.pt()), "%sGenPhotons"%self.nametag, self.bins2, self.low2, self.up2 )
        for reco in map( p4Reco.at, iRecos) : self.book.fill( (abs(reco.eta()),reco.pt()), "%sRecoPhotons"%self.nametag, self.bins2, self.low2, self.up2 )
        for reco,gen in [ (p4Reco.at(rg[0]), p4Gen.at(rg[1])) for rg in iRiGMatches] :
            self.book.fill( (abs(gen.eta()),gen.pt(),reco.pt()) , "%sMatchedPhotons"%self.nametag, self.bins3, self.low3, self.up3 )
#####################################
class singlePhotonHistogrammer(analysisStep) :

    def __init__(self, cs, jetCs, maxIndex = 0) :
        self.cs = cs
        self.jetCs = jetCs
        self.maxIndex = maxIndex
        self.moreName="%s%s through index %d" % (self.cs+(maxIndex,))
        self.photonIndicesName = "%sIndices%s" % self.cs
        self.p4sName = "%sP4%s" % self.cs
        self.seedTimes = "%sSeedTime%s" % self.cs

        self.jetIndicesName = "%sIndices%s" % self.jetCs
        self.jetP4Name = "%sCorrectedP4%s" % self.jetCs
        self.mhtName = "%sSumP4%s" % self.jetCs
        self.htName  = "%sSumEt%s"%self.jetCs
        self.etaBE = 1.479 #from CMS PAS EGM-10-005

        self.minDeltaRToJet = "%s%sMinDeltaRToJet%s%s"% (self.cs[0], self.cs[1], self.jetCs[0], self.jetCs[1])
        
    def uponAcceptance (self,eventVars) :
        p4s = eventVars[self.p4sName]
        seedTimes = eventVars[self.seedTimes]
        cleanPhotonIndices = eventVars[self.photonIndicesName]

        cleanJetIndices = eventVars[self.jetIndicesName]
        jetP4s = eventVars[self.jetP4Name]
        mh = eventVars[self.mhtName]
        mht = mh.pt() if mh else None
        ht =  eventVars[self.htName]
        
        #ID variables
        jurassicEcalIsolations    = eventVars["%sEcalRecHitEtConeDR04%s"%self.cs]
        towerBasedHcalIsolations1 = eventVars["%sHcalDepth1TowSumEtConeDR04%s"%self.cs]
        towerBasedHcalIsolations2 = eventVars["%sHcalDepth2TowSumEtConeDR04%s"%self.cs]
        hadronicOverEms           = eventVars["%sHadronicOverEm%s"%self.cs]
        hollowConeTrackIsolations = eventVars["%sTrkSumPtHollowConeDR04%s"%self.cs]
        sigmaIetaIetas            = eventVars["%sSigmaIetaIeta%s"%self.cs]

        #self.book.fill( len(cleanPhotonIndices), "photonMultiplicity", 10, -0.5, 9.5,
        #                title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%self.cs)
        
        for i,iPhoton in enumerate(cleanPhotonIndices) :
            photon = p4s.at(iPhoton)
            pt = photon.pt()

            minDeltaRToJet = eventVars[self.minDeltaRToJet]
            
            photonLabel = str(i+1) if i <= self.maxIndex else "_ge%d"%(self.maxIndex+2)
            self.book.fill(seedTimes[iPhoton], "%s%s%sSeedTime" %(self.cs+(photonLabel,)), 100,  -20.0, 20.0, title=";photon%s seed crystal time (ns);events / bin"%photonLabel)
            self.book.fill(pt,                 "%s%s%sPt" %(self.cs+(photonLabel,)), 50,  0.0, 500.0, title=";photon%s p_{T} (GeV);events / bin"%photonLabel)
            self.book.fill(photon.eta(),       "%s%s%seta"%(self.cs+(photonLabel,)), 20, -3.0,   3.0, title=";photon%s #eta;events / bin"%photonLabel)
            self.book.fill(photon.phi(),       "%s%s%sphi"%(self.cs+(photonLabel,)), 20, -r.TMath.Pi(), r.TMath.Pi(), title=";photon%s #phi;events / bin"%photonLabel)
            self.book.fill((photon.eta(), photon.phi()),  "%s%s%sPhiVsEta"%(self.cs+(photonLabel,)),
                      (10, 10), (-3.0, -r.TMath.Pi()), (3.0, r.TMath.Pi()), title=";photon%s #eta;photon%s #phi;events / bin"%(photonLabel,photonLabel))

            if iPhoton in minDeltaRToJet :
                self.book.fill(minDeltaRToJet[iPhoton],  "%s%s%sMinDRToJet"%(self.cs+(photonLabel,)), 60, 0.0, 6.0, title=";photon%s #DeltaR to closest jet;events / bin"%photonLabel)

            if mht==None : continue
            self.book.fill((pt,mht), "%s%s%smhtVsPhotonPt"%(self.cs+(photonLabel,)),
                           (50, 50), (0.0, 0.0), (500.0, 500.0),
                           title=";photon%s p_{T} (GeV);MHT %s%s (GeV);events / bin"%(photonLabel,self.jetCs[0],self.jetCs[1])
                           )

            self.book.fill(mht/pt, "%s%s%smhtOverPhotonPt"%(self.cs+(photonLabel,)),
                           50, 0.0, 2.0, title=";MHT %s%s / photon%s p_{T};events / bin"%(self.jetCs[0],self.jetCs[1],photonLabel)
                           )
            
            #self.book.fill(pt-mht, "%s%s%sphotonPtMinusMht"%(self.cs+(photonLabel,)),
            #               100, -200.0, 200.0,
            #               title=";photon%s p_{T} - %s%sMHT (GeV);events / bin"%(photonLabel,self.jetCs[0],self.jetCs[1])
            #               )

            self.book.fill((pt-mht)/math.sqrt(ht+mht), "%s%s%sphotonPtMinusMhtOverMeff"%(self.cs+(photonLabel,)),
                           100, -20.0, 20.0,
                           title=";( photon%s p_{T} - MHT ) / sqrt( H_{T} + MHT )    [ %s%s ] ;events / bin"%(photonLabel,self.jetCs[0],self.jetCs[1])
                           )

            #ID variables
            jEI = jurassicEcalIsolations.at(iPhoton)
            tbHI = towerBasedHcalIsolations1.at(iPhoton)+towerBasedHcalIsolations2.at(iPhoton)
            hOE = hadronicOverEms.at(iPhoton)
            hcTI = hollowConeTrackIsolations.at(iPhoton)
            sHH = sigmaIetaIetas.at(iPhoton)

            cmbI = jEI + tbHI + hcTI
            
            #ecalIso
            self.book.fill(jEI, "%s%s%sjurassicEcalIsolation"%(self.cs+(photonLabel,)),
                           50, 0.0, 10.0, title=";ECAL Isolation (GeV);events / bin")
            #self.book.fill((pt,jEI), "%s%s%sjurassicEcalIsolationVsPt"%(self.cs+(photonLabel,)),
            #          (50, 50), (0.0, 0.0), (500.0, 10.0),
            #          title=";photon%s p_{T} (GeV);Jurassic ECAL Isolation;events / bin"%photonLabel)
            
            #hcalIso
            self.book.fill(tbHI, "%s%s%stowerBasedHcalIsolation"%(self.cs+(photonLabel,)),
                           50, 0.0, 10.0, title=";Tower-based HCAL Isolation (GeV);events / bin")
            #self.book.fill((pt,tbHI), "%s%s%stowerBasedHcalIsolationVsPt"%(self.cs+(photonLabel,)),
            #          (50, 50), (0.0, 0.0), (500.0, 10.0),
            #          title=";photon%s p_{T} (GeV);Tower-based HCAL Isolation;events / bin"%photonLabel)

            #hOverE
            self.book.fill(hOE, "%s%s%shadronicOverEm"%(self.cs+(photonLabel,)),
                           50, 0.0, 0.5, title=";Hadronic / EM;events / bin")
            #self.book.fill((pt,hOE), "%s%s%shadronicOverEmVsPt"%(self.cs+(photonLabel,)),
            #          (50, 50), (0.0, 0.0), (500.0, 1.0),
            #          title=";photon%s p_{T} (GeV);Hadronic / EM;events / bin"%photonLabel)

            #trkIso
            self.book.fill(hcTI, "%s%s%shollowConeTrackIsolation"%(self.cs+(photonLabel,)),
                           50, 0.0, 10.0, title=";hollow cone track isolation (GeV);events / bin")
            #self.book.fill((pt,hcTI), "%s%s%shollowConeTrackIsolationVsPt"%(self.cs+(photonLabel,)),
            #          (50, 50), (0.0, 0.0), (500.0, 10.0),
            #          title=";photon%s p_{T} (GeV);hollow cone track isolation;events / bin"%photonLabel)

            #combIso
            self.book.fill(cmbI, "%s%s%scombinedIsolation"%(self.cs+(photonLabel,)),
                           40, -10.0, 30.0, title=";combined isolation (GeV);events / bin")

            #sHH
            if abs(photon.eta())<self.etaBE :
                self.book.fill(sHH, "%s%s%ssigmaIetaIetaBarrel"%(self.cs+(photonLabel,)),
                               50, 0.0, 0.05, title=";sigma i#eta i#eta [photon in barrel];events / bin")
                #self.book.fill((pt,sHH), "%s%s%ssigmaIetaIetaBarrelVsPt"%(self.cs+(photonLabel,)),
                #          (50, 50), (0.0, 0.0), (500.0, 0.1),
                #          title=";photon%s p_{T} (GeV) [photon in barrel];sigma i#eta i#eta;events / bin"%photonLabel)
            else :
                self.book.fill(sHH, "%s%s%ssigmaIetaIetaEndcap"%(self.cs+(photonLabel,)),
                               50, 0.0, 0.05, title=";sigma i#eta i#eta [photon in endcap];events / bin")
                #self.book.fill((pt,sHH), "%s%s%ssigmaIetaIetaEndcapVsPt"%(self.cs+(photonLabel,)),
                #          (50, 50), (0.0, 0.0), (500.0, 0.1),
                #          title=";photon%s p_{T} (GeV) [photon in endcap];sigma i#eta i#eta;events / bin"%photonLabel)
#####################################
class photonDeltaRGreaterSelector(analysisStep) :

    def __init__(self, jets = None, photons = None, minDeltaR = None, photonIndex = None):
        self.photonIndex = photonIndex
        self.minDeltaR = minDeltaR
        self.photonIndicesName = "%sIndices%s"%photons

        self.moreName = "%s%s; %s%s; DR(ph.index[%d], jet) > %.2f"%(jets[0], jets[1], photons[0], photons[1], photonIndex, minDeltaR)
        self.minDeltaRVar = "%s%sMinDeltaRToJet%s%s"%(photons[0], photons[1], jets[0], jets[1])
        
    def select (self,eventVars) :
        indices = eventVars[self.photonIndicesName]
        if len(indices) <= self.photonIndex : return False
        index = indices[self.photonIndex]
        return eventVars[self.minDeltaRVar][index]>self.minDeltaR
#####################################
class photonPtGreaterSelector(analysisStep) :

    def __init__(self, cs, photonPtThreshold, photonIndex):
        self.photonIndex = photonIndex
        self.photonPtThreshold = photonPtThreshold
        self.cs = cs
        self.indicesName = "%sIndices%s" % self.cs
        self.p4sName = "%sP4%s" % self.cs
        self.moreName = "%s%s; pT[index[%d]]>=%.1f GeV" % (self.cs[0], self.cs[1], photonIndex, photonPtThreshold)

    def select (self,eventVars) :
        indices = eventVars[self.indicesName]
        if len(indices) <= self.photonIndex : return False
        p4s = eventVars[self.p4sName]
        return self.photonPtThreshold <= p4s.at(indices[self.photonIndex]).pt()
#####################################
class photonPtLessSelector(analysisStep) :

    def __init__(self, cs, photonPtThreshold, photonIndex):
        self.photonIndex = photonIndex
        self.photonPtThreshold = photonPtThreshold
        self.cs = cs
        self.indicesName = "%sIndices%s" % self.cs
        self.p4sName = "%sP4%s" % self.cs
        self.moreName = "%s%s; pT[index[%d]]<%.1f GeV" % (self.cs[0], self.cs[1], photonIndex, photonPtThreshold)

    def select (self,eventVars) :
        indices = eventVars[self.indicesName]
        if len(indices) <= self.photonIndex : return False
        p4s = eventVars[self.p4sName]
        return self.photonPtThreshold > p4s.at(indices[self.photonIndex]).pt()
#####################################
