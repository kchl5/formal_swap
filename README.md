# Formal Swaps

This is an executable python program which automatically assigns people into groups for the formal swap. 

### Installing

Create conda environment after repo has been cloned
```
conda env create --name formal_swaps --file=formal_swap_env.yml
```

### Executing program

Specify URL of GSheet containing the formal swap information, e.g d/xyz/edit#gid=0 -> url=xyz
```
url=*GSheet-URL* python app.py
```

