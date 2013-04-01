#ifndef Susy_SusyNt_h
#define Susy_SusyNt_h


#include <iostream>
#include "TLorentzVector.h"


namespace Susy
{
  class Particle : public TLorentzVector
  {
  public:
    Particle(){ clear(); }
    virtual ~Particle(){};
    Particle(const Particle &);
    Particle& operator=(const Particle &);
    unsigned int idx;   // d3pd index
    // Crowd wants pt, eta, phi of nominal stored
    float pt;
    float eta;
    float phi;
    float m;
    void resetTLV(){ this->SetPtEtaPhiM(pt,eta,phi,m); };
    // Internal state for particles. Makes easier to grab right TLV given systematic variations
    void setState(int sys){ resetTLV(); };
    void clear() { 
      TLorentzVector::Clear(); 
      idx = 999;      // This is not a very good choice...
      pt = eta = phi = m = 0;
    }
    virtual void print() const {};

    ClassDef(Particle, 1);
  };
};


#endif
