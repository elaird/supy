-----------
| License |
-----------
GPLv3 (http://www.gnu.org/licenses/gpl.html)

----------------
| Instructions |
----------------
1) Set up pyROOT:
- use a CMSSW area: cd /somewhere/CMSSW_4_2_8/src && cmsenv
- or see note (A)

2) Check out the code (try branch 'eps' or 'master')
- git clone https://github.com/elaird/supy.git
- cd supy
- git checkout <branchname>

3) Run it!
- ./supy analyses/example.py --loop 1

---------
| Notes |
---------
(A) ROOT (>=5.27.06) and python (>=2.6) are required; CMSSW is not.  These are useful pages for setting up and learning pyROOT:
http://root.cern.ch/drupal/content/how-use-use-python-pyroot-interpreter
http://wlav.web.cern.ch/wlav/pyroot/

(B) A std::vector<bool> stored in a TTree is not yet supported.

(C) TTrees with multiple leaves per branch are not yet supported.

--------
| Bugs |
--------
Please report problems at https://github.com/elaird/supy/issues or contact edward dot laird at cern dot ch.
