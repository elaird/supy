if [ $HOSTNAME == "lx05.hep.ph.ic.ac.uk" ]
    then
    export LD_LIBRARY_PATH=/vols/cms/grid/dcap:/vols/grid/glite/ui/current/d-cache/dcap/lib:$LD_LIBRARY_PATH
fi

if [ $HOSTNAME == "lx06.hep.ph.ic.ac.uk" ]
    then
    export LD_LIBRARY_PATH=/vols/cms/grid/dcap:/vols/grid/glite/ui/current/d-cache/dcap/lib:$LD_LIBRARY_PATH
fi

export PYTHONPATH=${PYTHONPATH}:${PWD}
