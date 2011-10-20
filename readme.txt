-----------
| License |
-----------
GPLv3 (http://www.gnu.org/licenses/gpl.html)

---------------
| Quick Start |
---------------
1) Set up pyROOT:
- use a CMSSW area: cd /somewhere/CMSSW_4_2_8/src && cmsenv
- or see note (A)

2) Clone the repository:
git clone git://github.com/elaird/supy.git
#  or, if you have forked it,
git clone git://github.com/your_username/supy.git
cd supy

3) Run it!
- ./supy analyses/example.py --loop 1

---------------------
| Brief Description |
---------------------
To be written.

----------------
| Dependencies |
----------------
ROOT (>=5.27.06) and python (>=2.6) are required; CMSSW is not.  These
are useful pages for setting up and learning pyROOT:
http://root.cern.ch/drupal/content/how-use-use-python-pyroot-interpreter
http://wlav.web.cern.ch/wlav/pyroot/

-----------
| Gotchas |
-----------
- TTrees with multiple leaves per branch are not yet supported.

- A std::vector<bool> stored in a TTree is not yet supported.

- Creating a Lorentz vector every event is slow.  As a workaround, use
  core.utils.LorentzV (see calculables.Jet.SumP4 for an example).

- Iterating through a std::map<string, bool> is slow.  Consider using
  a cache (see steps.Trigger.Counts for an example).

--------
| Bugs |
--------
Please report problems at https://github.com/elaird/supy/issues
