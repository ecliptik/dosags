/*
 * wsprobe.c -- BOOTSTRAP-0 probe 3: window-surface + palette smoke test.
 *
 * Standalone SDL3 program, no AGS code at all. Exercises exactly the
 * presentation path PATCH-SEQUENCE.md's patch 0017 commits AGS's own
 * graphics driver (Engine/gfx/ali3dsw.cpp) to: SDL_GetWindowSurface +
 * one blit/fill + SDL_UpdateWindowSurface, at the game's own depth,
 * instead of SDL_Renderer/SDL_Texture. Run at 8bpp (paletted,
 * SDL_HINT_DOS_MAX_BPP=8) with a palette set and synced, then at 16bpp
 * (SDL_HINT_DOS_MAX_BPP=16) and 32bpp (SDL_HINT_DOS_MAX_BPP=32) with the
 * queried surface format used to compute fill values, rather than a
 * hardcoded RGB565/555/XRGB8888 assumption. The 32bpp run is this
 * probe's own validation of PLAN.md's "32-bit display path -- design
 * comparison" section (operator decision, Option 1, 2026-09-15) -- the
 * shared SDL3-DOS backend's VESA/LFB present path had never actually run
 * at 32bpp before this, on DOSBox-X or real hardware, independent of
 * whether AGS's own ali3dsw.cpp gate (patch 0075) let a game request it.
 *
 * Output is printf()/stdout only, never SDL_Log() -- see
 * .sdl-dos-ports/shared/tests/sdl3-smoke/sdltest.c's own header comment:
 * SDL_Log() writes to stderr, and the headless DOSBox-X harness this
 * probe is run under cannot capture stderr (neither MS-DOS COMMAND.COM
 * nor DOSBox-X's own shell support `2>&1`). Every line is prefixed with
 * a fixed tag so a runner can grep known-stable substrings.
 *
 * License: MIT (this file, dosags's own). See LICENSE in repo root.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

#include <SDL3/SDL.h>

/*
 * Link-satisfying stub, NOT a real fix -- see tests/probes/window-surface-
 * smoke/README.md's "Unrelated finding" section. vendor/SDL/src/audio/dos/
 * SDL_dosaudio_sb.c:292 declares `extern volatile uint32_t
 * g_dos_sfx_synth_active_count;` with the comment "engine -> SDL extern":
 * SDL's own DOS SoundBlaster backend expects the CONSUMING ENGINE to define
 * and maintain this counter (doskutsu/NXEngine's PixTone active-voice
 * count). SDL_audio.c's static driver bootstrap table references
 * DOSSOUNDBLASTER_bootstrap unconditionally, so SDL_dosaudio_sb.c.obj (and
 * this unresolved extern) is pulled into EVERY DJGPP link against this
 * sysroot's libSDL3.a, even a video-only, SDL_INIT_AUDIO-free program like
 * this one. AGS has no PixTone-equivalent counter, so this repo needs its
 * own permanent decision (a real stub translation unit, most likely landing
 * alongside patch 0012/0018's audio stubs) rather than each probe/binary
 * improvising its own copy -- this local `= 0` definition only unblocks
 * THIS probe's build.
 */
volatile uint32_t g_dos_sfx_synth_active_count = 0;

/*
 * Second link-satisfying stub, same non-fix status as the one above --
 * added when rebuilding this probe against a newer sysroot picked up
 * vendor/SDL/src/timer/dos/SDL_dos_scheduler.c's `extern uclock_t
 * dos_port_engine_start_uclock;` (an engine -> SDL extern in the same
 * shape as g_dos_sfx_synth_active_count, this one landed later than this
 * probe's original build). AGS itself defines and sets the real one at
 * `Engine/main/main.cpp:77` (`dos_port_engine_start_uclock = uclock();`
 * at startup, used to compute ms-since-start timestamps throughout the
 * engine) -- this probe has no engine startup to hook, so `0` just makes
 * any scheduler code that reads it see "elapsed since the DOS epoch",
 * which this video-only probe never actually consumes.
 */
uclock_t dos_port_engine_start_uclock = 0;

/* Long enough for an external screenshot tool to grab the window before
 * the probe moves on to the next depth or exits. */
#define DISPLAY_DELAY_MS 8000

static int run_depth(const char *bpp_hint, const char *tag)
{
    /* The hint must be set BEFORE SDL_Init(SDL_INIT_VIDEO), not merely
     * before SDL_CreateWindow -- confirmed empirically (an earlier version
     * of this probe set it after one shared SDL_Init() call and got
     * XRGB8888 at every depth). vendor/SDL/src/video/dos/SDL_dosvideo.c's
     * DOSVESA_VideoInit() (device->VideoInit, run once by SDL_Init) calls
     * DOSVESA_GetDisplayModes() directly, which is where the hint's bpp
     * cap actually filters the enumerated VESA mode list; that list is
     * then cached for the display's lifetime. So each depth needs its own
     * Init/Quit cycle with the hint set first. A real port only needs one
     * such cycle (it picks its depth once at startup and never changes
     * it); this probe does two only to compare them in one run. */
    printf("%s: SDL_SetHint(SDL_DOS_MAX_BPP, \"%s\")\n", tag, bpp_hint);
    if (!SDL_SetHint(SDL_HINT_DOS_MAX_BPP, bpp_hint)) {
        printf("%s: SDL_SetHint FAILED: %s\n", tag, SDL_GetError());
        return 1;
    }

    if (!SDL_InitSubSystem(SDL_INIT_VIDEO)) {
        printf("%s: SDL_InitSubSystem(VIDEO) FAILED: %s\n", tag, SDL_GetError());
        return 1;
    }
    printf("%s: SDL_InitSubSystem(VIDEO) OK driver=%s\n", tag, SDL_GetCurrentVideoDriver());

    /* SDL_WINDOW_FULLSCREEN is required to trigger a real VESA mode-set on
     * this backend -- there is no DOS window manager, so a non-fullscreen
     * create does not pick a hardware mode at all (confirmed empirically:
     * an earlier run of this probe without the flag got a constant
     * SDL_PIXELFORMAT_XRGB8888 surface regardless of SDL_DOS_MAX_BPP,
     * indicating no VESA mode-set happened). doskutsu's own window creation
     * always passes this flag (patches/SDL/0012's commit message shows
     * `SDL_CreateWindow(320, 240, FULLSCREEN)`).
     *
     * 320x240, not 320x200: doskutsu's own committed VESA mode fixture
     * (~/git/doskutsu/tests/fixtures/sdl3-modes-dosbox.txt, captured under
     * the same DOSBox-X setup) lists NO 320x200 entry at all under this
     * emulated card's VESA BIOS -- only 320x240/320x400/320x480 exist.
     * Requesting the unlisted 320x200 made SDL's closest-mode matching
     * fall back to a default XRGB8888 surface regardless of
     * SDL_DOS_MAX_BPP (confirmed empirically: still XRGB8888 even with
     * FULLSCREEN added). 320x240 has real INDEX8/RGB565/XRGB1555 entries
     * in that fixture, matching PLAN.md's own "320x200/240" TITLE_SCREEN
     * wording. */
    SDL_Window *window = SDL_CreateWindow("wsprobe", 320, 240, SDL_WINDOW_FULLSCREEN);
    if (!window) {
        printf("%s: SDL_CreateWindow FAILED: %s\n", tag, SDL_GetError());
        return 1;
    }

    SDL_Surface *surface = SDL_GetWindowSurface(window);
    if (!surface) {
        printf("%s: SDL_GetWindowSurface FAILED: %s\n", tag, SDL_GetError());
        SDL_DestroyWindow(window);
        return 1;
    }

    const char *fmt_name = SDL_GetPixelFormatName(surface->format);
    printf("%s: format=%s w=%d h=%d pitch=%d\n",
           tag, fmt_name ? fmt_name : "(null)",
           surface->w, surface->h, surface->pitch);

    const SDL_PixelFormatDetails *details =
        SDL_GetPixelFormatDetails(surface->format);
    if (!details) {
        printf("%s: SDL_GetPixelFormatDetails FAILED: %s\n", tag, SDL_GetError());
        SDL_DestroyWindow(window);
        return 1;
    }
    printf("%s: bits_per_pixel=%d bytes_per_pixel=%d "
           "Rmask=0x%08x Gmask=0x%08x Bmask=0x%08x\n",
           tag, details->bits_per_pixel, details->bytes_per_pixel,
           (unsigned)details->Rmask, (unsigned)details->Gmask,
           (unsigned)details->Bmask);

    int is_indexed = (SDL_ISPIXELFORMAT_INDEXED(surface->format) != 0);
    printf("%s: indexed=%d\n", tag, is_indexed);

    /* Four quadrants, four distinct colors -- red / green / blue / white --
     * so a screenshot can visually confirm which color landed where,
     * not just that the API calls returned success. */
    struct { int r, g, b; } colors[4] = {
        {255, 0, 0}, {0, 255, 0}, {0, 0, 255}, {255, 255, 255}
    };
    SDL_Rect quads[4] = {
        {0, 0, 160, 120}, {160, 0, 160, 120},
        {0, 120, 160, 120}, {160, 120, 160, 120}
    };

    if (is_indexed) {
        SDL_Palette *palette = SDL_CreateSurfacePalette(surface);
        if (!palette) {
            printf("%s: SDL_CreateSurfacePalette FAILED: %s\n", tag, SDL_GetError());
            SDL_DestroyWindow(window);
            return 1;
        }
        SDL_Color pal_colors[4];
        for (int i = 0; i < 4; ++i) {
            pal_colors[i].r = (Uint8)colors[i].r;
            pal_colors[i].g = (Uint8)colors[i].g;
            pal_colors[i].b = (Uint8)colors[i].b;
            pal_colors[i].a = 255;
        }
        if (!SDL_SetPaletteColors(palette, pal_colors, 0, 4)) {
            printf("%s: SDL_SetPaletteColors FAILED: %s\n", tag, SDL_GetError());
            SDL_DestroyWindow(window);
            return 1;
        }
        printf("%s: SDL_CreateSurfacePalette + SDL_SetPaletteColors ok (indices 0-3)\n", tag);

        /* For an indexed surface, the fill "color" IS the palette index. */
        for (int i = 0; i < 4; ++i) {
            if (!SDL_FillSurfaceRect(surface, &quads[i], (Uint32)i)) {
                printf("%s: SDL_FillSurfaceRect(index=%d) FAILED: %s\n",
                       tag, i, SDL_GetError());
                SDL_DestroyWindow(window);
                return 1;
            }
        }
        printf("%s: SDL_FillSurfaceRect x4 (palette indices) ok\n", tag);
    } else {
        /* Direct-color surface: compute the fill value FROM the queried
         * format via SDL_MapRGB, rather than assuming RGB565 or RGB555. */
        for (int i = 0; i < 4; ++i) {
            Uint32 pixel = SDL_MapRGB(details, NULL,
                                       (Uint8)colors[i].r,
                                       (Uint8)colors[i].g,
                                       (Uint8)colors[i].b);
            if (!SDL_FillSurfaceRect(surface, &quads[i], pixel)) {
                printf("%s: SDL_FillSurfaceRect(pixel=0x%08x) FAILED: %s\n",
                       tag, (unsigned)pixel, SDL_GetError());
                SDL_DestroyWindow(window);
                return 1;
            }
        }
        printf("%s: SDL_FillSurfaceRect x4 (SDL_MapRGB-derived pixels) ok\n", tag);
    }

    if (!SDL_UpdateWindowSurface(window)) {
        printf("%s: SDL_UpdateWindowSurface FAILED: %s\n", tag, SDL_GetError());
        SDL_DestroyWindow(window);
        return 1;
    }
    printf("%s: SDL_UpdateWindowSurface ok\n", tag);
    fflush(stdout);

    SDL_Delay(DISPLAY_DELAY_MS);

    SDL_DestroyWindow(window);
    SDL_QuitSubSystem(SDL_INIT_VIDEO);
    return 0;
}

int main(int argc, char *argv[])
{
    (void)argc;
    (void)argv;

    printf("WSPROBE-BEGIN: sdl-dos-ports window-surface probe (SDL3 %d.%d.%d)\n",
           SDL_MAJOR_VERSION, SDL_MINOR_VERSION, SDL_MICRO_VERSION);
    fflush(stdout);

    int rc8 = run_depth("8", "PALETTE-8BPP");
    fflush(stdout);
    int rc16 = run_depth("16", "FORMAT-16BPP");
    fflush(stdout);
    int rc32 = run_depth("32", "FORMAT-32BPP");
    fflush(stdout);

    int rc = (rc8 != 0 || rc16 != 0 || rc32 != 0) ? 1 : 0;
    printf("WSPROBE-END: rc=%d bpp8=%d bpp16=%d bpp32=%d\n", rc, rc8, rc16, rc32);
    fflush(stdout);
    return rc;
}
