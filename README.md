# edf_topology_analysis

Prerequistes:
```
pip install -U matplotlib
pip install networkx
```

Usage:
put the script alongside one of the following repository:
  - 021774092604_lu
  - 021774092604_lu
  - 021874091558_lu

and then run command 
```
python analyse.py name_of_edf_topology_repository
python addConcentrator.py name_of_edf_topology_repository
```

NOTE:
In indicateurs-adp-k/indicateurs-adp-k.log, there is a null character for entry AdpSoftVersion in the end, which leads to malfunction of json library. Please remove the null character and everything should work.
