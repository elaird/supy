#include "Math/LorentzVector.h"
#include "TMath.h"
#include "TString.h"
#include "TGraph.h"
#include "TBranch.h"
#include "TH2D.h"
///////////////////////////////////////////////////////////////////////
class cleanJetIndexHelper {
public:

  //constructor and destructor
  cleanJetIndexHelper() {}
  ~cleanJetIndexHelper() {}

  void SetThresholds(double jetPtThresholdIn,double jetEtaMaxIn) {
    jetPtThreshold=jetPtThresholdIn;
    jetEtaMax=jetEtaMaxIn;
  }

  void Loop(std::vector<ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> > >* jetP4,
	    std::vector<float>*  jetEmf,
	    std::vector<double>* jetFHpd,
	    std::vector<int>*    jetN90Hits,
	    std::vector<int>*    cleanJetIndices,
	    std::vector<int>*    otherJetIndices) {

    unsigned int nJets=jetP4->size();
    for (unsigned int iJet=0;iJet<nJets;++iJet) {
      //pt cut
      if (jetP4->at(iJet).pt()<jetPtThreshold) break; //assumes sorted
      
      //if pass pt cut, add to "other" category
      otherJetIndices->push_back(iJet);
            
      //eta cut
      double absEta=fabs(jetP4->at(iJet).eta());
      if (absEta>jetEtaMax) continue;
      
      //jet ID
      if (absEta<=2.6) {
	if (jetEmf->at(iJet)<=0.01)  continue;
      }
      if (jetFHpd->at(iJet)>=0.98)  continue;
      if (jetN90Hits->at(iJet)<2)  continue;

      cleanJetIndices->push_back(iJet);
      otherJetIndices->pop_back();
    }
    
  }
  
private:
    double jetPtThreshold;
    double jetEtaMax;
};
///////////////////////////////////////////////////////////////////////
class htMhtHelper {
public:

  //constructor and destructor
  htMhtHelper() {
    mht=new ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> >(0.0,0.0,0.0,0.0);
  }
  ~htMhtHelper() {delete mht;}

  ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> >* GetMht()  {return mht;}
  double GetHt()   {return ht;  }
  double GetHtEt() {return htEt;}
  
  void Loop(std::vector<ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> > >* jetP4,
	    std::vector<int>*    cleanJetIndices) {

    mht->SetCoordinates(0.0,0.0,0.0,0.0);
    ht=0.0;
    htEt=0.0;

    unsigned int nJets=cleanJetIndices->size();
    for (unsigned int i=0;i<nJets;++i) {
      int iJet=cleanJetIndices->at(i);
      ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> >& jet=jetP4->at(iJet);
      (*mht)-=jet;
      ht+=jet.pt();
      htEt+=jet.Et();
    }
  }
  
private:
  ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> >* mht;
  double ht;
  double htEt;
};
///////////////////////////////////////////////////////////////////////
class alphaHelper {
public:

  //constructor and destructor
  alphaHelper() {
    pts.reserve(256);
  }
  
  ~alphaHelper() {}
  
  double GetMinDiff() {
    return minDiff;
  }

  void go(std::vector<ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> > >* jets,
	  std::vector<int>* cleanJetIndices) {
    
    pts.clear();
    double totalPt=0.0;
    
    unsigned int nJets=cleanJetIndices->size();
    
    for (unsigned int i=0;i<nJets;++i) {
      int iJet=cleanJetIndices->at(i);
      ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> >&jet=jets->at(iJet);
      double pt=jet.pt();
      pts.push_back(pt);
      totalPt+=pt;
    }
    
    int nCombinations=1<<nJets;
    
    minDiff=1.0e6;
    for (int iCombination=0;iCombination<nCombinations;++iCombination) {
      double pseudoJetPt=0.0;
      for (unsigned int iJet=0;iJet<nJets;++iJet) {
	if (iCombination&(1<<iJet)) pseudoJetPt+=pts.at(iJet);
      }
      double thisDiff=fabs(totalPt-2.0*pseudoJetPt);
      if (thisDiff<minDiff) minDiff=thisDiff;
    }
    
  }
  
private:
  std::vector<double> pts;
  double minDiff;
};
///////////////////////////////////////////////////////////////////////
class displayHelper {
public:

  //constructor and destructor
  displayHelper() {}
  ~displayHelper() {}

  void Fill(TH2D *histo,std::vector<double>* x,std::vector<double>* y,int nVariedJets) {
    if (nVariedJets<=0) return;

    unsigned int N=x->size();
    for (unsigned int i=0;i<N;++i) {
      histo->Fill(x->at(i)/nVariedJets,y->at(i));
    }
  }
};
/////////////////////////////////////////////////////////////////////////
//class analysisStepHelper {
//public:
//  analysisStepHelper() {branches.reserve(20);}
//  ~analysisStepHelper() {}
//
//  void AddBranch(TBranch* branch) {
//    branches.push_back(branch);
//  }
//
//  void Clear() {
//    branches.clear();
//  }
//
//  void readData(Long64_t localEntry) {
//    unsigned int nBranches=branches.size();
//    for (unsigned int iBranch=0;iBranch<nBranches;++iBranch) {
//      //if (localEntry==0) std::cout << "branch= " << branches.at(iBranch) << std::endl;
//      branches.at(iBranch)->GetEntry(localEntry);
//    }
//  }
//private:
//  std::vector<TBranch*> branches;
//};
