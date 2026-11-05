@ECHO OFF
REM =====================================================================
REM  DOSKUTSU sound-card boot menu.  Video = UniVBE for every profile.
REM  Global defaults (all profiles): official wiimidi MIDI set + joystick OFF.
REM  To opt into WaveBlaster wavetable / OrgMIDI, set these at the prompt
REM  before launching the game:
REM     SET SDL_HINT_DOS_AUDIO_BACKEND=wb
REM     SET SDL_HINT_DOS_AUDIO_MIDI_SOURCE=orgmid
REM     SET SDL_HINT_DOS_AUDIO_MIDI_GM_VARIANT=v1
REM =====================================================================

SET TEMP=C:\TEMP
SET TMP=C:\TEMP
SET ULTRADIR=C:\ULTRASND
PROMPT $p$g
PATH C:\DOS;C:\WINDOWS;C:\PICOGUS;C:\UNISOUND;C:\UNIVBE;C:\DRIVERS

REM --- CLEAN branches out BEFORE any TSR loads; see the :CLEAN block ---
IF "%config%"=="CLEAN" GOTO CLEAN

REM --- capture mode: make the console visible to the VGA capture stick ---
REM DOS text mode 03h is 720x400 @70Hz and the capture hardware cannot lock
REM onto it -- it returns flat black. BIOS mode 12h is 640x480 @60Hz, which
REM it locks onto reliably, and the console stays usable at 80x30 because
REM text still renders through the BIOS TTY into the graphics framebuffer.
REM Placed here, before the TSR loads, so ALL of AUTOEXEC is capturable.
REM
REM COST: mode 12h console text is SLOW (planar, read-modify-write per
REM glyph), so CLS and heavy ECHO visibly crawl. If you are sitting at the
REM machine rather than driving it remotely, REM out the next line, or run
REM VGACAP\MODE03 at the prompt to go back to normal text mode.
REM A copy of this file from before this change is kept as C:\AUTOEXEC.NOM
IF EXIST C:\VGACAP\MODE12.COM C:\VGACAP\MODE12.COM

REM --- video + shared TSRs (all profiles) ---
LH C:\UNIVBE\UNIVBE.EXE
LH C:\WINDOWS\SMARTDRV.EXE 4096 1024 C A-
LH C:\DRIVERS\CTMOUSE.EXE
LH DOSKEY

REM --- clean DOSKUTSU defaults for every profile ---
SET SDL_HINT_DOS_AUDIO_MIDI_SOURCE=wiimidi
SET DOSKUTSU_USE_JOYSTICK=0

GOTO %config%

REM === Vibra16 (SB16/OPL3) + PicoGUS USB (CD on D: + MPU-401 MIDI) ======
REM The single Vibra16 lane. PGUSINIT /mode usb is deliberate beyond the
REM CD-ROM: it leaves the PicoGUS in a known NON-sound state, so a Vibra
REM run cannot inherit whatever sound mode a previous boot left the card
REM in. That inheritance has already broken a sweep at sdl_init once.
:VIBRA
SET BLASTER=A220 I5 D1 H5 T6 P330
SET MIDI=SYNTH:1 MAP:E MODE:0
C:\PICOGUS\PGUSINIT.EXE /mode usb
C:\UNISOUND\UNISOUND.COM /V80
LH C:\DOS\MSCDEX.EXE /D:MSCD000 /D:OPTICAL /M:5
GOTO READY

REM === PicoGUS Sound Blaster (8-bit DMA; SB 2.0-class emulation) ========
REM PHYSICAL JUMPERS RULE EVERYTHING: this PicoGUS is jumpered IRQ7 + DMA3
REM (set during the GUS campaign for Vibra16 coexistence), and the SB-mode
REM IRQ/DMA MUST match the jumpers -- pgusinit /sbirq /sbdma help says
REM '(must match jumper settings!)' and it is literal. BLASTER therefore
REM says I7 D3. Confirmed working 2026-07-06 (music + SFX audible).
REM T3 = SB 2.0 class: matches the card's 8-bit-DMA reality, makes the
REM legacy autoinit path native, and sidesteps firmware v4.x's SB16-mode
REM 'D and H must match' rule. /sbenv PROGRAMS the card's SB registers
REM from BLASTER (/mode sb alone does NOT; plain pgusinit only validates).
REM FORCE_8BIT pins DOSKUTSU to the 8-bit path regardless of DSP version.
REM Gives OPL3 (picogus-sb-dbopl3) + the WaveBlaster header (MPU-401 0x330).
:PGSB
SET BLASTER=A220 I7 D3 P330 T3
SET SDL_HINT_DOS_AUDIO_SB_FORCE_8BIT=1
C:\PICOGUS\PGUSINIT.EXE /mode sb
C:\PICOGUS\PGUSINIT.EXE /sbenv
LH C:\DOS\MSCDEX.EXE /D:OPTICAL /M:5
GOTO READY

REM === PicoGUS AdLib (OPL2 FM at 0x388) =================================
REM DOSKUTSU AdLib backend (Campaign 2): OPL2 FM music via the PIT timer
REM pump, MUSIC ONLY (a pure AdLib card has no DAC, so no Pixtone SFX).
REM Requires the Campaign-2 AdLib binary. Do NOT run a Sound Blaster in the
REM same machine -- two OPL chips at 0x388 conflict.
:PGADLIB
SET SDL_HINT_DOS_AUDIO_BACKEND=adlib
C:\PICOGUS\PGUSINIT.EXE /mode adlib
LH C:\DOS\MSCDEX.EXE /D:OPTICAL /M:5
GOTO READY

REM === PicoGUS Ultrasound (GF1) =========================================
REM PicoGUS jumpered IRQ7 + DMA3 (leaves IRQ5/DMA1 free for the Vibra16 when it
REM is installed -- coexistence). ULTRASND = port,playDMA,recDMA,GF1-IRQ,MIDI-IRQ
REM and MUST match the jumpers.
REM CARD CONFIRMED WORKING: Gravis MIDIDEMO.BAT (C:\ULTRASND) plays GUS music on
REM every jumper config tried. Doom GUS is silent regardless (a Doom/DMX
REM IRQ-driven quirk, NOT a card fault -- MIDIDEMO is poll-based + works). So the
REM GUS audio path is proven; Doom is not our gate.
REM pgusinit /mode gus swaps to GUS firmware; the SECOND pgusinit run applies the
REM settings + the DMA interval (/gusdma 12). ULTRADIR (global, C:\ULTRASND)
REM the GUS .pat patch set. doskutsu GUS backend (Campaign 3) ships next; its GF1
REM driver is being hardened to be IRQ-INDEPENDENT (poll DMA-terminal, not the GF1
REM IRQ) so it sounds where Doom's IRQ-driven path does not.
:PGGUS
SET SDL_HINT_DOS_AUDIO_BACKEND=gus
SET ULTRASND=240,3,3,7,7
C:\PICOGUS\PGUSINIT.EXE /mode gus
C:\PICOGUS\PGUSINIT.EXE /gusdma 12
LH C:\DOS\MSCDEX.EXE /D:OPTICAL /M:5
GOTO READY

REM === Networking: ODI stack + mTCP, for file transfer ==================
REM Gated behind its own profile DELIBERATELY. The packet driver hooks a
REM software interrupt AND the NIC hardware IRQ 10, and measured cells run
REM audio on IRQ 7 under a cooperative scheduler where starving the audio
REM thread degrades music. Against a 0.2 fps noise floor a contaminating
REM change need not look broken to invalidate a comparison.
REM ***** NEVER BOOT THIS PROFILE FOR A MEASURED RUN. *****
REM Load here, transfer, then REBOOT into a normal profile before measuring.
REM
REM Two gotchas that cost real time during bring-up, do not "fix" them:
REM   - ODIPKT takes logical board 0, NOT 1, even though E100BODI prints
REM     "Board 1". Board 1 fails with "Cannot get MLID control entry".
REM   - Packet vector is 0x7E, not the usual 0x60 -- 0x60 is contended by
REM     sound TSRs on this machine. TCP.CFG must agree (packetint 0x7E).
REM Verify with:  PKTTOOL scan   then   PING 192.168.7.1
:NET
CD \NET
C:\NET\LSL.COM
C:\NET\E100BODI.COM
C:\NET\ODIPKT.COM 0 0x7E
SET MTCPCFG=C:\MTCP\TCP.CFG
CD \
GOTO READY

REM === CLEAN: bare recovery boot ========================================
REM Reached by the branch at the top, before any TSR is loaded: no UniVBE,
REM no SMARTDRV, no mouse, no DOSKEY, no sound init, no MSCDEX.
REM NOT a driverless boot -- CONFIG.SYS [COMMON] still loads HIMEM, EMM386
REM and the optical driver. It is a boot where nothing in AUTOEXEC can hang.
REM Use it when a normal profile fails to reach the prompt.
:CLEAN
REM CLEAN branched out before the shared mode-12h line above, so set it
REM here too -- the recovery profile is exactly when remote visibility
REM matters most.
IF EXIST C:\VGACAP\MODE12.COM C:\VGACAP\MODE12.COM
ECHO.
ECHO [CLEAN] recovery boot -- no sound, no video init, no TSRs.
IF EXIST C:\DRIVERS\RDYPULSE.COM C:\DRIVERS\RDYPULSE.COM
GOTO END

:READY
ECHO.
ECHO [%config%] ready.
REM Harness readiness signal -- MUST stay the last line of this path, so
REM that seeing it means every TSR is up and the prompt is live. Guarded,
REM so it is a no-op until the COM exists and has been tested by hand.
IF EXIST C:\DRIVERS\RDYPULSE.COM C:\DRIVERS\RDYPULSE.COM

:END
