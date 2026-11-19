(restart_savegame_ms: the trace header in SW cells; else the STDOUT line or, for 5days, the journey write_ms)
| cell | prior (B) | save (B) | sha256[:12] | restart_savegame_ms | int21 n / ms | stdio fwrite ms | fseek ms | open / close ms | bracket - int21 (CPU-side) ms | dry run |
|---|---|---|---|---|---|---|---|---|---|---|
| MM-cpu | 146822 | 146822 | db6d2347575a | 160 (trace) | 146 / 2.9 | 2.626 | 3.911 | 0.246 / 0.220 | 157.6 | dry=off |
| MM-dry | 146822 | 146822 | db6d2347575a | 261 (trace) | 146 / 104.2 | 21.419 | 82.391 | 1.399 / 3.099 | 157.6 | dry=on dry_ms=89.309 dry_bytes=146822 disk_bytes=146822 dry_equal=1 |
| MM-drycpu | 146822 | 146822 | db6d2347575a | 160 (trace) | 146 / 2.9 | 2.622 | 3.908 | 0.246 / 0.221 | 157.6 | dry=on dry_ms=89.309 dry_bytes=146822 disk_bytes=146822 dry_equal=1 |
| MM-new | - | 146822 | db6d2347575a | 271 (trace) | 152 / 114.0 | 23.713 | 87.431 | 1.751 / 5.402 | 157.7 | dry=off |
| MM-off | 146822 | 146822 | db6d2347575a | 236 | (off) | | | | | |
| MM-offcpu | 146822 | 146822 | db6d2347575a | 125 | (off) | | | | | |
| MM-same | 146822 | 146822 | db6d2347575a | 266 (trace) | 146 / 109.2 | 25.031 | 84.582 | 1.756 / 1.939 | 157.6 | dry=off |
| S16-dry | 59538 | 59538 | 80350c1030a2 | 171 (trace) | 117 / 82.3 | 6.955 | 70.131 | 1.643 / 5.942 | 89.3 | dry=on dry_ms=56.894 dry_bytes=59538 disk_bytes=59538 dry_equal=1 |
| S16-new | - | 59538 | 80350c1030a2 | 171 (trace) | 123 / 82.2 | 6.690 | 69.440 | 2.643 / 5.943 | 89.4 | dry=off |
| S16-off | 59538 | 59538 | 80350c1030a2 | 154 | (off) | | | | | |
| S16-same | 59538 | 59538 | 80350c1030a2 | 172 (trace) | 117 / 83.3 | 7.048 | 71.080 | 1.644 / 5.943 | 89.3 | dry=off |
| S32-cpu | 59538 | 59538 | ab2b12a0445b | 89 (trace) | 117 / 2.3 | 0.903 | 3.290 | 0.246 / 0.223 | 87.5 | dry=off |
| S32-dry | 59538 | 59538 | ab2b12a0445b | 169 (trace) | 117 / 82.2 | 7.193 | 70.399 | 1.633 / 5.307 | 87.4 | dry=on dry_ms=54.289 dry_bytes=59538 disk_bytes=59538 dry_equal=1 |
| S32-drycpu | 59538 | 59538 | ab2b12a0445b | 89 (trace) | 117 / 2.3 | 0.904 | 3.290 | 0.246 / 0.224 | 87.5 | dry=on dry_ms=54.289 dry_bytes=59538 disk_bytes=59538 dry_equal=1 |
| S32-new | - | 59538 | b31841d31503 | 168 (trace) | 123 / 81.0 | 7.407 | 67.463 | 2.637 / 5.942 | 87.6 | dry=off |
| S32-new2 | - | 59538 | ab2b12a0445b | 168 (trace) | 123 / 81.0 | 7.452 | 67.427 | 2.632 / 5.942 | 87.6 | dry=off |
| S32-off | 59538 | 59538 | ab2b12a0445b | 151 | (off) | | | | | |
| S32-offcpu | 59538 | 59538 | ab2b12a0445b | 71 | (off) | | | | | |
| S32-same | 59538 | 59538 | ebf94307c744 | 168 (trace) | 117 / 81.2 | 7.406 | 68.543 | 1.637 / 5.942 | 87.5 | dry=off |
| S32-same2 | 59538 | 59538 | ab2b12a0445b | 172 (trace) | 117 / 85.2 | 7.406 | 74.367 | 1.633 / 4.133 | 87.4 | dry=off |
| S32-shrink | 146822 | 59538 | ab2b12a0445b | 166 (trace) | 117 / 79.1 | 7.409 | 66.509 | 1.632 / 5.942 | 87.5 | dry=off |
| S8-cpu | 61199 | 61199 | c19cb511d7c0 | 86 (trace) | 117 / 2.3 | 0.920 | 3.310 | 0.247 / 0.221 | 84.3 | dry=off |
| S8-dry | 61199 | 61199 | c19cb511d7c0 | 95 (trace) | 117 / 11.1 | 2.923 | 9.861 | 0.379 / 0.329 | 84.3 | dry=on dry_ms=51.263 dry_bytes=61199 disk_bytes=61199 dry_equal=1 |
| S8-drycpu | 61199 | 61199 | c19cb511d7c0 | 86 (trace) | 117 / 2.3 | 0.916 | 3.308 | 0.246 / 0.221 | 84.3 | dry=on dry_ms=51.264 dry_bytes=61199 disk_bytes=61199 dry_equal=1 |
| S8-grow | 59538 | 61199 | c19cb511d7c0 | 95 (trace) | 117 / 11.1 | 2.924 | 9.859 | 0.379 / 0.329 | 84.3 | dry=off |
| S8-new | - | 61199 | 6b4e00913fe3 | 95 (trace) | 123 / 11.2 | 2.925 | 9.762 | 0.721 / 0.329 | 84.4 | dry=off |
| S8-new2 | - | 61199 | c19cb511d7c0 | 95 (trace) | 123 / 11.3 | 2.920 | 9.797 | 0.729 / 0.329 | 84.4 | dry=off |
| S8-off | 61199 | 61199 | c19cb511d7c0 | 77 | (off) | | | | | |
| S8-offcpu | 61199 | 61199 | c19cb511d7c0 | 68 | (off) | | | | | |
| S8-same | 61199 | 61199 | c19cb511d7c0 | 95 (trace) | 117 / 11.1 | 2.927 | 9.863 | 0.380 / 0.329 | 84.3 | dry=off |
