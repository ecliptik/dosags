## G1 byte equality (SAVEMEM=0 vs =1)

| fixture | file | =0 sha256 (size) | =1 sha256 (size) | equal | =0 witness | =1 witness |
|---|---|---|---|---|---|---|
| S32P | AGSSAVE.999 | ab2b12a0445b22bb3c4caf43bb63a6022795dc1154d52bafce00c287bea2a0e9 (59538) | ab2b12a0445b22bb3c4caf43bb63a6022795dc1154d52bafce00c287bea2a0e9 (59538) | EQUAL | mode=0 slot=999 path=stream bytes=0 mem=0 fallback=0 stream=1 short=0 failknob=0 | mode=1 slot=999 path=mem bytes=59538 mem=1 fallback=0 stream=0 short=0 failknob=0 |
| S16 | AGSSAVE.999 | 80350c1030a205213aeaac3af3c388859a92492d6a3668372a1c46676b7d767e (59538) | 80350c1030a205213aeaac3af3c388859a92492d6a3668372a1c46676b7d767e (59538) | EQUAL | mode=0 slot=999 path=stream bytes=0 mem=0 fallback=0 stream=1 short=0 failknob=0 | mode=1 slot=999 path=mem bytes=59538 mem=1 fallback=0 stream=0 short=0 failknob=0 |
| S8 Trilby r35 | AGSSAVE.999 | c19cb511d7c077c9f793074ed256f2633a070ada2e782679f3349e32ab5bc47a (61199) | c19cb511d7c077c9f793074ed256f2633a070ada2e782679f3349e32ab5bc47a (61199) | EQUAL | mode=0 slot=999 path=stream bytes=0 mem=0 fallback=0 stream=1 short=0 failknob=0 | mode=1 slot=999 path=mem bytes=61199 mem=1 fallback=0 stream=0 short=0 failknob=0 |
| MMD title | AGSSAVE.999 | db6d2347575ae8c6b10435ac75b63b67eba92609a3c56c544b272d211d06e64c (146822) | db6d2347575ae8c6b10435ac75b63b67eba92609a3c56c544b272d211d06e64c (146822) | EQUAL | mode=0 slot=999 path=stream bytes=0 mem=0 fallback=0 stream=1 short=0 failknob=0 | mode=1 slot=999 path=mem bytes=146822 mem=1 fallback=0 stream=0 short=0 failknob=0 |
| G: normal save slot 1 (deflated) | AGSSAVE.001 | 360d7df1604efe75d16effe79457ac4889deffa8b9c6f219fa7450524e0844fc (13552) | 360d7df1604efe75d16effe79457ac4889deffa8b9c6f219fa7450524e0844fc (13552) | EQUAL | mode=0 slot=1 path=stream bytes=0 mem=0 fallback=0 stream=1 short=0 failknob=0 | mode=1 slot=1 path=mem bytes=13552 mem=1 fallback=0 stream=0 short=0 failknob=0 |

## G3 game output lines and frame digest (=0 vs =1)

- results/R-S32-m0 19 lines | results/R-S32-m1 19 lines | EQUAL
- results/R-S16-m0 19 lines | results/R-S16-m1 19 lines | EQUAL
- results/R-S8-m0 27 lines | results/R-S8-m1 27 lines | EQUAL
- results/R-MM-m0 27 lines | results/R-MM-m1 27 lines | EQUAL
- results/I-G-m0 35 lines | results/I-G-m1 35 lines | EQUAL
- frame digest, fixture G: results/I-G-m0: 3194 records, 3164 loop counters / results/I-G-m1: 3194 records, common lc 3164, EQUAL 3164, DIFF 0

## G4 forced fallback (DOSAGS_LAB_SAVEMEM_FAIL)

| cell | file | OFF (=0) sha256 | ON (=1) sha256 | fallback sha256 | equal to OFF | equal to ON | witness |
|---|---|---|---|---|---|---|---|
| I-S8-f1 | AGSSAVE.999 | c19cb511d7c077c9 | c19cb511d7c077c9 | c19cb511d7c077c9 | EQUAL | EQUAL | mode=1 slot=999 path=fallback bytes=61199 mem=0 fallback=1 stream=0 short=0 failknob=1 |
| I-S8-f2 | AGSSAVE.999 | c19cb511d7c077c9 | c19cb511d7c077c9 | c19cb511d7c077c9 | EQUAL | EQUAL | mode=1 slot=999 path=fallback bytes=61199 mem=0 fallback=1 stream=0 short=0 failknob=2 |
| I-Gs-f1 | AGSSAVE.001 | 360d7df1604efe75 | 360d7df1604efe75 | 360d7df1604efe75 | EQUAL | EQUAL | mode=1 slot=1 path=fallback bytes=13552 mem=0 fallback=1 stream=0 short=0 failknob=1 |
| I-Gs-f2 | AGSSAVE.001 | 360d7df1604efe75 | 360d7df1604efe75 | 360d7df1604efe75 | EQUAL | EQUAL | mode=1 slot=1 path=fallback bytes=13552 mem=0 fallback=1 stream=0 short=0 failknob=2 |

## G2 round trips (save with X, restore with Y; vs 0/0)

- results/R-S8R-00 18 lines | results/R-S8R-10 18 lines | EQUAL
- results/R-S8R-00 18 lines | results/R-S8R-01 18 lines | EQUAL
- results/R-S8R-00 18 lines | results/R-S8R-11 18 lines | EQUAL
- results/I-GR-00 9 lines | results/I-GR-10 9 lines | EQUAL
- results/I-GR-00 9 lines | results/I-GR-01 9 lines | EQUAL
- results/I-GR-00 9 lines | results/I-GR-11 9 lines | EQUAL
- frame digest, slot-1 restores: results/I-GR-00: 1115 records, 1100 loop counters / results/I-GR-10: 1115 records, common lc 1100, EQUAL 1100, DIFF 0 / results/I-GR-01: 1115 records, common lc 1100, EQUAL 1100, DIFF 0 / results/I-GR-11: 1115 records, common lc 1100, EQUAL 1100, DIFF 0

## stamps

- I-G-m0: binary_sha12=c72796d35101 build_dirty=1
- I-G-m1: binary_sha12=c72796d35101 build_dirty=1
- I-GR-00: binary_sha12=c72796d35101 build_dirty=1
- I-GR-01: binary_sha12=c72796d35101 build_dirty=1
- I-GR-10: binary_sha12=c72796d35101 build_dirty=1
- I-GR-11: binary_sha12=c72796d35101 build_dirty=1
- I-Gs-f1: binary_sha12=c72796d35101 build_dirty=1
- I-Gs-f2: binary_sha12=c72796d35101 build_dirty=1
- I-MM-m1sw: binary_sha12=c72796d35101 build_dirty=1
- I-S32-m1sw: binary_sha12=c72796d35101 build_dirty=1
- I-S8-f1: binary_sha12=c72796d35101 build_dirty=1
- I-S8-f2: binary_sha12=c72796d35101 build_dirty=1
- I-S8-m0sw: binary_sha12=c72796d35101 build_dirty=1
- R-MM-m0: binary_sha12=761f64ceccac build_dirty=1
- R-MM-m1: binary_sha12=761f64ceccac build_dirty=1
- R-S16-m0: binary_sha12=761f64ceccac build_dirty=1
- R-S16-m1: binary_sha12=761f64ceccac build_dirty=1
- R-S32-m0: binary_sha12=761f64ceccac build_dirty=1
- R-S32-m1: binary_sha12=761f64ceccac build_dirty=1
- R-S8-m0: binary_sha12=761f64ceccac build_dirty=1
- R-S8-m1: binary_sha12=761f64ceccac build_dirty=1
- R-S8R-00: binary_sha12=761f64ceccac build_dirty=1
- R-S8R-01: binary_sha12=761f64ceccac build_dirty=1
- R-S8R-10: binary_sha12=761f64ceccac build_dirty=1
- R-S8R-11: binary_sha12=761f64ceccac build_dirty=1
