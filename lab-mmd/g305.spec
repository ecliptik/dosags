# ags 0305 lab gates (LAB-MMD 16.7), fixed 40000, main 80a6d6f5; timing baseline = SPLREF-MMD (AGSL297)
G305T-MMD  | mmd      | AGS305.EXE  | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
MMD3MW0a   | mmd      | AGSMW3.EXE  | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
MMD3MW0b   | mmd      | AGSMW3.EXE  | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
MMD3SBW    | mmd      | AGS305W.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
MMD3MWC    | mmd      | AGSMW3.EXE  | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - | DOSAGS_WIT_PERTURB_TICK=300
AQ3MW0a    | agsquest | AGSMW3.EXE  | 6000 | -  | - |
AQ3MW0b    | agsquest | AGSMW3.EXE  | 6000 | -  | - |
AQ3SBW     | agsquest | AGS305W.EXE | 6000 | -  | - |
AQ3MWC     | agsquest | AGSMW3.EXE  | 6000 | -  | - | DOSAGS_WIT_PERTURB_TICK=500
5D3MW0a    | 5days    | AGSMW3.EXE  | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345
5D3MW0b    | 5days    | AGSMW3.EXE  | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345
5D3SBW     | 5days    | AGS305W.EXE | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345
5D3MWC     | 5days    | AGSMW3.EXE  | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345 DOSAGS_WIT_PERTURB_TICK=300
