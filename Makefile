# Makefile -- dosags (Adventure Game Studio DOS port)
#
# Orchestrates: SDL3 cross-build (shared fragment) -> AGS's own CMake engine
# stage, patched to configure and link against that SDL3 instead of AGS's
# stock SDL2 (this repo's own patches/ags/, applied by apply-patches.sh).
# Neither SDL3_mixer nor SDL3_image is vendored or built -- audio is
# stubbed for COMPILES (PATCH-SEQUENCE.md 0005/0006/0012/0016/0018;
# vendor/sources.manifest's SDL_mixer/SDL_image NOTE entries) and nothing
# in AGS's own Engine/Common code calls SDL_image. Do not add either stage
# here without a concrete reason found during porting -- see PLAN.md's
# Open questions.

PORT_NAME := dosags
REPO_ROOT := $(abspath .)
HUB_DIR   := $(REPO_ROOT)/.sdl-dos-ports

include $(HUB_DIR)/shared/build/sdl3-dos.mk

.PHONY: all
all: sdl3 game

# --- AGS engine stage --------------------------------------------------------
#
# First CMake-based upstream engine in this hub (PATCH-SEQUENCE.md tl;dr
# #3) -- there is no sibling port's "game" stage to copy the shape of.
# AGS's own CMakeLists.txt is patched in place (patches/ags/, not rewritten
# here) to configure/link against $(SYSROOT)'s SDL3 instead of its stock
# SDL2 acquisition path; this Makefile only drives that patched CMake
# project, the same way sdl3-dos.mk drives SDL3/SDL3_mixer/SDL3_image's.
#
# Until patches/ags/0001-0009 land (Phase A/B of PATCH-SEQUENCE.md),
# configure-ags fails at AGS's own CMAKE_SYSTEM_NAME gate
# (CMakeLists.txt:76-89) -- expected, not a Makefile bug. That failure,
# read literally, is the whole point of running this target before any
# patch exists: it is BOOTSTRAP's own "first sign of life" check.

AGS_SRC       := $(VENDOR_DIR)/ags
ifeq ($(DOSAGS_RELEASE),1)
AGS_BUILD_DIR := $(BUILD_DIR)/ags-release
else
AGS_BUILD_DIR := $(BUILD_DIR)/ags
endif
AGS_PATCHES   := $(wildcard $(REPO_ROOT)/patches/ags/*.patch)

# Flags matching the COMPILES milestone's own definition (PLAN.md):
# "editor, networking, hardware renderers, Theora (AGS_NO_VIDEO_PLAYER),
# and plugins disabled". Editor/networking/hardware-renderer exclusion
# falls out of Common/platform/platform.h simply not listing DOS among
# AGS_PLATFORM_DESKTOP's platforms (patch 0009) -- no CMake flag exists
# for those three, confirmed by reading CMakeLists.txt's own option()
# list (only AGS_NO_VIDEO_PLAYER and AGS_BUILTIN_PLUGINS are real toggles
# here). AGS_BUILD_ENGINE/AGS_TESTS are already the shown defaults;
# listed explicitly so a future AGS version bump can't silently change
# what this port builds.
#
# Deliberately NOT passed: any AGS_USE_LOCAL_* flag. Those select
# find_package(SDL2)/find_package(SDL2_sound)/find_package(Ogg|Vorbis|
# Theora) as the alternative to AGS's own FetchContent path -- patches
# 0003/0004/0005/0006 replace or gate out those acquisition blocks for
# DOS entirely (pointing at $(SYSROOT)'s SDL3, or dropping the
# dependency), so forcing a *_LOCAL_* toggle ON would just make CMake go
# looking for a package (SDL2, SDL2_sound, Ogg, ...) this sysroot never
# installs, fighting the patch instead of being superseded by it.
# CMAKE_COMMON (sdl3-dos.mk) already sets -DCMAKE_CXX_FLAGS="$(NOSIMD_FLAGS)";
# cmake's -D processing takes the LAST value for a given cache variable, so
# this override must restate NOSIMD_FLAGS itself, not just add the new bit,
# or the hard "no SIMD unless NOSIMD_FLAGS-gated" constraint would silently
# stop applying to this stage. The added -I makes
# .sdl-dos-ports/shared/include/runmanifest.h available to Engine/main/
# quit.cpp and main.cpp (patch 0038, RUNMANIFEST wiring) -- this is the
# first engine-stage consumer of shared/include, so no prior patch added
# this path. Sound milestone S4 adds a second -I for shared/audio
# (midi_sched.h / opl3_sink.h, S3's hub hoist) -- platform/dos/
# dos_midi_backend.cpp and audioplayer.cpp both consume these headers.
AGS_CXX_FLAGS_BASE := $(NOSIMD_FLAGS) -I$(HUB_DIR)/shared/include -I$(HUB_DIR)/shared/audio
# ags patch 0230: AGS_WORK_SCRIPT_INS=1 builds the LAB binary that also counts script VM
# instructions for the work vector (LAB-METRIC.md). Off by default because the
# per-instruction increment costs a script-bound cell measurably (MMD -18% render rate on
# a fixed-cycles DOSBox-X). Added to AGS_CXX_FLAGS_BASE, which AGS_BUILD_SHA12 hashes, so
# a lab binary never shares a binary_sha12 with a timed one.
ifeq ($(AGS_WORK_SCRIPT_INS),1)
AGS_CXX_FLAGS_BASE += -DDOSAGS_WORK_SCRIPT_INS
endif
# ags patch 0351 (PLAN-NEXT step 1, 2026-11-04): DOSAGS_RELEASE=1 builds the RELEASE flavour -- no tick
# timing, no work vector, no stall/skip attribution, no quit-time counter dump, no diagnostic-only env hooks,
# and DOSAGS_FIXED_TIMESTEP defaults on (operator 2026-11-04). It keeps RUNMANIFEST and every line the gate
# scorers and the DOSBox-X ratchet read. Added to AGS_CXX_FLAGS_BASE, which AGS_BUILD_SHA12 hashes, so the
# release exe has its own stamp; built in its own directory (build/ags-release/ags.exe) against the same
# SDL sysroot, so both flavours of one commit can sit side by side for an ABBA.
ifeq ($(DOSAGS_RELEASE),1)
AGS_CXX_FLAGS_BASE += -DDOSAGS_RELEASE
endif

# DOS_PORT_SHARED_AUDIO_DIR (S4): an absolute path CMakeLists.txt (patch
# 0052) uses to add midi_sched.c/opl3_sink.c -- plain C files that live in
# the hub subtree, not under vendor/ags/Engine/ -- as real compiled sources,
# the same way AGS_CXX_FLAGS_BASE's -I above already reaches their headers.
AGS_CMAKE_FLAGS := \
    -DAGS_BUILD_ENGINE=ON \
    -DAGS_BUILD_TOOLS=OFF \
    -DAGS_BUILD_COMPILER=OFF \
    -DAGS_TESTS=OFF \
    -DAGS_NO_VIDEO_PLAYER=ON \
    -DAGS_BUILTIN_PLUGINS=OFF \
    -DDOS_PORT_SHARED_AUDIO_DIR=$(HUB_DIR)/shared/audio

# --- Build fingerprint --------------------------------------------------
#
# A content hash of everything that determines this engine-stage binary, so
# a RUNMANIFEST block can name the build it came from and that name can be
# RECOMPUTED later rather than merely trusted -- same rationale as
# dossage's own BUILD_SHA12 (see that port's Makefile). PATCH-SEQUENCE.md
# Phase F left this deliberately empty at RUNMANIFEST-wiring time (patch
# 0038) because no fingerprint pipeline existed yet for this CMake-driven
# stage; this closes that follow-up.
#
# Hashes the INPUTS, never the output. Covered: both vendor trees post-
# patch (SDL, AGS -- each `rev-parse HEAD^{tree}` folds in that pin AND its
# full applied patch series, since apply-patches.sh commits each patch),
# this stage's own CMake flags (AGS_CMAKE_FLAGS captured HERE, before the
# CMAKE_CXX_FLAGS line below appends the fingerprint itself -- see the
# ordering note on that line), the hub build fragment supplying NOSIMD_FLAGS,
# and the compiler version. NOT covered: anything reached only at runtime
# (game data, CWSDPMI, SDL hints set by the launcher) -- same documented gap
# dossage's own comment carries.
# DOS-PORT: the vendor trees' WORKING-TREE state, folded in below.
#
# Without this, AGS_BUILD_SHA12 came from `rev-parse HEAD^{tree}` alone --
# the COMMITTED tree -- so a binary built from a working tree that differs
# from HEAD was stamped with a tree it was not built from. That happened
# three times in one day: an A/B arm built by reverse-applying a patch, a
# B arm built before its own commit, and a cell stamped with the previous
# patch's identity. It fails silently, and in the direction that PASSES
# the "the two arms must differ" invalidity check, because two
# working-tree builds off one commit get the same stamp.
#
# `git diff HEAD` rather than `git status --porcelain`: porcelain lists
# changed PATHS, so two different edits to the same file collide with each
# other. Diff content does not. `git diff HEAD` cannot see untracked
# files, so their contents are hashed too -- Engine sources are listed
# explicitly rather than globbed (only RESOURCE_FILES uses file(GLOB)), so
# an untracked .cpp would not be compiled, but an untracked .h can be
# included by one that is.
#
# No objects are created (unlike `git stash create`), so this is safe to
# run on every make invocation.
#
# Folded into the hash ONLY WHEN THE TREE IS DIRTY (see the `if` below).
# A clean build must keep reproducing its historical stamp: the collision
# this fixes only ever came from dirty trees, and making every clean build
# restamp would trade a real loss of auditability -- you could no longer
# identify which commit an archived cell was built from -- for nothing.
AGS_VENDOR_DIRT := $(shell {     for d in $(VENDOR_DIR)/SDL $(VENDOR_DIR)/ags; do         git -C $$d diff HEAD;         git -C $$d ls-files --others --exclude-standard -z             | (cd $$d && xargs -0 -r sha256sum) 2>/dev/null;     done;   } 2>/dev/null | sha256sum | cut -c1-12)

# 1 when either vendor tree differs from its commit. Reported in the run
# manifest as its own line, NOT folded into binary_sha12's text: that
# field is fixed-width in the manifest struct, and a reader wants to SEE
# "this cell ran a working-tree build" rather than merely observe that two
# opaque hashes differ.
AGS_BUILD_DIRTY := $(shell {     git -C $(VENDOR_DIR)/SDL status --porcelain;     git -C $(VENDOR_DIR)/ags status --porcelain;   } 2>/dev/null | head -c1 | wc -c | tr -d ' ')

# The stamp's input text (2026-09-24, hub docs/patch-conventions.md 799972d/21453cf): only content and
# RELATIVE paths, so the same series builds the same stamp in any worktree. It used to hash sha256sum's
# OUTPUT (which carries each file's absolute path) and echo flags carrying -I$(HUB_DIR)/... and
# -D...=$(HUB_DIR)/..., so two worktrees stamped identical code differently (dosags round F: my build of
# main 1301a56e stamped 5fa609ba8318, lab-metric's b983bf9d146a, the files differing only in those 13
# stamp bytes). Absolute roots are replaced by @ROOT@; hub files are hashed from inside $(HUB_DIR).
# `make stamp-input` prints the text. A clean build's stamp changed ONCE with this fix, so stamps from
# before it (every archived cell up to 2026-09-24) are not comparable with stamps after it.
AGS_BUILD_STAMP_INPUT = { \
    git -C $(VENDOR_DIR)/SDL rev-parse HEAD^{tree}; \
    git -C $(VENDOR_DIR)/ags rev-parse HEAD^{tree}; \
    if [ "$(AGS_BUILD_DIRTY)" = "1" ]; then echo "AGS_VENDOR_DIRT=$(AGS_VENDOR_DIRT)"; fi; \
    echo "AGS_CMAKE_FLAGS=$(subst $(REPO_ROOT),@ROOT@,$(AGS_CMAKE_FLAGS))"; \
    echo "AGS_CXX_FLAGS_BASE=$(subst $(REPO_ROOT),@ROOT@,$(AGS_CXX_FLAGS_BASE))"; \
    (cd $(HUB_DIR) && sha256sum shared/build/sdl3-dos.mk \
        shared/audio/midi_sched.c shared/audio/midi_sched.h \
        shared/audio/opl3_sink.c shared/audio/opl3_sink.h); \
    $(CXX) -dumpversion; \
  } 2>/dev/null
AGS_BUILD_SHA12 := $(shell $(AGS_BUILD_STAMP_INPUT) | sha256sum | cut -c1-12)

# Appended via += only AFTER AGS_BUILD_SHA12 is fully computed above --
# that recipe hashes AGS_CMAKE_FLAGS's PRIOR (pre-append) value, so baking
# the fingerprint into the very flags the fingerprint hashes would be
# circular (same non-circularity rule dossage's own BUILD_SHA12/
# GAME_CXXFLAGS ordering follows). This is the ONLY -DCMAKE_CXX_FLAGS in
# AGS_CMAKE_FLAGS (CMAKE_COMMON, from sdl3-dos.mk, supplies its own
# separate one) -- cmake's "last -D wins" rule (Measured Constants,
# 2026-09-10) means this single assignment must restate AGS_CXX_FLAGS_BASE
# in full (NOSIMD_FLAGS + the shared/include -I), not just add the new
# -DPORT_BUILD_SHA12 bit, or those would silently stop applying.
#
# DOUBLE backslash before each embedded quote, not single -- a real gap
# found and fixed while landing this (Measured Constants has the full
# diagnosis): there are TWO shell layers between this line and the actual
# compiler invocation (this Makefile's own recipe invoking `cmake`, THEN
# cmake's generated build.make invoking the compiler from its own separate
# recipe), and each layer's shell strips exactly one level of backslash-
# quote escaping. A single \" survives only the first layer, reaching
# flags.make as a bare unescaped ", which the second layer's shell then
# consumes as quoting syntax and strips -- leaving the compiler an
# unquoted bareword value (PORT_BUILD_SHA12 expanding to a bare
# 20a84a45bd83 token, not a string literal), which GCC's pp-number lexer
# then misreads as a numeric literal with a bogus user-defined-literal
# suffix ("unable to find numeric literal operator"). \\\" survives both
# layers intact, landing in the compiler's argv as a real ".
# DOS-PORT patch 0127: opt-in masked-blit run-length statistics build.
# Separate from the normal build on purpose -- the counters live inside
# Allegro's hottest inner loop (libsrc/allegro/src/c/cspr.h), and this
# port's own cache-footprint observations put executed additions to the
# render path at roughly 1 fps. A stats binary is for structure, never
# for a timing comparison. Both C and C++ need the define: the counters
# are defined and incremented in C (cmisc.c, cspr.h) and emitted from
# C++ (Engine/main/quit.cpp).
ifeq ($(AGS_SPRITE_RUN_STATS),1)
AGS_RUNSTATS_DEF := -DDOSAGS_SPRITE_RUN_STATS
AGS_CMAKE_FLAGS += -DCMAKE_C_FLAGS="$(NOSIMD_FLAGS) $(AGS_RUNSTATS_DEF)"
endif

# SDL patch 0198 (2026-09-25): every uclock() in the ags link goes through SDL's IRQ-safe wrapper, which
# makes each PIT read after the first atomic against the SB IRQ (see src/timer/dos/SDL_dosuclockwrap.c).
AGS_CMAKE_FLAGS += -DCMAKE_EXE_LINKER_FLAGS="-Wl,--wrap=uclock"
AGS_CMAKE_FLAGS += -DCMAKE_CXX_FLAGS="$(AGS_CXX_FLAGS_BASE) $(AGS_RUNSTATS_DEF) -DPORT_BUILD_SHA12=\\\"$(AGS_BUILD_SHA12)\\\" -DPORT_BUILD_DIRTY=$(AGS_BUILD_DIRTY)"

.PHONY: build-sha12
build-sha12:
	@echo "$(AGS_BUILD_SHA12)"

# DOS-PORT: report whether this build would be a working-tree build, and
# what the stamp would be. For checking BEFORE a benchmark arm is built,
# rather than discovering it in a cell's manifest afterwards.
.PHONY: stamp-input
stamp-input:
	@$(AGS_BUILD_STAMP_INPUT)

.PHONY: build-dirty
build-dirty:
	@echo "build_dirty=$(AGS_BUILD_DIRTY) sha12=$(AGS_BUILD_SHA12)"

.PHONY: configure-ags
configure-ags: verify-patches-applied $(SYSROOT)/lib/libSDL3.a
	@test -d "$(AGS_SRC)" || (echo "error: $(AGS_SRC) not present -- run make sources" >&2; exit 1)
	cmake -S $(AGS_SRC) -B $(AGS_BUILD_DIR) $(CMAKE_COMMON) $(AGS_CMAKE_FLAGS)

# DJGPP stub minimum stack for ags.exe, set explicitly (operator 2026-11-05). 512 KB is
# what every gate cell and the dist zip measured: it is also stubify's default, so this
# stubedit leaves the exe byte-identical (sha256 checked before/after on both flavours,
# 2026-11-05). Changing it changes the measured binary: re-validate before you do.
AGS_MINSTACK := 512k

.PHONY: build-ags
build-ags: configure-ags
	cmake --build $(AGS_BUILD_DIR) -j$(NPROC)
	$(STUBEDIT) $(AGS_BUILD_DIR)/ags.exe minstack=$(AGS_MINSTACK)

.PHONY: game
game: build-ags

# make dist [DIST_VERSION=v0.1] [DIST_REPO_URL=https://...] -- the player zip:
# builds the RELEASE flavour, then scripts/make-dist.sh packages it
# (build/dist/dosags-$(DIST_VERSION).zip) and scripts/check-dist.sh checks it
# against THIRD-PARTY.md's dist-files table and LICENSE-REVIEW.md. Without
# DIST_REPO_URL the zip is marked not releasable (no public source URL).
DIST_VERSION ?= dev
DIST_REPO_URL ?=
.PHONY: dist
dist:
	$(MAKE) DOSAGS_RELEASE=1 game
	scripts/make-dist.sh --version "$(DIST_VERSION)" $(if $(DIST_REPO_URL),--repo-url "$(DIST_REPO_URL)")

.PHONY: ags-clean
ags-clean:
	rm -rf $(AGS_BUILD_DIR)
