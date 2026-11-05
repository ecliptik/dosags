# G (0299) screen gate (14, gate 6): fast conf, fixed timestep, freezes; BW base witness, GW G witness, BWC control
GSG-MMDBW0 | mmd | AGSBW.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |  | freeze=200,500,900
GSG-AQBW0 | agsquest | AGSBW.EXE | 3500 | - | - |  | freeze=400,1500,3000
GSG-5DBW0 | 5days | AGSBW.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345  | freeze=200,500,900
GSG-INTBW0 | mmd | AGSBW.EXE | 9000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 40 |  | freeze=2000,5000,8000
GSG-MMDGW | mmd | AGSGW.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - |  | freeze=200,500,900
GSG-AQGW | agsquest | AGSGW.EXE | 3500 | - | - |  | freeze=400,1500,3000
GSG-5DGW | 5days | AGSGW.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345  | freeze=200,500,900
GSG-INTGW | mmd | AGSGW.EXE | 9000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 40 |  | freeze=2000,5000,8000
GSG-MMDBWC | mmd | AGSBW.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | - | DOSAGS_WIT_PERTURB_TICK=150 | freeze=200,500,900
GSG-AQBWC | agsquest | AGSBW.EXE | 3500 | - | - | DOSAGS_WIT_PERTURB_TICK=300 | freeze=400,1500,3000
GSG-5DBWC | 5days | AGSBW.EXE | 1000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 3 | DOSAGS_WIT_SEED=12345 DOSAGS_WIT_PERTURB_TICK=150 | freeze=200,500,900
GSG-INTBWC | mmd | AGSBW.EXE | 9000 | /home/claude/git/dosags-lab-mmd/lab-mmd/cfg/ACSETUP.CFG | --startr 40 | DOSAGS_WIT_PERTURB_TICK=1000 | freeze=2000,5000,8000
