# API early-out read-first: counts (0296 probe, ablation off) and ABLATION arms (cost measurement only, fixed 40000)
APIB     | mmd      | AGSM1.EXE  | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
APIC0    | mmd      | AGSAPI.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |
APICF    | mmd      | AGSAPI.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - | DOSAGS_ABL_FGI=1
APICS1   | mmd      | AGSAPI.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - | DOSAGS_ABL_SBP=1
APICS2   | mmd      | AGSAPI.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - | DOSAGS_ABL_SBP=2
APICAQ   | agsquest | AGSAPI.EXE | 6000 | -  | - |
APIC5D   | 5days    | AGSAPI.EXE | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 |
