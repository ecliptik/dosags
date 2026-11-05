DOSAGS @VERSION@ -- Adventure Game Studio engine for MS-DOS
==========================================================

Build @SHA12@ (release flavour). Source: @REPO_URL@

DOSAGS is the Adventure Game Studio (AGS) 3.6.3 engine ported to MS-DOS.
It plays AGS games; it is not a game itself. NO GAME DATA IS INCLUDED.
Use your own, legally obtained copy of an AGS game.

DOSAGS is a Modified Version of AGS, not the Standard Version. It is
named differently and does not stop you installing standard AGS. The
changes are documented in the source repository (patches/ags/).


WHAT YOU NEED
-------------

- A 486DX2-66 or faster. 16 MB RAM is the target minimum (the
  reference machine has 48 MB; less has not been measured).
- MS-DOS (tested on MS-DOS 6.22).
- A VESA 1.2+ video BIOS for 512x384 and 640x480 (on cards without one,
  load a VESA driver such as UniVBE first).
- A DOS mouse driver (MOUSE.COM, CTMOUSE or similar), loaded before
  AGS.EXE.
- For sound: a Sound Blaster compatible card, a Gravis UltraSound, and/or
  an MPU-401 with a General MIDI daughterboard (e.g. a WaveBlaster).


FILES
-----

  AGS.EXE       the engine
  CWSDPMI.EXE   DPMI host (DJGPP programs need one; keep it next to
                AGS.EXE or on the PATH)
  CWSDPMI.DOC   CWSDPMI's licence and documentation
  README.TXT    this file
  LICENSE.TXT   licence for this port's own code (MIT)
  ARTISTIC.TXT  Artistic License 2.0, the AGS engine's licence
  AGSCOPY.TXT   AGS copyright notice
  NOTICES.TXT   licence notices of the libraries linked into AGS.EXE
  FTL.TXT       the FreeType Project License
  3RDPARTY.TXT  the full third-party component list
  MANIFEST.TXT  sha256 of every file in this package, and the build stamp


SETTING UP A GAME
-----------------

1. Copy AGS.EXE and CWSDPMI.EXE into the game's directory.
2. The game's data file must have a DOS 8.3 name (e.g. GAME.AGS). Games
   shipped as a Windows .EXE with the data appended work too, renamed to
   an 8.3 name. Keep any AUDIO.VOX / SPEECH.VOX next to it.
3. Run AGS.EXE from that directory. It finds the game file there.

An ACSETUP.CFG in the game directory sets the screen mode and sound.
For example, to show a 320x200 game 1:1 at 512x384, centred:

  [graphics]
  fullscreen = 512x384
  game_scale_fs = round
  windowed = 0

Saves go in the current directory (the game directory). Use
--user-data-dir to put them elsewhere.


SOUND
-----

Sound effects and speech (PCM) go to the Sound Blaster, or to the GUS
with the GUS backend. MIDI music goes to the backend named by the
SDL_HINT_DOS_AUDIO_BACKEND environment variable:

  SET SDL_HINT_DOS_AUDIO_BACKEND=auto   OPL3/OPL2 FM synth (the default)
  SET SDL_HINT_DOS_AUDIO_BACKEND=opl3   the same, by name
  SET SDL_HINT_DOS_AUDIO_BACKEND=wb     MPU-401 / WaveBlaster General MIDI
  SET SDL_HINT_DOS_AUDIO_BACKEND=gus    Gravis UltraSound for both PCM and
                                        MIDI (GF1)
  SET SDL_HINT_DOS_AUDIO_BACKEND=none   no MIDI

The Sound Blaster is found from the BLASTER variable, e.g.

  SET BLASTER=A220 I7 D3 P330 T3

(port A, IRQ I, 8-bit DMA D, MPU port P, card type T). The GUS is found
from ULTRASND, e.g. SET ULTRASND=240,1,1,11,7 (port, DMA, DMA, IRQ, IRQ).
Use the values your card's own setup program gives you.

If a backend's hardware is not found, that part of the sound is off for
the session and the game still runs.


KNOWN LIMITS
------------

- Speed. On the reference machine (486DX2-66, ATI Mach64, sound on) the
  project's three test scenes ran at full speed (40 game ticks per
  second) at 8-, 16- and 32-bit colour. Other games and heavier rooms
  can be slower; game logic stays correct, the frame rate drops.
- OGG and MP3 audio are NOT decoded on DOS. Games whose music or speech
  is OGG/MP3 (most games made with AGS 3.x) play those clips silently
  unless the clips are first converted to WAV on a modern PC with the
  port-game tool in the source repository (tools/port-game).
- Tracker music (MOD/XM/S3M/IT) is not played.
- No Theora video playback.
- No engine plugins are built in or loadable. A game that needs one may
  refuse to start, or run without that plugin's features.
- No networking.
- Sound start latency: a sound started from silence reaches the card
  4.3 ms (median) after the game asks for it on the reference machine.
  The project's target was 1.0 ms; this is recorded as a failed target
  (test D2), not a playback fault.
- A mouse click shorter than one game frame can be missed on a slow
  machine when a game runs below 1 frame per second: hold the button a
  moment.


CREDITS AND LICENCES
--------------------

AGS (Adventure Game Studio) by Chris Jones and contributors, Artistic
License 2.0 (ARTISTIC.TXT, AGSCOPY.TXT).

This software is based in part on the work of the FreeType Team
(https://www.freetype.org) -- FreeType 2.1.3, used under the FreeType
Project License (FTL.TXT). AllegroFont 2.0.9 is also under that licence.

Uses SDL 3 (zlib licence), Allegro 4.4.3 (giftware), aastr (giftware),
miniz (MIT), stb_image (MIT) and GLM (MIT); see NOTICES.TXT.

Built with DJGPP (stock libc). DJGPP is free and can be obtained from
https://www.delorie.com/djgpp/

CWSDPMI is Copyright (C) 1995-2010 Charles W Sandmann. You have the
right to receive the source code and binary updates for CWSDPMI; they
are available from https://sandmann.dotster.com/cwsdpmi/

Source for this port, including every change made to AGS and SDL:
@REPO_URL@
