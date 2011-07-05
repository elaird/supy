-----------
| License |
-----------
GPLv3 (http://www.gnu.org/licenses/gpl.html)

----------------
| Instructions |
----------------
1) Set up pyROOT:
- use a CMSSW area: cd /somewhere/CMSSW_4_1_3/src && cmsenv
- or see note (A)

2) Check out the code:
- [if needed: export CVSROOT=username@cmscvs.cern.ch:/cvs_server/repositories/CMSSW;export CVS_RSH=ssh]
- cvs co -d supy -r V11-5 UserCode/elaird/supy
- cd supy

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
Please send bug reports to edward.laird@cern.ch.
