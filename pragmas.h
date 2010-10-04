#include <map>
#include <vector>
#include <string>

#include <Math/LorentzVector.h>

typedef ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> > LorentzV  ;
typedef std::vector<LorentzV>                                     LorentzVs ;
typedef std::map<std::string,bool>                                trigger_t ;
typedef std::map<std::string,std::string>                         stringstring ;

#ifdef __CINT__

#pragma link C++ typedef  LorentzV  ;
#pragma link C++ typedef  LorentzVs ;
#pragma link C++ typedef  trigger_t ;
#pragma link C++ class    trigger_t::iterator;
#pragma link C++ class    trigger_t::const_iterator;
#pragma link C++ class    stringstring::iterator;
#pragma link C++ class    stringstring::const_iterator;

#pragma link C++ class    LorentzVs+;
#pragma link C++ class    trigger_t+;
#pragma link C++ class    std::pair<std::string,bool>+;
#pragma link C++ class    std::pair<const std::string,bool>+;
#pragma link C++ class    std::pair<std::string,std::string>+;
#pragma link C++ class    std::pair<const std::string,std::string>+;

#endif

