from supy.defaults import *

def cppROOTDictionariesToGenerate() :
    return [
        ("vector<ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> > >", "vector;Math/LorentzVector.h"),
        ]

def cppFiles() :
    return ["cpp/linkdef.cxx"]
