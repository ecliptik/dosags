# ags lever M (0307) screen gate (fast conf, fixed timestep, freezes, exclusive, display 261)
MMDSG7MW0 | mmd      | AGSMW4.EXE  | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |  | freeze=200,500,900
AQSG7MW0  | agsquest | AGSMW4.EXE  | 3500 | -  | - |  | freeze=400,1500,3000
5DSG7MW0  | 5days    | AGSMW4.EXE  | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345 | freeze=200,500,900
MMDSG7MMW | mmd      | AGSMW4M.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |  | freeze=200,500,900
AQSG7MMW  | agsquest | AGSMW4M.EXE | 3500 | -  | - |  | freeze=400,1500,3000
5DSG7MMW  | 5days    | AGSMW4M.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345 | freeze=200,500,900
MMDSG7MWC | mmd      | AGSMW4.EXE  | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - | DOSAGS_WIT_PERTURB_TICK=150 | freeze=200,500,900
AQSG7MWC  | agsquest | AGSMW4.EXE  | 3500 | -  | - | DOSAGS_WIT_PERTURB_TICK=300 | freeze=400,1500,3000
5DSG7MWC  | 5days    | AGSMW4.EXE  | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345 DOSAGS_WIT_PERTURB_TICK=150 | freeze=200,500,900
