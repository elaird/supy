-----------
| License |
-----------
GPLv3 (http://www.gnu.org/licenses/gpl.html)

----------------
| Instructions |
----------------
0) Set up pyROOT:
- use a CMSSW area:  cd /somewhere/CMSSW_3_8_1_patch2/src && cmsenv
- or see note (A)

1) Check out the code:
- cvs co -d supy -r V9-1 UserCode/elaird/supy
- cd supy

2) (required only if running from dcache at IC) Use better dcap libraries:
- source fixdcap.sh

3) Run it!
- ./supy analyses/example.py --loop 1

---------
| Notes |
---------
(A) ROOT and python are required; CMSSW is not.  These are useful pages for setting up and learning pyROOT:
http://root.cern.ch/drupal/content/how-use-use-python-pyroot-interpreter
http://wlav.web.cern.ch/wlav/pyroot/

(B) A std::vector<bool> stored in a TTree is not yet supported.

(C) TTrees with multiple leaves per branch are not yet supported.

--------
| Bugs |
--------
Please send bug reports to edward.laird@cern.ch.
