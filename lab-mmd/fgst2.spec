# 0298 self-test v2: first tick >= N outside a script; AGS Quest after its own AutoPilot save/restore (no forced save)
FGST2-MMD | mmd      | AGSFGST2.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - | DOSAGS_FGI_SELFTEST=300
FGST2-AQ  | agsquest | AGSFGST2.EXE | 6000 | -  | - | DOSAGS_FGI_SELFTEST=2100 DOSAGS_FGI_SELFTEST_NOSAVE=1
FGST2-5D  | 5days    | AGSFGST2.EXE | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_FGI_SELFTEST=300 DOSAGS_WIT_SEED=12345
