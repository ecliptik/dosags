# Lever B (0295): guard W0 (AGSWIT2) vs W2 (AGSL2W2), timing L2, op counts
MMDSW0  | mmd      | AGSWIT2.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
MMDW2   | mmd      | AGSL2W2.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
AQSW0   | agsquest | AGSWIT2.EXE | 6000 | -  | - |
AQW2    | agsquest | AGSL2W2.EXE | 6000 | -  | - |
5DSW2   | 5days    | AGSL2W2.EXE | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345
MMDTL2  | mmd      | AGSL2.EXE   | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
AQTL2   | agsquest | AGSL2.EXE   | 6000 | -  | - |
MMDOCL2 | mmd      | AGSOCL2.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
