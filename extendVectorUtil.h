// Following http://root.cern.ch/root/html/src/ROOT__Math__VectorUtil.h.html
#include "Math/VectorUtil.h"
typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> > LV;
namespace ROOT {
  namespace Math {
    namespace VectorUtil {
      float DeltaPhi     ( const LV& v1, const LV& v2) {return DeltaPhi     <LV,LV>(v1,v2);}
      float DeltaR       ( const LV& v1, const LV& v2) {return DeltaR       <LV,LV>(v1,v2);}
      float CosTheta     ( const LV& v1, const LV& v2) {return CosTheta     <LV,LV>(v1,v2);}
      float Angle        ( const LV& v1, const LV& v2) {return Angle        <LV,LV>(v1,v2);}
      float InvariantMass( const LV& v1, const LV& v2) {return InvariantMass<LV,LV>(v1,v2);}
    }
  }
}
