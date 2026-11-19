# L1 pre-registration (2026-11-06, before any L1 lab data): is MMD's in-play script cost fixed per tick or click-driven?
Baseline, 486, R1 build in play (GCMP, instrumented, fine timing on): script_vm 12.11 ms/tick = 14,041 entries over 7,004
ticks at 6.04 ms each; process_events_dispatch 13.86 ms/tick; rep_exec_wrapper 14,008 calls. So 2.00 entries/tick, with only
~33 entries beyond the two per-tick ones over the whole fixture.
Test (DOSBox-X lab, R1 lab instrumented exe, P9/GC fixture = save 007 + TAS exit 12440, plus lab fixture G): attribute
script_vm time by entry point (repeatedly_execute / repeatedly_execute_always / room rep_exec vs event handlers:
on_mouse_click, interactions, GUI handlers, dialog) and by tick class (no input within +-40 ticks vs the rest).
P1: per-tick entries carry >= 95% of script_vm time (central 98%). Falsifier: < 90%.
P2: script_vm/tick on input-free ticks is within +-10% of the all-tick mean. Falsifier: input-free ticks > 15% lower.
P3 (486 figure L1 is scored against): R1 build in play script_vm 11.0-13.2 ms/tick, central 12.1; the confirmation round's
instrumented cell, if one runs, reads inside it. Falsifier: outside.
If P1+P2 hold: L1 targets what MMD's per-tick scripts do every tick (API calls such as GetLocationName / GetAtScreenXY,
cc_has_error, formatting; docs/lab/MMD-REMAINDER.md rows 2-4) and the VM's per-instruction cost, not click handlers.
If P1 or P2 is falsified: L1 targets the click-driven handlers first. No lever is built before this is answered.
