# 0298 self-test v4 (12.1 amendment 2): immediate re-lookup hits; resident keys snapshotted and checked after the restore
FGST4-MMD | mmd      | AGSFGST4.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - | DOSAGS_FGI_SELFTEST=300
FGST4-AQ  | agsquest | AGSFGST4.EXE | 6000 | -  | - | DOSAGS_FGI_SELFTEST=1900 DOSAGS_FGI_SELFTEST_NOSAVE=1 DOSAGS_FGI_SELFTEST2=2100
FGST4-5D  | 5days    | AGSFGST4.EXE | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_FGI_SELFTEST=300 DOSAGS_WIT_SEED=12345
