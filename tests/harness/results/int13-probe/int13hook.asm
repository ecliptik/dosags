; int13hook.asm -- a real-mode INT 13h timing stub, installed by a DJGPP
; program into DOS memory it allocates itself. Assembled flat with nasm and
; embedded in the probe as a byte array, so there is no separate TSR binary
; and no second toolchain.
;
; WHY NOT DPMI INTERCEPTION: hooking the real-mode vector from protected mode
; needs a real-mode callback, which is a mode transition on EVERY call. The
; instrument would become the cost. This stub runs entirely in real/V86 mode
; and costs a few port reads per call.
;
; WHY NOT uclock(): it is DJGPP libc and is not callable from a real-mode
; interrupt handler.
;
; THE TIMESTAMP COMPOSES, IT DOES NOT DISCARD. PIT counter 0 wraps every
; 54.9 ms and the phenomenon being hunted is ~220 ms -- FOUR wraps. An
; earlier design discarded wrapped records, which would have thrown away
; 100% of the events and returned a clean, guarded, wrong answer. So:
; BIOS tick at 0040:006C is the high word, (65536 - PIT counter) is the low
; word, giving an unbounded monotonic count at ~0.838 us per unit. The
; tick/latch/tick re-read resolves the race against the BIOS tick ISR.
;
; THE COUNTER COUNTS DOWN. PIT channel 0 in mode 3 counts 65535->0 and the
; tick fires at the wrap, so elapsed-within-tick is (65536 - counter).

BITS 16
ORG 0

; ---------------------------------------------------------------------------
; DATA -- fixed offsets, read directly by the DJGPP side via dosmemget.
; ---------------------------------------------------------------------------
old_off:    dw 0            ; +0x00  original INT 13h vector
old_seg:    dw 0            ; +0x02
total_lo:   dw 0            ; +0x04  total calls seen (32-bit)
total_hi:   dw 0            ; +0x06
slow_lo:    dw 0            ; +0x08  calls at or over threshold
slow_hi:    dw 0            ; +0x0A
thresh_lo:  dw 0            ; +0x0C  threshold in PIT units
thresh_hi:  dw 0            ; +0x0E
ring_head:  dw 0            ; +0x10  next slot index
ring_max:   dw 0            ; +0x12  slot count, set by the installer
t0_lo:      dw 0            ; +0x14  scratch
t0_hi:      dw 0            ; +0x16
in_ax:      dw 0            ; +0x18  scratch: the call's input registers
in_cx:      dw 0            ; +0x1A
in_dx:      dw 0            ; +0x1C
busy:       dw 0            ; +0x1E  reentrancy guard
hdl_off:    dw handler      ; +0x20  entry point, read by the installer
ring_off:   dw ring_start   ; +0x22  ring base, read by the installer
rec_size:   dw 16           ; +0x24  bytes per record
hist_off:   dw 0            ; +0x26  cylinder histogram base, set by installer
wring_off:  dw 0            ; +0x28  raw write-address ring base
wring_head: dw 0            ; +0x2A  next slot
wring_max:  dw 0            ; +0x2C  slot count
ret_fl:     dw 0            ; +0x2E  flags the downstream handler returned.
                            ; APPENDED, not inserted: putting it after in_dx
                            ; shifted busy/hdl_off/ring_off and the C side
                            ; then read `busy` as the handler entry and got
                            ; 0x0000. Header cells are an ABI; append only.

; THE RING GOES AFTER THE CODE, NOT AT A GUESSED FIXED OFFSET. The first
; version of this file put it at 0x40, which is INSIDE the handler -- the
; first recorded slow call would have overwritten the code that recorded it.
; Caught by reading the listing rather than by a crash on the target, which
; is the whole reason for assembling and inspecting before it ships.

times 0x30-($-$$) db 0

; ---------------------------------------------------------------------------
; read_ts -- composed timestamp into DX:AX. Clobbers AX, DX only.
; ---------------------------------------------------------------------------
read_ts:
    push ds
    push cx
    push bx
    mov  ax, 0x40
    mov  ds, ax
.retry:
    mov  cx, [0x6C]         ; BIOS tick, low word
    mov  al, 0              ; latch counter 0
    out  0x43, al
    in   al, 0x40
    mov  bl, al
    in   al, 0x40
    mov  bh, al             ; BX = counter (counts down)
    cmp  cx, [0x6C]
    jne  .retry             ; the tick moved under us -- re-read
    mov  ax, bx
    neg  ax                 ; AX = 65536 - counter = elapsed within the tick
    mov  dx, cx             ; DX = tick low word
    pop  bx
    pop  cx
    pop  ds
    ret

; ---------------------------------------------------------------------------
; handler -- the installed INT 13h vector.
; ---------------------------------------------------------------------------
handler:
    ; REENTRANCY: a nested INT 13h would corrupt the scratch slots. Chain
    ; straight through if we are already inside one, and count nothing --
    ; a wrong record is worse than a missing one, and the total-call counter
    ; is what the probe uses to prove the hook is live.
    cmp  word [cs:busy], 0
    je   .take
    jmp  far [cs:old_off]

.take:
    inc  word [cs:busy]
    mov  [cs:in_ax], ax
    mov  [cs:in_cx], cx
    mov  [cs:in_dx], dx

    push ax
    push dx
    call read_ts
    mov  [cs:t0_lo], ax
    mov  [cs:t0_hi], dx
    pop  dx
    pop  ax

    ; ----- the original call, with the caller's registers intact -----
    pushf
    call far [cs:old_off]
    ; AX AND THE FLAGS ARE THE RESULT AND MUST REACH THE CALLER UNCHANGED.
    ; Captured into CS memory the instant the call returns, and pushed back
    ; as the very last act before retf. The first version relied on a
    ; pushf/popf pair spanning the epilogue and leaked PF and AF -- caught by
    ; the register-transparency gate on its first run. CF, ZF, IF and DF were
    ; preserved, so nothing the BIOS or DOS acts on was ever wrong, but "no
    ; caller reads PF" is a claim about SMARTDRV and DOS's FAT layer, whose
    ; source we do not have. Fixed rather than documented.
    pushf
    pop  word [cs:ret_fl]
    push ax
    push cx
    push dx
    push bx                 ; BX IS A RETURN REGISTER for some INT 13h
                            ; functions (AH=08h returns BL=drive type). The
                            ; first version clobbered it on the slow path and
                            ; would have corrupted those calls' results --
                            ; found by reading the register usage, not by a
                            ; failure on the target.

    call read_ts
    sub  ax, [cs:t0_lo]
    sbb  dx, [cs:t0_hi]     ; DX:AX = delta in PIT units

    ; total++
    add  word [cs:total_lo], 1
    adc  word [cs:total_hi], 0

    ; EVERY WRITE COUNTED BY CYLINDER -- the denominator.
    ; The ring records only SLOW calls, which is a numerator with no
    ; population: if the file lives in cylinders 730-737 then every write
    ; went there and "twelve of fourteen stalls were there" is arithmetic,
    ; not clustering. What the erase-block question needs is stalls PER
    ; WRITE by region, so all AH=03 calls are histogrammed here.
    push bx
    push ax
    cmp  byte [cs:in_ax+1], 0x03    ; AH == 03h, disk write?
    jne  .nohist
    cmp  word [cs:hist_off], 0
    je   .nohist
    mov  bx, [cs:in_cx]
    mov  ah, bl
    and  ah, 0xC0
    shr  ah, 1
    shr  ah, 1
    shr  ah, 1
    shr  ah, 1
    shr  ah, 1
    shr  ah, 1                      ; AH = cylinder high bits (0-3)
    mov  al, bh                     ; AL = cylinder low 8 bits
    cmp  ah, 4
    jae  .nohist                    ; out of the 1024-cylinder table
    shl  ax, 1                      ; word index
    add  ax, [cs:hist_off]
    mov  bx, ax
    inc  word [cs:bx]
    ; RAW ADDRESS RING, alongside the histogram. The histogram is an
    ; AGGREGATE and its first outing was wrong -- an un-zeroed block gave
    ; 17.6 million writes against 1,430 calls. This records the addresses
    ; themselves for the first N writes, so the extent can be read from raw
    ; records rather than from the aggregation step that failed. Not
    ; independent of the hook, but independent of the part that was wrong,
    ; and the two must agree.
    mov  bx, [cs:wring_head]
    cmp  bx, [cs:wring_max]
    jae  .nohist
    cmp  word [cs:wring_off], 0
    je   .nohist
    push dx
    mov  ax, bx
    shl  ax, 1
    shl  ax, 1
    add  ax, [cs:wring_off]
    mov  bx, ax
    mov  ax, [cs:in_cx]
    mov  [cs:bx], ax
    mov  ax, [cs:in_dx]
    mov  [cs:bx+2], ax
    inc  word [cs:wring_head]
    pop  dx
.nohist:
    pop  ax
    pop  bx

    ; delta >= threshold ?
    cmp  dx, [cs:thresh_hi]
    ja   .slow
    jb   .done
    cmp  ax, [cs:thresh_lo]
    jb   .done

.slow:
    add  word [cs:slow_lo], 1
    adc  word [cs:slow_hi], 0
    mov  bx, [cs:ring_head]
    cmp  bx, [cs:ring_max]
    jae  .done              ; ring full -- keep counting, stop recording
    push ax
    push dx
    mov  ax, bx
    mov  cx, [cs:rec_size]
    mul  cx
    add  ax, [cs:ring_off]
    mov  bx, ax             ; BX = record offset
    pop  dx
    pop  ax
    mov  cx, [cs:t0_lo]
    mov  [cs:bx],   cx
    mov  cx, [cs:t0_hi]
    mov  [cs:bx+2], cx
    mov  [cs:bx+4], ax
    mov  [cs:bx+6], dx
    mov  cx, [cs:in_ax]
    mov  [cs:bx+8], cx
    mov  cx, [cs:in_cx]
    mov  [cs:bx+10], cx
    mov  cx, [cs:in_dx]
    mov  [cs:bx+12], cx
    inc  word [cs:ring_head]

.done:
    dec  word [cs:busy]
    pop  bx
    pop  dx
    pop  cx
    pop  ax
    push word [cs:ret_fl]
    popf
    retf 2                  ; discard the INT-pushed flags; ours carry the
                            ; original call's CF/AH status to the caller

; ---------------------------------------------------------------------------
; The ring. ring_max is set by the installer to whatever fits the block it
; allocated; the handler stops recording (but keeps counting) when it is full.
; ---------------------------------------------------------------------------
align 16
ring_start:
