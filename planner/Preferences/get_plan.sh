#/usr/bin/env bash

# path to fast downward #
FD_PATH=$(locate fast-downward.py | head -n 1)

# find optimal plan using fd on input domain and problem #
rm -f output output.sas sas_plan
#timeout 10s ${FD_PATH} $1 $2 --search "astar(lmcut())" | grep -e \([0-9]\) | awk '{$NF=""; print $0}'
timeout 2s ${FD_PATH} $1 $2 --search "astar(hm(m=$3))" > /dev/null #| grep  "Simplified to trivially false goal" #> /dev/null #| grep -e \([0-9]\) | awk '{$NF=""; print $0}'
if [ $? -eq 124 ]; then echo -e "(dummy)\n; cost = 15 (general cost)"; echo -e "(dummy)\n; cost = 15 (general cost)" > sas_plan ;
elif ${FD_PATH} $1 $2 --search "astar(hm(m=$3))" | grep "Solution found.">/dev/null; then echo -e "Solution found.";
fi
#if [[ $(${FD_PATH} $1 $2 --search "astar(hm(m=$3))" | grep "Solution found.") = "" ]]; then echo -e "Solution found.";echo -e "Solution found.">sas_plan;
#fi