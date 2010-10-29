import ROOT as r
import utils,collections
from analysisStep import analysisStep
#####################################
pdgLookupExists=False
try:
    import pdgLookup
    pdgLookupExists=True
except ImportError:
    pass
#####################################
class ptHatFilter(analysisStep) :

    def __init__(self,maxPtHat) :
        self.maxPtHat=maxPtHat
        self.moreName = "(pthat<%.1f)"%maxPtHat

    def select (self,eventVars) :
        return eventVars["genpthat"]<self.maxPtHat
#####################################
class susyScanPointPrinter(analysisStep) :

    def __init__(self) :
        self.leavesToPrint=["susyScanA0",
                            "susyScanCrossSection",
                            "susyScanM0",
                            "susyScanM12",
                            "susyScanMu",
                            "susyScanRun",
                            "susyScanTanBeta"
                            ]
        
    def uponAcceptance (self,eventVars) :
        outString=""
        for leafName in self.leavesToPrint :
            outString+=leafName.replace("susyScan","")+" = "+str(eventVars[leafName])+"\t"
        print outString
#####################################
class genJetPrinter(analysisStep) :

    def __init__(self,jetCollection,jetSuffix) :
        self.jetCollection=jetCollection
        self.jetSuffix=jetSuffix
        self.moreName="("
        self.moreName+=self.jetCollection
        self.moreName+="; "
        self.moreName+=self.jetSuffix
        self.moreName+=")"

    def uponAcceptance (self,eventVars) :
        p4Vector        =eventVars[self.jetCollection+'GenJetP4'     +self.jetSuffix]
        #emEnergy        =eventVars[self.jetCollection+'EmEnergy'        +self.jetSuffix]
        #hadEnergy       =eventVars[self.jetCollection+'HadEnergy'       +self.jetSuffix]
        #invisibleEnergy =eventVars[self.jetCollection+'InvisibleEnergy' +self.jetSuffix]
        #auxiliaryEnergy =eventVars[self.jetCollection+'AuxiliaryEnergy' +self.jetSuffix]

        print " jet   pT (GeV)    eta    phi    emF   hadF   invF   auxF"
        print "---------------------------------------------------------"
        for iJet in range(len(p4Vector)) :
            jet=p4Vector[iJet]
            totalEnergy=jet.energy()
            
            outString=" "
            #if (iJet in otherJetIndices) : outString="-"
            #if (iJet in cleanJetIndices) : outString="*"
            
            outString+=" %2d"   %iJet
            outString+="     %#6.1f"%jet.pt()
            outString+="   %#4.1f"%jet.eta()
            outString+="   %#4.1f"%jet.phi()
            #outString+="   %#4.2f"%(       emEnergy[iJet]/totalEnergy)
            #outString+="   %#4.2f"%(      hadEnergy[iJet]/totalEnergy)
            #outString+="   %#4.2f"%(invisibleEnergy[iJet]/totalEnergy)
            #outString+="   %#4.2f"%(auxiliaryEnergy[iJet]/totalEnergy)
            ##outString+="  %#4.2f"%( (emEnergy[iJet]+hadEnergy[iJet]+invisibleEnergy[iJet]+auxiliaryEnergy[iJet]) / totalEnergy )
            print outString
        print
#####################################
class genParticleCountHistogrammer(analysisStep) :

    def __init__(self,tanBeta) :
        self.tanBetaThreshold=0.1
        self.tanBeta=tanBeta
        self.maxCountsPerCategory=2 #0 ... this number counted explicitly; otherwise overflows

        #Lo and Hi are both sampled in scan
        self.m0Lo=0.0
        self.m0Hi=4000.0
        self.m0StepSize=50.0
        self.nBinsM0=int(1+(m0Hi-m0Lo)/m0StepSize)

        self.m12Lo=100.0
        self.m12Hi=600.0
        self.m12StepSize=20.0
        self.nBinsM12=int(1+(m12Hi-m12Lo)/m12StepSize)

        self.histoBaseName="genParticleCounter"
        self.madeLabelHisto=False

    def makeCodeString(self,eventVars) :
        codeString=""
        for category,count in eventVars["GenParticleCategoryCounts"].iteritems() :
            if count>self.maxCountsPerCategory :
                count=self.maxCountsPerCategory+1
            codeString+=str(count)
        return codeString
    
    def uponAcceptance (self,eventVars) :
        if abs(eventVars["susyScanTanBeta"]-self.tanBeta)>self.tanBetaThreshold : return

        #make histo with labels
        if not self.madeLabelHisto :
            nCategories=len(eventVars["GenParticleCategoryCounts"])
            labelHistoName=self.histoBaseName+"CategoryLabels"
            self.book(eventVars).fill(-1.0,labelHistoName,
                                      nCategories,-0.5,nCategories-0.5,
                                      ";categories")
            for book in self.books.values() :
                if labelHistoName not in book : continue

                categories=eventVars["GenParticleCategoryCounts"].keys()
                for iCategory in range(len(categories)) :
                    book[labelHistoName].GetXaxis().SetBinLabel(iCategory+1,categories[iCategory])
                    book[labelHistoName].SetBinContent(iCategory+1,self.maxCountsPerCategory)
            self.madeLabelHisto=True

        #get scan point info
        xs=eventVars["susyScanCrossSection"]
        m0=eventVars["susyScanM0"]
        m12=eventVars["susyScanM12"]

        #fill histos
        codeString=self.makeCodeString(eventVars)
        self.book(eventVars).fill( (m0, m12), self.histoBaseName+codeString,
                                   (self.nBinsM0, self.nBinsM12),
                                   (self.m0Lo-self.m0StepSize/2.0, self.m12Lo-self.m12StepSize/2.0),
                                   (self.m0Hi+self.m0StepSize/2.0, self.m12Hi+self.m12StepSize/2.0),
                                   self.histoBaseName+codeString+";m_{0} (GeV);m_{1/2} (GeV)",
                                   )

        self.book(eventVars).fill( (m0, m12), self.histoBaseName+"nEvents",
                                   (self.nBinsM0, self.nBinsM12),
                                   (self.m0Lo-self.m0StepSize/2.0, self.m12Lo-self.m12StepSize/2.0),
                                   (self.m0Hi+self.m0StepSize/2.0, self.m12Hi+self.m12StepSize/2.0),
                                   self.histoBaseName+"nEvents;m_{0} (GeV);m_{1/2} (GeV)",
                                   )

        self.book(eventVars).fill( (m0, m12), self.histoBaseName+"XS",
                                   (self.nBinsM0, self.nBinsM12),
                                   (self.m0Lo-self.m0StepSize/2.0, self.m12Lo-self.m12StepSize/2.0),
                                   (self.m0Hi+self.m0StepSize/2.0, self.m12Hi+self.m12StepSize/2.0),
                                   xs,
                                   self.histoBaseName+"XS;m_{0} (GeV);m_{1/2} (GeV)",
                                   )
#####################################
class genParticlePrinter(analysisStep) :

    def __init__(self,minPt=-1.0,minStatus=-1):
        self.oneP4=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        self.sumP4=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        self.zeroP4=r.Math.LorentzVector(r.Math.PxPyPzE4D('double'))(0.0,0.0,0.0,0.0)
        self.minPt=minPt
        self.minStatus=minStatus
        
    def uponAcceptance (self,eventVars) :

        self.sumP4.SetCoordinates(0.0,0.0,0.0,0.0)

        mothers=set(eventVars["genMother"])
        print "mothers: ",mothers
        print "---------------------------------------------------------------------------"
        print " i  st    mo         id            name        E        pt       eta    phi"
        print "---------------------------------------------------------------------------"

        size=len(eventVars["genP4"])
        for iGen in range(size) :

            p4=eventVars["genP4"][iGen]
            if p4.pt()<self.minPt :
                continue

            status=eventVars["genStatus"][iGen]
            if status<self.minStatus :
                continue

            pdgId=eventVars["genPdgId"][iGen]
            outString=""
            outString+="%#2d"%iGen
            outString+=" %#3d"%status
            outString+="  %#4d"%eventVars["genMother"][iGen]
            outString+=" %#10d"%pdgId
            if pdgLookupExists : outString+=" "+pdgLookup.pdgid_to_name(pdgId).rjust(15)
            else :                 outString+="".rjust(16)
            outString+="  %#7.1f"%p4.E()
            outString+="  %#8.1f"%p4.pt()
            outString+="  %#8.1f"%p4.eta()
            outString+="  %#5.1f"%p4.phi()
            #outString+="  %#5.1f"%p4.mass()
        
            if not (iGen in mothers) :
                outString+="   non-mo"
        #        self.sumP4+=self.oneP4
        #        #outString2="non-mo P4 sum".ljust(37)
        #        #outString2+="  %#7.1f"%self.sumP4.E()
        #        #outString2+="  %#8.1f"%self.sumP4.eta()
        #        #outString2+="  %#8.1f"%self.sumP4.pt()
        #        #outString2+="  %#5.1f"%self.sumP4.phi()
        #        #print outString2
        #
            print outString
        #
        #outString="non-mo P4 sum".ljust(37)
        #outString+="  %#7.1f"%self.sumP4.E()
        #outString+="  %#8.1f"%self.sumP4.eta()
        #outString+="  %#8.1f"%self.sumP4.pt()
        #outString+="  %#5.1f"%self.sumP4.phi()
        #print outString
        print
#####################################
class genMassHistogrammer(analysisStep) :

    def __init__(self,pdgId = 23):
        self.pdgId = pdgId
        self.histoName = "mass_pdgId==%d"%self.pdgId
        
    def uponAcceptance (self,eventVars) :
        size=len(eventVars["genP4"])
        for iGen in range(size) :
            p4=eventVars["genP4"].at(iGen)
            if eventVars["genPdgId"].at(iGen)!=self.pdgId : continue
            self.book(eventVars).fill(p4.mass(), self.histoName, 100, 0.0, 300.0, title = ";mass (GeV);events / bin")
#####################################
class genSHatHistogrammer(analysisStep) :

    def uponAcceptance (self,eventVars) :
        p4 = eventVars["genP4"]
        size=p4.size()
        counts = [0,0]
        indices = [-1,-1]
        for iGen in range(size) :
            if not eventVars["genMotherStored"].at(iGen) : continue
            motherIndex = eventVars["genMother"].at(iGen)
            if motherIndex!=0 and motherIndex!=1 : continue
            counts[motherIndex] += 1
            indices[motherIndex] = iGen

        if counts[0]!=1 or counts[1]!=1 :
            print "bad counts",counts
            return
        
        rootSHat = ( p4.at(indices[0])+p4.at(indices[1]) ).mass()
        print indices,rootSHat
        self.book(eventVars).fill(rootSHat, "rootSHat", 100, 0.0, 300.0, title = ";#sqrt{#hat{s}} (GeV);events / bin")
#####################################
class photonEfficiencyPlots(analysisStep) :

    def __init__(self, label, ptCut, etaCut, isoCut, jets, photons) :
        for item in ["label","ptCut","etaCut","isoCut","jets", "photons"] :
            setattr(self,item,eval(item))
        self.jetHt         = "%sSumEt%s"  %self.jets
        self.photonHt      = "%sSumEt%s"  %self.photons
        
        self.jetIndices    = "%sIndices%s"%self.jets
        self.photonIndices = "%sIndices%s"%self.photons

        self.minDeltaRToJet = "%s%sMinDeltaRToJet%s%s"% (self.photons[0], self.photons[1], self.jets[0], self.jets[1])
        self.moreName = "pT>%g GeV; |eta|<%g; iso<%g"%(self.ptCut, self.etaCut, self.isoCut)

    def uponAcceptance (self, eventVars) :
        genP4s = eventVars["genP4"]
        nGen = genP4s.size()

        n = 0
        for genIndex in eventVars["genIndices"+self.label] :
            photon = genP4s.at(genIndex)
            pt = photon.pt()
            eta = photon.eta()
            phi = photon.phi()
            
            if pt<self.ptCut or self.etaCut<abs(eta) : continue

            if eventVars["category"+self.label][genIndex]=="otherMother" : continue
            
            iso = eventVars["genIsolation"+self.label][genIndex]
            if self.isoCut < iso : continue

            n+=1
            self.book(eventVars).fill(iso,"photonIso"+self.label, 100, 0.0,  100.0, title = ";gen photon isolation [5 GeV cut-off] (GeV);photons / bin")
            self.book(eventVars).fill(eta,"photonEta"+self.label, 100, -3.0,   3.0, title = ";gen photon #eta;photons / bin")
            self.book(eventVars).fill(pt, "photonPt"+self.label,  100,  0.0, 500.0, title = ";gen photon p_{T} (GeV);photons / bin")
            self.book(eventVars).fill((eta, phi), "photonPhiVsEta"+self.label, (72, 72), (-3.0, -r.TMath.Pi()), (3.0, r.TMath.Pi()),
                                      title = ";gen photon #eta;gen photon #phi;photons / bin")

            nJets = len(eventVars[self.jetIndices])
            jetHt = eventVars[self.jetHt]

            photonIndices = eventVars[self.photonIndices]
            nPhotons      = len(photonIndices)
            photonHt      = eventVars[self.photonHt]
            
            self.book(eventVars).fill(nJets,            "nJets"+self.label,              10, -0.5, 9.5,    title = ";nJets [gen photon satisfies cuts];photons / bin")
            self.book(eventVars).fill(jetHt,            "jetHt"+self.label,             100,  0.0, 1000.0, title = ";H_{T} [jets] (GeV) [gen photon satisfies cuts];photons / bin")
            self.book(eventVars).fill(nJets + nPhotons, "nJetsPlusnPhotons"+self.label,  10, -0.5, 9.5,    title = ";nJets+nPhotons [gen photon satisfies cuts];photons / bin")
            self.book(eventVars).fill(jetHt + photonHt, "jetHtPlusPhotonHt"+self.label, 100,  0.0, 1000.0, title = ";H_{T} [jets+photons] (GeV) [gen photon satisfies cuts];photons / bin")
            deltaR = eventVars["genMinDeltaRPhotonOtherStatus3Photon"]
            if deltaR!=None : 
                self.book(eventVars).fill(deltaR, "getMinDeltaRPhotonOtherStatus3Photon"+self.label,50, 0.0, 5.0,
                                          title = ";#DeltaR between st.3 photon and nearest daughterless st.3 particle; events / bin")
        self.book(eventVars).fill(n,"nGenPhotons"+self.label, 10, -0.5, 9.5,title = ";N gen photons [gen photon satisfies cuts];photons / bin")
#####################################
class photonPurityPlots(analysisStep) :

    def __init__(self, label, jetCs, photonCs) :
        for item in ["label","jetCs","photonCs"] :
            setattr(self,item,eval(item))

        self.bin = {}
        self.bin["photonMother"] = 0
        self.bin["quarkMother"]  = 1
        self.bin["otherMother"]  = 2
        
    def uponAcceptance (self, eventVars) :
        genP4s   = eventVars["genP4"]
        jetSumP4 = eventVars["%sSumP4%s"%self.jetCs]

        photonIndices = eventVars["%sIndices%s"%self.photonCs]
        if not len(photonIndices) : return
        recoP4   = eventVars["%sP4%s"%self.photonCs].at( photonIndices[0] )
        categories = eventVars["category"+self.label]

        recoPt = recoP4.pt()
        matchedIndices = []
        for index in eventVars["genIndices"+self.label] :
            genP4 = genP4s.at(index)
            genPt  = genP4.pt()
            deltaR = r.Math.VectorUtil.DeltaR(recoP4,genP4)
            #if genPt>0.3*recoPt :
            #    self.book(eventVars).fill(deltaR,"deltaRGenReco", 100, 0.0, 5.0, title = ";#DeltaR (GEN,RECO) photon when {gen pT > 0.3 reco pT};photons / bin")

            if deltaR>0.5 :
                continue
            matchedIndices.append(index)
            #self.book(eventVars).fill(genPt,         categories[index]+"genPt" , 100, 0.0, 200.0, title = ";GEN photon p_{T} (GeV);photons / bin")
            #self.book(eventVars).fill(recoPt,        categories[index]+"recoPt", 100, 0.0, 200.0, title = ";reco. photon p_{T} (GeV);photons / bin")
            #if jetSumP4 :
            #    self.book(eventVars).fill(jetSumP4.pt(), categories[index]+"mht",    100, 0.0, 200.0, title = ";MHT (GeV);photons / bin")

        nMatch = len(matchedIndices)
        self.book(eventVars).fill(nMatch,"nMatch",10, -0.5, 9.5, title = ";N gen. photons within #DeltaR 0.5 of the reco photon;photons / bin")
        label = "1"if len(matchedIndices)==1 else "gt1"
        for index in matchedIndices :
            self.book(eventVars).fill( ( recoPt, genP4s.at(index).pt() ), "genVsRecoPt%s"%label,
                                       (50,50), (0.0,0.0), (200.0,200.0),
                                       title = "nMatch = %s;RECO photon p_{T} (GeV);GEN photon p_{T} (GeV);photons / bin"%label)
            self.book(eventVars).fill(self.bin[categories[index]],"photonCategory%s"%label,
                                      len(self.bin), -0.5, len(self.bin)-0.5,
                                      title = ";photon category when nMatch = %s;photons / bin"%label)

    def endFunc(self,chain,otherChainDict,nEvents,xs) :
        for book in self.books.values() :
            for key,histo in book.iteritems() :
                if "photonCategory" in histo.GetName() :
                    for label,iBin in self.bin.iteritems() :
                        histo.GetXaxis().SetBinLabel(iBin+1,label)
#####################################
class genMotherHistogrammer(analysisStep) :

    def __init__(self, indexLabel, specialPtThreshold) :
        self.indexLabel = indexLabel
        self.specialPtThreshold = specialPtThreshold
        self.keyAll       = "motherIdVsPt%sAll"%self.indexLabel
        self.keyAllHighPt = "motherIdVsPt%sAllHighPt"%self.indexLabel        
        self.motherDict = collections.defaultdict(int)
        self.binLabels = []
        self.binLabels.append("other")

        self.addParticle( 1, "d"); self.addParticle(-1, "#bar{d}")
        self.addParticle( 2, "u"); self.addParticle(-2, "#bar{u}")
        self.addParticle( 3, "s"); self.addParticle(-3, "#bar{s}");
        self.addParticle( 4, "c"); self.addParticle(-4, "#bar{c}");
        self.addParticle(21, "gluon")
        self.addParticle(22, "photon")
        self.addParticle(111,"#pi^{0}")
        self.addParticle(221,"#eta")
        self.addParticle(223,"#omega")
        self.addParticle(331,"#eta^{/}")
        
    def addParticle(self, id, name) :
        self.binLabels.append(name)
        self.motherDict[id] = self.binLabels[-1]

    def fillSpecialHistos(self, eventVars, iParticle) :
        motherIndex = eventVars["genMother"].at(iParticle)
        #motherIndex = eventVars["genMotherIndex"].at(iParticle)
        p4 = eventVars["genP4"].at(iParticle)
        motherP4 = eventVars["genP4"].at(motherIndex)
        deltaRPhotonMother = r.Math.VectorUtil.DeltaR(p4,motherP4)
        deltaRPhotonOther  = r.Math.VectorUtil.DeltaR(p4,motherP4-p4)
        
        self.book(eventVars).fill(motherP4.mass(), "mothersMass",
                                  20, -0.1, 0.4,
                                  title = ";mother's mass (GeV) [when GEN photon p_{T}> %.1f (GeV) and mother is u quark];photons / bin"%self.specialPtThreshold
                                  )
        self.book(eventVars).fill(deltaRPhotonMother, "deltaRPhotonMother",
                                  20, 0.0, 1.5,
                                  title = ";#DeltaR(photon,mother) [when GEN photon p_{T}> %.1f (GeV) and mother is u quark];photons / bin"%self.specialPtThreshold
                                  )
        self.book(eventVars).fill(deltaRPhotonOther, "deltaRPhotonOther",
                                  20, 0.0, 1.5,
                                  title = ";#DeltaR(photon,mother-photon) [when GEN photon p_{T}> %.1f (GeV) and mother is u quark];photons / bin"%self.specialPtThreshold
                                  )
        
    def uponAcceptance (self, eventVars) :
        indices = eventVars[self.indexLabel]
        if len(indices)==0 : return

        p4s = eventVars["genP4"]
        nBinsY = len(self.binLabels)
        for iParticle in indices :
            p4 = p4s.at(iParticle)
            pt = p4.pt()
            motherId = eventVars["genMotherPdgId"][iParticle]
            if not self.motherDict[motherId] :
                #print motherId,"not found"
                yValue = 0
            else :
                yValue = self.binLabels.index(self.motherDict[motherId])
            self.book(eventVars).fill((pt,yValue), self.keyAll, (50,nBinsY), (0.0,-0.5), (500.0, nBinsY-0.5), title = ";GEN photon p_{T} (GeV);mother;photons / bin")
            if pt>self.specialPtThreshold :
                self.book(eventVars).fill(yValue, self.keyAllHighPt,
                                          nBinsY, -0.5, nBinsY-0.5,
                                          title = ";mother [when GEN photon p_{T}> %.1f (GeV)];photons / bin"%self.specialPtThreshold
                                          )
                if motherId==2 : self.fillSpecialHistos(eventVars, iParticle)

    def endFunc(self, chain, otherChainDict, nEvents, xs) :
        for book in self.books.values() :
            if self.keyAll in book :
                for iParticle in range(len(self.binLabels)) :
                    book[self.keyAll].GetYaxis().SetBinLabel(iParticle+1,self.binLabels[iParticle])
            if self.keyAllHighPt in book :
                for iParticle in range(len(self.binLabels)) :
                    book[self.keyAllHighPt].GetXaxis().SetBinLabel(iParticle+1,self.binLabels[iParticle])
#####################################
class zHistogrammer(analysisStep) :

    def __init__(self, jetCs) :
        self.jetCs = jetCs
        self.mhtName = "%sSumP4%s" % self.jetCs
        self.htName  = "%sSumEt%s"%self.jetCs
        
    def uponAcceptance (self,eventVars) :
        book = self.book(eventVars)
        p4s = eventVars["genP4"]
        mht = eventVars[self.mhtName].pt()
        ht =  eventVars[self.htName]
        
        book.fill( len(cleanPhotonIndices), "photonMultiplicity", 10, -0.5, 9.5,
                   title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%self.cs)

        zIndices = eventVars["genIndicesZ"]
        if len(zS)>1 : return False
        for index in zIndices :
            Z = p4s.at(iPhoton)
            pt = photon.pt()


            book.fill(pt,           "%s%s%sPt" %(self.cs+(photonLabel,)), 50,  0.0, 500.0, title=";photon%s p_{T} (GeV);events / bin"%photonLabel)
            book.fill(photon.eta(), "%s%s%seta"%(self.cs+(photonLabel,)), 50, -5.0,   5.0, title=";photon%s #eta;events / bin"%photonLabel)

            book.fill((pt,mht), "%s%s%smhtVsPhotonPt"%(self.cs+(photonLabel,)),
                      (50, 50), (0.0, 0.0), (500.0, 500.0),
                      title=";photon%s p_{T} (GeV);MHT %s%s (GeV);events / bin"%(photonLabel,self.jetCs[0],self.jetCs[1])
                      )

            book.fill(mht/pt, "%s%s%smhtOverPhotonPt"%(self.cs+(photonLabel,)),
                      50, 0.0, 2.0, title=";MHT %s%s / photon%s p_{T};events / bin"%(self.jetCs[0],self.jetCs[1],photonLabel)
                      )

            #book.fill(pt-mht, "%s%s%sphotonPtMinusMht"%(self.cs+(photonLabel,)),
            #          100, -200.0, 200.0,
            #          title=";photon%s p_{T} - %s%sMHT (GeV);events / bin"%(photonLabel,self.jetCs[0],self.jetCs[1])
            #          )

            book.fill((pt-mht)/math.sqrt(ht+mht), "%s%s%sphotonPtMinusMhtOverMeff"%(self.cs+(photonLabel,)),
                      100, -20.0, 20.0,
                      title=";( photon%s p_{T} - MHT ) / sqrt( H_{T} + MHT )    [ %s%s ] ;events / bin"%(photonLabel,self.jetCs[0],self.jetCs[1])
                      )
#####################################
