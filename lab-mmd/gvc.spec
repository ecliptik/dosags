# G gate 1 power: VM-level trace control (DOSAGS_VMTRACE_CONTROL flips bit 0 of one engine-call return in AX)
GVC-MMD  | mmd      | AGSBWV.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - | DOSAGS_VMTRACE_CONTROL=300
GVC-AQ   | agsquest | AGSBWV.EXE | 6000 | -  | - | DOSAGS_VMTRACE_CONTROL=500
GVC-5D   | 5days    | AGSBWV.EXE | 2000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345 DOSAGS_VMTRACE_CONTROL=300
GVC-INT  | mmd      | AGSBWV.EXE | 9000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 40 | DOSAGS_VMTRACE_CONTROL=1000
