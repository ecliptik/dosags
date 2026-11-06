# Third-Party Components

Attribution and licence matrix for everything DOSAGS links, ships, or
uses to build and test. Kept in sync with `vendor/sources.manifest` and
`vendor/binaries.manifest`. The licence texts were read at the pinned
revisions; `LICENSE-REVIEW.md` records each reading. This file ships in
the player zip as `3RDPARTY.TXT`. Rewritten 2026-11-04 for `make dist`;
the earlier text dated from before the first build.

---

## In AGS.EXE (statically linked)

The link line is `build/ags-release/Engine/CMakeFiles/ags.dir/link.txt`.

| Component | Version / ref | Licence | Notes |
|---|---|---|---|
| [Adventure Game Studio](https://github.com/adventuregamestudio/ags) | `v3.6.3.13` @ `94e271df9c14` | Artistic License 2.0 | Engine. A Modified Version: this repo's `patches/ags/` |
| [SDL 3](https://github.com/libsdl-org/SDL) | `main` @ `74a746281f22` | zlib | Platform layer and DOS backend, with this repo's `patches/SDL/` |
| Allegro (subset inside AGS, `libsrc/allegro`) | 4.4.3 | giftware | Blit, palette, math, packfile only |
| FreeType (inside AGS, `Common/libsrc/freetype-2.1.3`) | 2.1.3 | FreeType Project License (chosen over GPL) | TTF fonts. Binary redistribution needs the FreeType credit in the docs (README.TXT carries it) |
| AllegroFont (inside AGS, `Common/libsrc/alfont-2.0.9`) | 2.0.9 | FreeType Project License | Allegro wrapper for FreeType |
| aastr (inside AGS, `Common/libsrc/aastr-0.1.1`) | 0.1.1 | giftware | Anti-aliased stretch |
| miniz (inside AGS, `libsrc/miniz`) | 3.0.2 | MIT | Deflate |
| stb_image (inside AGS, `libsrc/stb`) | stripped, commit `31c1ad37` | MIT (or public domain) | PNG loading |
| GLM (inside AGS, `libsrc/glm`) | 1.0.1 | MIT (or Happy Bunny) | Maths headers |
| sdl-dos-ports `shared/` (subtree `.sdl-dos-ports/`) | subtree pin | MIT | runmanifest, MIDI scheduler, OPL3 / WaveBlaster / GUS sinks |
| DJGPP C library | stock libc, `go32stub v2.05` | DJGPP `copying.dj` (LGPL sources; stock binaries free to ship with a pointer to DJGPP) | C runtime |
| GCC runtime (libgcc, libstdc++) | GCC 12.2.0 | GPLv3 + GCC Runtime Library Exception 3.1 | C++ runtime |

Not linked: SDL2_sound, mojoAL, Ogg / Vorbis / Theora (gated out at
configure time, `AGS_NO_VIDEO_PLAYER`), tinyxml2, Glad, and all AGS
built-in plugins (`-DAGS_BUILTIN_PLUGINS=OFF`). libxmp-lite (tracker
music) is planned but not vendored.

## Shipped beside AGS.EXE

| Component | Version / ref | Licence | Notes |
|---|---|---|---|
| [CWSDPMI](https://sandmann.dotster.com/cwsdpmi/) | r7 (`csdpmi7b.zip`), sha256 pinned in `vendor/binaries.manifest` | freeware: may be redistributed unmodified with `CWSDPMI.DOC` and a notice of where its source is | DPMI host. Not linked; a separate program |
| OPL3 GM FM bank (`OPL3BANK.DAT`) | hub `shared/audio/opl3bank.dat`, from [DMXOPL](https://github.com/sneakernets/DMXOPL) `e83c144a2e6d` | MIT | Data read by `opl3_sink`; without it OPL3 music uses 8 built-in patches |

## Build and test only (not shipped)

| Component | Licence | Role |
|---|---|---|
| DJGPP cross toolchain (GCC 12.2.0, binutils) | GPL | Compiler |
| [DOSBox-X](https://dosbox-x.com/) | GPLv2 | Emulator for the ratchet and harness |
| ffmpeg (host) | LGPL / GPL | `tools/port-game` transcodes OGG / MP3 to WAV |
| FluidSynth + FluidR3_GM (host) | LGPL / MIT | Reference renders for the capture scorers |

No game data is shipped or tracked. Test games are pinned by hash in
`tests/games/*/PIN` and `tests/harness/packages/*/PIN`.

## Sibling and hub projects

- **sdl-dos-ports** (hub, consumed as the `.sdl-dos-ports/` subtree):
  `https://forgejo.example.ts.net/ecliptik/sdl-dos-ports`, MIT.
- **doskutsu** and **dossage** (sibling ports): structural references
  only, no code linked. doskutsu: https://github.com/ecliptik/doskutsu,
  MIT.

---

## Player zip contents (`make dist`)

`scripts/check-dist.sh` checks every zip against this table. It fails
when a file is in the zip but not listed here, or listed here but not in
the zip, or when a row names a `LICENSE-REVIEW.md` section that does not
exist. Text files are ASCII with CRLF line ends. The exceptions are
CWSDPMI.DOC and FTL.TXT, which ship upstream's text unaltered; FTL.txt
has one Latin-1 copyright sign.

<!-- dist-files:begin -->
| File | From | Why it ships | LICENSE-REVIEW.md section |
|---|---|---|---|
| `AGS.EXE` | `build/ags-release/ags.exe` (`DOSAGS_RELEASE=1`), byte for byte | the engine | `Engine source` |
| `CWSDPMI.EXE` | `vendor/cwsdpmi/cwsdpmi.exe` (pinned) | DPMI host | `CWSDPMI` |
| `CWSDPMI.DOC` | `vendor/cwsdpmi/cwsdpmi.doc` (pinned) | CWSDPMI's terms require it beside the exe | `CWSDPMI` |
| `OPL3BANK.DAT` | `.sdl-dos-ports/shared/audio/opl3bank.dat` (sha256 pinned in make-dist.sh) | the OPL3 music's GM instrument bank | `OPL3 instrument bank` |
| `README.TXT` | `docs/dist/README.TXT` | player guide; carries the FreeType, DJGPP and CWSDPMI notices | `This port's own code` |
| `LICENSE.TXT` | `LICENSE` | MIT, this port's own code | `This port's own code` |
| `ARTISTIC.TXT` | `vendor/ags/License.txt` | Artistic License 2.0 | `Engine source` |
| `AGSCOPY.TXT` | `vendor/ags/Copyright.txt` | AGS copyright notice | `Engine source` |
| `FTL.TXT` | `vendor/ags/Common/libsrc/freetype-2.1.3/docs/FTL.txt` | FreeType Project License | `Linked libraries` |
| `NOTICES.TXT` | generated by `make-dist.sh` from the vendored licence files | notices for SDL, miniz, stb, GLM, aastr, AllegroFont, Allegro, the hub modules, DMXOPL, DJGPP and GCC | `Linked libraries` |
| `3RDPARTY.TXT` | this file | the component list | `This port's own code` |
| `MANIFEST.TXT` | generated | sha256 of every file, build stamp, stub minstack | `This port's own code` |
<!-- dist-files:end -->

The zip carries the source URL given as `make dist DIST_REPO_URL=...`.
The Artistic License (sections 4 and 6), DJGPP and CWSDPMI all need
players to be told where the source is. Without a URL the check prints
NOT RELEASABLE, and with `--release` it fails.
