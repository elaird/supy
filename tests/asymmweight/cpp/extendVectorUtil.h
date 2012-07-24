// Following http://root.cern.ch/root/html/src/ROOT__Math__VectorUtil.h.html
#include "Math/VectorUtil.h"
typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> > LV;
typedef ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> > LVd1;
typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiE4D<double> > LVd2;
namespace ROOT {
  namespace Math {
    namespace VectorUtil {
      float DeltaPhi     ( const LV& v1, const LV& v2) {return DeltaPhi     <LV,LV>(v1,v2);}
      float DeltaR       ( const LV& v1, const LV& v2) {return DeltaR       <LV,LV>(v1,v2);}
      float CosTheta     ( const LV& v1, const LV& v2) {return CosTheta     <LV,LV>(v1,v2);}
      float Angle        ( const LV& v1, const LV& v2) {return Angle        <LV,LV>(v1,v2);}
      float InvariantMass( const LV& v1, const LV& v2) {return InvariantMass<LV,LV>(v1,v2);}

      //for compatibility with pre-V15 ntuples
      double DeltaPhi     ( const LV& v1, const LVd1& v2) {return DeltaPhi     <LV,LVd1>(v1,v2);}
      double DeltaR       ( const LV& v1, const LVd1& v2) {return DeltaR       <LV,LVd1>(v1,v2);}
      double CosTheta     ( const LV& v1, const LVd1& v2) {return CosTheta     <LV,LVd1>(v1,v2);}
      double Angle        ( const LV& v1, const LVd1& v2) {return Angle        <LV,LVd1>(v1,v2);}
      double InvariantMass( const LV& v1, const LVd1& v2) {return InvariantMass<LV,LVd1>(v1,v2);}

      double DeltaPhi     ( const LV& v1, const LVd2& v2) {return DeltaPhi     <LV,LVd2>(v1,v2);}
      double DeltaR       ( const LV& v1, const LVd2& v2) {return DeltaR       <LV,LVd2>(v1,v2);}
      double CosTheta     ( const LV& v1, const LVd2& v2) {return CosTheta     <LV,LVd2>(v1,v2);}
      double Angle        ( const LV& v1, const LVd2& v2) {return Angle        <LV,LVd2>(v1,v2);}
      double InvariantMass( const LV& v1, const LVd2& v2) {return InvariantMass<LV,LVd2>(v1,v2);}

    }
  }
}
