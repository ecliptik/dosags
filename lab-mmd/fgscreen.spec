# 0297 screen gate (fast conf, fixed timestep, freezes)
MMDSG3MW0 | mmd | AGSMW.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |  | freeze=200,500,900
AQSG3MW0 | agsquest | AGSMW.EXE | 3500 | - | - |  | freeze=400,1500,3000
5DSG3MW0 | 5days | AGSMW.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345  | freeze=200,500,900
MMDSG3FGW | mmd | AGSFGW.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |  | freeze=200,500,900
AQSG3FGW | agsquest | AGSFGW.EXE | 3500 | - | - |  | freeze=400,1500,3000
5DSG3FGW | 5days | AGSFGW.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345  | freeze=200,500,900
MMDSG3MWC | mmd | AGSMW.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - | DOSAGS_WIT_PERTURB_TICK=150 | freeze=200,500,900
AQSG3MWC | agsquest | AGSMW.EXE | 3500 | - | - | DOSAGS_WIT_PERTURB_TICK=300 | freeze=400,1500,3000
5DSG3MWC | 5days | AGSMW.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345 DOSAGS_WIT_PERTURB_TICK=150 | freeze=200,500,900
