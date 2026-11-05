# ags 0305 screen gate (fast conf, fixed timestep, freezes, exclusive, display 261)
MMDSG5MW0 | mmd      | AGSMW3.EXE  | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |  | freeze=200,500,900
AQSG5MW0  | agsquest | AGSMW3.EXE  | 3500 | -  | - |  | freeze=400,1500,3000
5DSG5MW0  | 5days    | AGSMW3.EXE  | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345 | freeze=200,500,900
MMDSG5SBW | mmd      | AGS305W.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |  | freeze=200,500,900
AQSG5SBW  | agsquest | AGS305W.EXE | 3500 | -  | - |  | freeze=400,1500,3000
5DSG5SBW  | 5days    | AGS305W.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345 | freeze=200,500,900
MMDSG5MWC | mmd      | AGSMW3.EXE  | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - | DOSAGS_WIT_PERTURB_TICK=150 | freeze=200,500,900
AQSG5MWC  | agsquest | AGSMW3.EXE  | 3500 | -  | - | DOSAGS_WIT_PERTURB_TICK=300 | freeze=400,1500,3000
5DSG5MWC  | 5days    | AGSMW3.EXE  | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345 DOSAGS_WIT_PERTURB_TICK=150 | freeze=200,500,900
