# Screen gate re-run (9.9 amendment): fixed timestep ON (0195 freezes need it), cycles=max conf
MMDSG2W0 | mmd | AGSWIT2.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |  | freeze=200,500,900
AQSG2W0 | agsquest | AGSWIT2.EXE | 3500 | - | - |  | freeze=400,1500,3000
5DSG2W0 | 5days | AGSWIT2.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345  | freeze=200,500,900
MMDSG2W1 | mmd | AGSL1W2.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |  | freeze=200,500,900
AQSG2W1 | agsquest | AGSL1W2.EXE | 3500 | - | - |  | freeze=400,1500,3000
5DSG2W1 | 5days | AGSL1W2.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345  | freeze=200,500,900
MMDSG2W2 | mmd | AGSL2W2.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |  | freeze=200,500,900
AQSG2W2 | agsquest | AGSL2W2.EXE | 3500 | - | - |  | freeze=400,1500,3000
5DSG2W2 | 5days | AGSL2W2.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345  | freeze=200,500,900
MMDSG2WC | mmd | AGSWIT2.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - | DOSAGS_WIT_PERTURB_TICK=150 | freeze=200,500,900
AQSG2WC | agsquest | AGSWIT2.EXE | 3500 | - | - | DOSAGS_WIT_PERTURB_TICK=300 | freeze=400,1500,3000
5DSG2WC | 5days | AGSWIT2.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345 DOSAGS_WIT_PERTURB_TICK=150 | freeze=200,500,900
