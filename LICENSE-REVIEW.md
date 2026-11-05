<!--
Template: ports/adventure-game-studio/LICENSE-REVIEW.md (or the port repo's own root).
Required before building any release-packaging automation for a port.
See sdl-dos-ports' docs/licensing.md for the policy this implements.
-->

# License review: dosags (Adventure Game Studio)

## Engine source

License: **Artistic License 2.0**, verified 2026-09-10 by reading
`License.txt` and `Copyright.txt` directly at the pinned revision
(`v3.6.3.13`, `94e271df9c14484d89f4861100f643d39555dae7`) -- not a
remembered/assumed license. Original author Chris Jones (1999-2011),
various contributors 2011-2026.

Redistribution terms (source): Section 2 permits distributing verbatim
copies of the Standard Version's source freely (gratis or for a
distributor fee), provided original copyright notices/disclaimers are
kept. Section 4 covers a Modified Version (which this port's own
`patches/ags/` makes it): must clearly document how it differs from the
Standard Version, and must satisfy at least one of (a) offer the changes
back to the Copyright Holder [we deliberately do not do this -- see the
hub's "Never contribute upstream" policy], (b) not prevent installing the
Standard Version, and bear a different name [`dosags` satisfies this], or
(c) allow recipients to get the Modified Version's source under the
Original License or an equivalent copyleft-ish license. (b) is the path
this port takes: it's named differently, doesn't block installing
upstream AGS, and documents its differences here and in `PLAN.md`.

Redistribution terms (compiled binary): Section 5 permits distributing
Compiled forms of the Standard Version without source, given valid
instructions for obtaining the source. Section 6 covers distributing a
Modified Version in Compiled form without its own source, which requires
satisfying Section 4 (above) for the Modified Version's source -- i.e. if
dosags ever ships compiled binaries, its own modified source needs to
stay available the way (b) above already sets up (a public repo, source
included). Section 8 permits linking/embedding the Package in a larger
work and distributing the result without restriction, provided the result
doesn't expose a direct interface to the Package -- read this before
deciding how any bundled/statically-linked release binary is packaged.

Notes: this is a plain read of the license text, not a legal opinion --
re-verify before an actual public release, and re-read this section if
`vendor/sources.manifest`'s `ags` pin ever moves (AGS's licensing terms
are not guaranteed identical across all of its own history; this review
applies to the pinned revision only). The AGSBlend plugin
(`Plugins/agsblend/`) carries its own separate license file.
**Correction (2026-09-10, found during `DEPENDENCIES.md` research):**
this is not "irrelevant unless whitelisted" as previously phrased here --
`AGS_BUILTIN_PLUGINS` defaults **ON** (`CMakeLists.txt:35`), and AGSBlend
is one of six plugins (`Plugins/agsblend/`, `agsflashlight/`,
`ags_snowrain/`, `ags_parallax/`, `agspalrender/`, `agsspritefont/`)
statically linked into the Engine binary by default, not gated behind an
opt-in whitelist. Its own license needs the same read-the-actual-file
treatment as Allegro's below before `RELEASE_READY`, not deferred as
"currently irrelevant."
**Resolved for this port (2026-09-16):** the DOS build passes
`-DAGS_BUILTIN_PLUGINS=OFF` (this repo's `Makefile`, `AGS_CMAKE_FLAGS`),
and dynamic plugin loading resolves to `Engine/util/library_dummy.h`
because `library.h` lists no DOS platform -- so none of the six
built-in plugins, and no plugin loader, is linked into `ags.exe`.
AGSBlend's separate license is therefore not a release question for
this port unless a future session turns built-in plugins back on (a
compatibility-sweep finding could motivate that; re-open this entry if
so).

## DOS-specific patches (this port's own `patches/ags/`)

License: inherits Artistic License 2.0 (a Modified Version under the
engine's own terms, per above -- not a separate license).
Notes: 76 patches landed as of 2026-09-16 (`patches/ags/0001-0076`,
with five spent S7 diagnostics reverted); `PATCH-SEQUENCE.md` and
`PLAN.md` document how the Modified Version differs from upstream,
which is Section 4's documentation requirement. This port's own C/C++
additions that are not patches to upstream files (the shared/audio
modules pulled in from the hub subtree) are MIT per the hub's
`THIRD-PARTY.md`; both licenses permit the combination.

## Allegro 4.4.3 (vendored inside AGS's own tree, `vendor/ags/libsrc/allegro/`)

License: **the Allegro "giftware" license**, verified 2026-09-16 by
reading upstream Allegro's own license text at the exact version the
vendored copy identifies itself as -- not from memory.

What was actually read, and why this counts as verification under the
hub's rule (`.sdl-dos-ports/docs/licensing.md`: read the project's own
license file at the pinned revision):

- The vendored subset carries no license file of its own, but every
  vendored source and header ends its banner with `See readme.txt for
  copyright information.` (e.g. `include/allegro.h`,
  `include/allegro/base.h`, `src/allegro.c`), i.e. it points at
  upstream Allegro's `readme.txt`, which AGS's trimmed copy simply did
  not carry over. Its version macros are `ALLEGRO_VERSION 4`,
  `ALLEGRO_SUB_VERSION 4`, `ALLEGRO_WIP_VERSION 3`,
  `ALLEGRO_VERSION_STR "4.4.3"` (`include/allegro/base.h:47-50`), and
  its `CMakeLists.txt` sets `ALLEGRO_VERSION 4.4.3`.
- Upstream Allegro 4.4.3 is git tag `4.4.3` in `liballeg/allegro5`
  (commit `f2224395518ffa3fbdbc94cb107c5045e3a97864`, looked up via the
  GitHub API, not guessed). That tree has no `readme.txt` at its root
  either -- the 4.x line generates it from `docs/src/readme._tx`, and
  keeps the license as its own document `docs/src/license._tx`
  ("The giftware license"). Both were fetched from that tag and read.
  `readme._tx`'s "Copyright" section (lines 196-220) and `license._tx`
  carry the same text:

  > Allegro is gift-ware. It was created by a number of people working
  > in cooperation, and is given to you freely as a gift. You may use,
  > modify, redistribute, and generally hack it about in any way you
  > like, and you do not have to give us anything in return. However,
  > if you like this product you are encouraged to thank us by making a
  > return gift to the Allegro community. [...] If you redistribute
  > parts of this code or make a game using it, it would be nice if you
  > mentioned Allegro somewhere in the credits, but you are not required
  > to do this. [...] THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY
  > OF ANY KIND [...]

Redistribution terms: use, modify, and redistribute freely, source or
binary, with no attribution requirement (a credit is requested, not
required). This port's own `patches/ags/0002` (DJGPP buildability) and
`0037` (the `canonicalize_filename()` DOS drive-prefix fix) are
modifications the license explicitly permits. Nothing in the giftware
text conflicts with distributing `ags.exe` under the engine's Artistic
License 2.0 terms above.

Caveats, stated rather than hidden: (1) AGS's copy is a trimmed and
locally modified subset (AGS's own history, plus this port's two
patches) -- a modification does not change the license it was received
under, but this is a read of upstream's text for the matching version,
not of a file inside the vendored copy, because no such file exists;
(2) the version match rests on the vendored copy's own version macros
and every file's pointer to `readme.txt`, which is the strongest
evidence the tree offers. **Action for `RELEASE_READY`**: add a
`THIRD-PARTY.md` entry with the giftware text quoted above, and mention
Allegro in the release credits (requested by the license, not
required). This section previously read "Open, unverified" (2026-09-10)
-- that blocker is closed.

## SDL3 + this port's own vendored `patches/SDL/`

License: zlib (see this repo's own `THIRD-PARTY.md`).
Notes: `patches/SDL_mixer/` was vendored by the scaffold script but is
**not currently pinned** in `vendor/sources.manifest`. **Resolved
2026-09-11 (Sound milestone plan, "replace, don't port")**: this port
needs neither SDL3_mixer nor SDL2_sound -- PCM goes through its own
fixed-voice mixer on an SDL3 audio stream and MIDI through the hub's
`midi_sched` sinks, so no SDL_mixer entry is needed here. The one
audio dependency still pending is libxmp-lite for tracker decode
(decision 5 / S6: "native decode", not yet vendored) -- its license
gets its own entry here when it is vendored, read from its own
LICENSE file at the pin, before any type-6 clip is wired.

## Linked libraries (in AGS.EXE besides AGS, Allegro and SDL)

Read 2026-11-04 from the vendored files at the AGS pin, for `make dist`.
The list is the link line of `ags.exe`
(`build/ags-release/Engine/CMakeFiles/ags.dir/link.txt`): libSDL3,
libcommon, libaastr, libalfont, libfreetype, libengine, liballeg,
libglm, libminiz, libstb, -lm.

- **FreeType 2.1.3** (`Common/libsrc/freetype-2.1.3`). `docs/license.txt`
  offers the FreeType License (`docs/FTL.txt`) or the GPL; this port takes
  the FTL, as AllegroFont's README says it does. FTL section 2:
  "Redistribution in binary form must provide a disclaimer that states
  that the software is based in part of the work of the FreeType Team, in
  the distribution documentation." The player README.TXT carries that
  credit, and the zip ships `FTL.TXT`. Section 3 bars using the FreeType
  name to promote the product.
- **AllegroFont 2.0.9** (`Common/libsrc/alfont-2.0.9`). README.txt:
  "AllegroFont is distributed under the FreeType Project License (see
  file FTL.txt)". Its FTL.txt differs from FreeType's only in the
  end-of-file label.
- **aastr 0.1.1** (`Common/libsrc/aastr-0.1.1`). Gift-ware, per the
  `aastr.c` header: "You may use, modify, redistribute, and generally
  hack it about in any way you like". It has no conditions.
- **miniz 3.0.2** (`libsrc/miniz`). `miniz.c` carries the MIT licence
  (copyright RAD Game Tools and Valve Software, Rich Geldreich and
  Tenacious Software). `miniz.h` points to an Unlicense statement. The
  MIT notice ships in NOTICES.TXT.
- **stb_image** (`libsrc/stb`, stripped, commit 31c1ad37). `LICENSE`
  offers MIT or public domain. The MIT notice ships in NOTICES.TXT.
- **GLM 1.0.1** (`libsrc/glm`). `copying.txt` offers the Happy Bunny
  licence or MIT. The text ships in NOTICES.TXT.
- **sdl-dos-ports `shared/`** (the hub subtree): MIT
  (`.sdl-dos-ports/LICENSE`). The text ships in NOTICES.TXT.
- **DJGPP C library.** The toolchain has no copy of its licence. We read
  `copying.dj` from delorie.com (`djgpp/dl/ofc/current/v2/copying.dj`,
  identical to the djgpp-cvs mirror) and DJGPP FAQ 19.1, 2026-11-04.
  copying.dj says: "Runtime objects and libraries, as provided by DJ in
  DJGPP, when linked into an application, may be distributed without
  sources ONLY if the recipient is given sufficient information to
  obtain a copy of djgpp themselves. This primarily applies to crt0.o
  and libc.a." The FAQ adds that the BSD acknowledgement was withdrawn
  in 1999, and that a modified libc puts the binary under the LGPL and
  GPL. This port's libc is stock. The toolchain is GCC 12.2.0 built with
  andrewwutw/build-djgpp, which installs DJ's prebuilt libc. No patch here
  touches libc: ags 0082 and 0092 only read libc.a. README.TXT points
  to https://www.delorie.com/djgpp/.
- **GCC runtime** (libgcc, libstdc++, GCC 12.2.0): GPLv3 with the GCC
  Runtime Library Exception 3.1. It permits shipping the compiled
  program under its own terms, with no notice requirement. NOTICES.TXT
  names it anyway.

## CWSDPMI

Release 7 (`csdpmi7b.zip`). The bytes are pinned in
`vendor/binaries.manifest` and are the same as doskutsu's. Its terms, from
the top of `CWSDPMI.DOC`: the files "may be redistributed under the GPL
(with source) or without the source code provided" that CWSDPMI.EXE is
not modified except via CWSPARAM, and with a "Notice to users that they
have the right to receive the source code and/or binary updates for
CWSDPMI. Distributors should indicate a site for the source in their
documentation." The zip ships CWSDPMI.EXE unmodified with CWSDPMI.DOC.
README.TXT gives the notice and https://sandmann.dotster.com/cwsdpmi/.
It is a separate program, not linked into AGS.EXE.

## This port's own code

MIT (`LICENSE`): the build system, scripts, harness, docs, the player
README and the generated MANIFEST.TXT. The DOS patches to AGS and SDL
take their upstream licences (above).

## Game assets

Graphics license: N/A -- no game data ships with this repo.
Music license: N/A -- no game data ships with this repo.
Font license: N/A -- no game data ships with this repo.
Redistribution rights: N/A -- no game data ships with this repo.
Can this port ship any game data at all? **No.** Open-engine +
user-supplied-data model, same as doskutsu. This applies to the first
test game chosen for bring-up (see `PLAN.md`) as much as to any other AGS
game -- its own license is a separate question to record here once it's
actually chosen, not assumed from AGS's own license.

Golden-reference and harness games used for local testing (AGS Quest,
Trilby's Notes, Shards of God, IOAWN4T, and the two still to be
sourced) are never committed; each has a `PIN` file recording what was
downloaded, its hash, and the license/freeware terms as actually read.
Only manifests, hashes, logs, and screenshot **hashes** enter git.

**The self-authored first test game (decided 2026-09-16, operator):**
its art, backgrounds, WAV, and MIDI ship under **CC0 1.0**; its scripts,
`Game.agf`, and build tooling under this repo's **MIT**; its font stays
a verified OFL font (Press Start 2P, whose OFL text is already committed
at `tests/harness/packages/agsquest/overlay/assets/PressStart2P-OFL.txt`).
It will be the ONE game package this repo does commit (under
`tests/fixtures/`), and the `README` next to it must record those terms
and confirm no template-derived Editor content (default GUI sprites,
cursors, boilerplate scripts from `ags-template-source`, which has no
license file) survived into the package -- see `PLAN.md` "First test
game -- authoring plan".

## Conclusion

The AGS engine itself (Artistic License 2.0) can be distributed as source
and, with care (Sections 5/6/8 above), as compiled binaries, provided this
port's modifications stay documented, differently named, and don't block
installing standard upstream AGS -- all already true by construction
(`dosags`, its own public repo, `PLAN.md` tracking the diff). No game data
of any kind is or will be shipped by this repo; users supply their own
legally obtained AGS game files, including for the first test game once
one is chosen. This conclusion covers the pinned revision only and should
be re-checked before any real release, not treated as a one-time legal
sign-off. The Allegro 4.4.3 blocker recorded here on 2026-09-10 is
**closed (2026-09-16)**: giftware, verified against upstream's own
license text for the matching version (see that section for exactly
what was read and the one caveat). Built-in plugins are compiled out,
so no plugin license applies. Remaining before `RELEASE_READY`: a libxmp-lite entry
if/when it is vendored; the self-authored test game's own `README`
license record once it exists. The `THIRD-PARTY.md` Allegro entry is
done (2026-11-04, with the `make dist` work). Before a public zip, the
source must be published and its URL passed to `make dist`
(`DIST_REPO_URL`); see "Linked libraries" and "CWSDPMI" above for the
notices the zip carries.
