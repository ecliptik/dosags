# Lever G (0299) gates, fixed 40000: trace-digest equivalence (BW = base+0297+0292+0302, GW = +0299+0303),
# baseline twice, control, save/restore arms; MMD-INTRO = --startr 40 (the intro's own room chain, no input)
GMMD-BW0a | mmd      | AGSBW.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
GMMD-BW0b | mmd      | AGSBW.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
GMMD-GW   | mmd      | AGSGW.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
GMMD-BWC  | mmd      | AGSBW.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - | DOSAGS_WIT_PERTURB_TICK=300
GMMD-BWSR | mmd      | AGSBW.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - | DOSAGS_WIT_SAVERESTORE_TICK=400
GMMD-GWSR | mmd      | AGSGW.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - | DOSAGS_WIT_SAVERESTORE_TICK=400
GAQ-BW0a  | agsquest | AGSBW.EXE | 6000 | -  | - |
GAQ-BW0b  | agsquest | AGSBW.EXE | 6000 | -  | - |
GAQ-GW    | agsquest | AGSGW.EXE | 6000 | -  | - |
GAQ-BWC   | agsquest | AGSBW.EXE | 6000 | -  | - | DOSAGS_WIT_PERTURB_TICK=500
G5D-BW0a  | 5days    | AGSBW.EXE | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345
G5D-BW0b  | 5days    | AGSBW.EXE | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345
G5D-GW    | 5days    | AGSGW.EXE | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345
G5D-BWC   | 5days    | AGSBW.EXE | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345 DOSAGS_WIT_PERTURB_TICK=300
G5D-BWSR  | 5days    | AGSBW.EXE | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345 DOSAGS_WIT_SAVERESTORE_TICK=800
G5D-GWSR  | 5days    | AGSGW.EXE | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345 DOSAGS_WIT_SAVERESTORE_TICK=800
GINT-BW0a | mmd      | AGSBW.EXE | 9000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 40 |
GINT-BW0b | mmd      | AGSBW.EXE | 9000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 40 |
GINT-GW   | mmd      | AGSGW.EXE | 9000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 40 |
GINT-BWC  | mmd      | AGSBW.EXE | 9000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 40 | DOSAGS_WIT_PERTURB_TICK=1000
GINT-BWSR | mmd      | AGSBW.EXE | 9000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 40 | DOSAGS_WIT_SAVERESTORE_TICK=7000
GINT-GWSR | mmd      | AGSGW.EXE | 9000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 40 | DOSAGS_WIT_SAVERESTORE_TICK=7000
GT-MMD-B  | mmd      | AGSFG.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
GT-MMD-G  | mmd      | AGSG1.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
GT-AQ-B   | agsquest | AGSFG.EXE | 6000 | -  | - |
GT-AQ-G   | agsquest | AGSG1.EXE | 6000 | -  | - |
