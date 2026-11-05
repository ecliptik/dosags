# Screen gate (9.2 pre-registration): no fixed timestep, freeze captures; W0 base, W1 lever A, W2 lever A+B, WC control
MMDSGW0 | mmd | AGSWIT2.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |  | nofixed freeze=200,500,900
AQSGW0 | agsquest | AGSWIT2.EXE | 3500 | - | - |  | nofixed freeze=400,1500,3000
5DSGW0 | 5days | AGSWIT2.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345  | nofixed freeze=200,500,900
MMDSGW1 | mmd | AGSL1W2.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |  | nofixed freeze=200,500,900
AQSGW1 | agsquest | AGSL1W2.EXE | 3500 | - | - |  | nofixed freeze=400,1500,3000
5DSGW1 | 5days | AGSL1W2.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345  | nofixed freeze=200,500,900
MMDSGW2 | mmd | AGSL2W2.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |  | nofixed freeze=200,500,900
AQSGW2 | agsquest | AGSL2W2.EXE | 3500 | - | - |  | nofixed freeze=400,1500,3000
5DSGW2 | 5days | AGSL2W2.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345  | nofixed freeze=200,500,900
MMDSGWC | mmd | AGSWIT2.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - | DOSAGS_WIT_PERTURB_TICK=150 | nofixed freeze=200,500,900
AQSGWC | agsquest | AGSWIT2.EXE | 3500 | - | - | DOSAGS_WIT_PERTURB_TICK=300 | nofixed freeze=400,1500,3000
5DSGWC | 5days | AGSWIT2.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345 DOSAGS_WIT_PERTURB_TICK=150 | nofixed freeze=200,500,900
