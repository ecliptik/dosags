# 0297 lab gates (12.1): self-test (0298), timing, determinism (fixed 40000)
FGST-MMD | mmd      | AGSFGST.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - | DOSAGS_FGI_SELFTEST=300
FGST-AQ  | agsquest | AGSFGST.EXE | 6000 | -  | - | DOSAGS_FGI_SELFTEST=500
FGST-5D  | 5days    | AGSFGST.EXE | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_FGI_SELFTEST=300 DOSAGS_WIT_SEED=12345
FGTB-MMD | mmd      | AGSM1.EXE   | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
FGT-MMD  | mmd      | AGSFG.EXE   | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
FGTB-AQ  | agsquest | AGSM1.EXE   | 6000 | -  | - |
FGT-AQ   | agsquest | AGSFG.EXE   | 6000 | -  | - |
MMDMW0a  | mmd      | AGSMW.EXE   | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
MMDMW0b  | mmd      | AGSMW.EXE   | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
MMDFGW   | mmd      | AGSFGW.EXE  | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
MMDMWC   | mmd      | AGSMW.EXE   | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - | DOSAGS_WIT_PERTURB_TICK=300
AQMW0a   | agsquest | AGSMW.EXE   | 6000 | -  | - |
AQMW0b   | agsquest | AGSMW.EXE   | 6000 | -  | - |
AQFGW    | agsquest | AGSFGW.EXE  | 6000 | -  | - |
AQMWC    | agsquest | AGSMW.EXE   | 6000 | -  | - | DOSAGS_WIT_PERTURB_TICK=500
5DMW0a   | 5days    | AGSMW.EXE   | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345
5DMW0b   | 5days    | AGSMW.EXE   | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345
5DFGW    | 5days    | AGSFGW.EXE  | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345
5DMWC    | 5days    | AGSMW.EXE   | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345 DOSAGS_WIT_PERTURB_TICK=300
