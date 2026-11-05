# djgpp-runtime probe

`run.sh` compiles and links a dozen ten-line programs against the DJGPP
cross toolchain to answer "does this even build under DJGPP" for every
C++/libc facility AGS's engine code assumes. Compile-only; nothing runs on
DOS. See the script's header comment for why each probe exists.

## Results, 2026-09-10

Toolchain: `i586-pc-msdosdjgpp-g++ (GCC) 12.2.0` at `~/emulators/tools/djgpp`.
libstdc++ configuration: `_GLIBCXX_HAS_GTHREADS` **not defined**
(`_GLIBCXX_HAVE_SLEEP`/`_GLIBCXX_HAVE_USLEEP` are).

| Probe | Result | Consequence for the port |
|---|---|---|
| `std::mutex` | **FAIL** -- `'mutex' in namespace 'std' does not name a type` | `AGS_DISABLE_THREADS` is not sufficient: `debugmanager.cpp/.h` and `audio_core.cpp/.h` use `std::mutex` unconditionally. Needs a DOS no-op shim patch (`PATCH-SEQUENCE.md` 0010). |
| `std::condition_variable` | **FAIL** | Same patch (`audio_core.cpp:49`). |
| `std::thread` | **FAIL** -- class exists as a shell, no usable constructor | Already behind `AGS_DISABLE_THREADS`; fine. |
| `std::this_thread::sleep_for` + `std::chrono::steady_clock` | PASS | `Engine/ac/timer.cpp`'s frame pacing builds as-is. Precision under the DOS cooperative scheduler is a separate runtime question. |
| `std::atomic<int>` | PASS | |
| `<iconv.h>` | **FAIL** -- header absent | alfont's `ALFONT_DOS` path (`alfont.c:20`) is the *iconv* path -- do **not** define `ALFONT_DOS`. |
| `setlocale`/`mbstowcs`/`wchar.h` | PASS | alfont's default (non-DOS) path builds against what DJGPP has. |
| `mmap`/`mprotect` symbols | **FAIL** (absent from libc; `<sys/mman.h>` exists but is a broken stub) | Allegro's `check_function_exists(mmap/mprotect)` will come back false -- expected, not a blocker for the headless subset. |
| `<sys/io.h>` | **FAIL** -- header absent | Allegro's `check_include_files(sys/io.h)` comes back false -- expected. |
| `dirent.h`, `sys/stat.h`, `sys/time.h`, `sys/utsname.h`, `inttypes.h`, `stdint.h` | PASS | Allegro's remaining Unix-branch header probes succeed. |
| `statfs()` from `<sys/vfs.h>` | PASS | Mechanism for `AGSPlatformDriver::GetDiskFreeSpaceMB()` identified. Runtime correctness under DOSBox-X still to verify. |
