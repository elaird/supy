#include "Math/LorentzVector.h"
#include "extendVectorUtil.h"
#ifdef __CINT__ 
typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> > LV;
#pragma link C++ class ROOT::Math::PtEtaPhiM4D<float>+;
//#pragma link C++ class ROOT::Math::PtEtaPhiM4D<float>::*+;
#pragma link C++ class ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> >+;
//#pragma link C++ class ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> >::*+;
#pragma link C++ function ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> >::operator+(LV);
#pragma link C++ function ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> >::operator-(LV);
#pragma link C++ namespace ROOT::Math::VectorUtil+;
//#pragma link C++ nestedclasses; 
//#pragma link C++ nestedtypedefs;
#endif
