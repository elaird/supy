#include "Math/LorentzVector.h"
#include "extendVectorUtil.h"
#include "Math/BoostZ.h"
#ifdef __CINT__ 
typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> > LV;
#pragma link C++ class ROOT::Math::PtEtaPhiM4D<float>+;
//#pragma link C++ class ROOT::Math::PtEtaPhiM4D<float>::*+;
#pragma link C++ class ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> >+;
//#pragma link C++ class ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> >::*+;
#pragma link C++ function ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> >::operator+(LV);
#pragma link C++ function ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> >::operator-(LV);
#pragma link C++ function ROOT::Math::BoostZ::operator()(LV);
#pragma link C++ namespace ROOT::Math::VectorUtil+;
//#pragma link C++ nestedclasses; 
//#pragma link C++ nestedtypedefs;

//for compatibility with pre-V15 ntuples
typedef ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> > LVd;
#pragma link C++ function ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> >::operator+(LVd);
#pragma link C++ function ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> >::operator-(LVd);
#pragma link C++ function ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> >::operator+(LV);
#pragma link C++ function ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> >::operator-(LV);
#endif
