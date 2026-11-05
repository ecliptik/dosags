# 9.2 determinism guard, baseline arms: W0 twice (baseline is deterministic) and WC (control, must differ)
MMDW0a | mmd      | AGSWIT.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
MMDW0b | mmd      | AGSWIT.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
MMDWC  | mmd      | AGSWIT.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - | DOSAGS_WIT_PERTURB_TICK=300
AQW0a  | agsquest | AGSWIT.EXE | 6000 | -  | - |
AQW0b  | agsquest | AGSWIT.EXE | 6000 | -  | - |
AQWC   | agsquest | AGSWIT.EXE | 6000 | -  | - | DOSAGS_WIT_PERTURB_TICK=500
5DW0a  | 5days    | AGSWIT.EXE | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 |
5DW0b  | 5days    | AGSWIT.EXE | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 |
5DWC   | 5days    | AGSWIT.EXE | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_PERTURB_TICK=300
