#include <cmath>
#include <vector>
#include <algorithm>
#include <iostream>

// The specification is Section 4.2 of CMS PAS SUS-09-001
// available at http://cdsweb.cern.ch/record/1194509/files/SUS-09-001-pas.pdf

struct fabs_less { 
  bool operator()(const double x, const double y) const { 
    return fabs(x) < fabs(y); 
  } 
};

double deltaHt(const std::vector<double>& ETs) {
  std::vector<double> diff( 1<<(ETs.size()-1) , 0. );
  for(unsigned i=0; i < diff.size(); i++)
    for(unsigned j=0; j < ETs.size(); j++)
      diff[i] += ETs[j] * ( 1 - 2 * (int(i>>j)&1) ) ;
  return fabs( *min_element( diff.begin(), diff.end(), fabs_less() ) );
}

double alphaT(const double HT, const double DHT, const double MHT) {
  return 0.5 * ( HT - DHT ) / sqrt( HT*HT - MHT*MHT );
}

void test() {
  std::vector<double> ETs;
  ETs.push_back(220.0);
  ETs.push_back(150.0);
  ETs.push_back( 75.0);
  std::cout << alphaT(445.0, deltaHt(ETs), 200.0) << std::endl; //0.553426
}

int main(void) {
  test();
  return 0;
}
