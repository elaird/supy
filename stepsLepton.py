from analysisStep import analysisStep

class leptonFilter(analysisStep) :
        """leptonFilter"""

        def __init__(self,nMinLeptons, minPt=0) :
            self.neededBranches=["muonP4Pat", "muonP4PF",
                                             "electronP4Pat", "electronP4PF",
                                             "tauP4Pat", "tauP4PF"]
            self.nMinLeptons=nMinLeptons
            self.minPt=minPt
            self.moreName="(nLeptons >= %d, pt > %f)" % (self.nMinLeptons, self.minPt)

        def select(self,chain,chainVars,extraVars) :
            # muons
            nMuonsPF = len(chainVars.muonP4PF)
            nMuonsPAT = len(chainVars.muonP4Pat)

            nGoodMuonsPF = 0
            for i in range(nMuonsPF):
                #print "mu pf pt: %f" % chainVars.muonP4PF[i].pt()
                if (chainVars.muonP4PF[i].pt() > self.minPt):
                    nGoodMuonsPF += 1
                    
            nGoodMuonsPAT = 0
            for i in range(nMuonsPAT):
                #print "mu pat pt: %f" % chainVars.muonP4Pat[i].pt()
                if (chainVars.muonP4Pat[i].pt() > self.minPt):
                    nGoodMuonsPAT += 1


            # electrons
            nElectronsPF = len(chainVars.electronP4PF)
            nElectronsPAT = len(chainVars.electronP4Pat)
            
            nGoodElectronsPF = 0
            for i in range(nElectronsPF):
                #print "e pf pt: %f" % chainVars.electronP4PF[i].pt()
                if (chainVars.electronP4PF[i].pt() > self.minPt):
                    nGoodElectronsPF += 1
                    

            nGoodElectronsPAT = 0
            for i in range(nElectronsPAT):
                #print "e pat pt: %f" % chainVars.electronP4Pat[i].pt()
                if (chainVars.electronP4Pat[i].pt() > self.minPt):
                    nGoodElectronsPAT += 1


            # taus
            nTausPF = len(chainVars.tauP4PF)
            nTausPAT = len(chainVars.tauP4Pat)

            nGoodTausPF = 0
            for i in range(nTausPF):
                #print "tau pf pt: %f" % chainVars.tauP4PF[i].pt()
                if (chainVars.tauP4PF[i].pt() > self.minPt):
                    nGoodTausPF += 1
                    
            nGoodTausPAT = 0
            for i in range(nTausPAT):
                #print "tau pat pt: %f" % chainVars.tauP4Pat[i].pt()
                if (chainVars.tauP4Pat[i].pt() > self.minPt):
                    nGoodTausPAT += 1


            #print "mu: %d / %d, e: %d / %d, tau: %d / %d" % (nGoodMuonsPF, nGoodMuonsPAT, nGoodElectronsPF, nGoodElectronsPAT, nGoodTausPF, nGoodTausPAT)
            if (self.nMinLeptons == 1):
                # select events with at least one lepton candidate (pat as well as pf)
                return (nGoodMuonsPF != 0 or nGoodMuonsPAT != 0 or nGoodElectronsPF != 0 or nGoodElectronsPAT != 0 or nGoodTausPF != 0 or nGoodTausPAT != 0)
            else:
                # number != 1 has been specified, count only PF candidates
                return (nGlobalMuonsPF + nGoodElectronsPF + nGoodTausPF) >= self.nMinLeptons



