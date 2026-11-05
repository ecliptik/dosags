#!/bin/sh
# tests/probes/djgpp-runtime/run.sh -- does DJGPP's libstdc++/libc provide
# what AGS's engine code assumes? Compile-and-link probes only; nothing runs.
#
# Why: AGS uses std::mutex/std::condition_variable unconditionally
# (Common/debug/debugmanager.cpp, Engine/media/audio/audio_core.cpp),
# std::this_thread::sleep_for + std::chrono (Engine/ac/timer.cpp),
# alfont's ALFONT_DOS path needs <iconv.h>, Allegro's CMakeLists.txt probes
# mmap/mprotect/sys/io.h, and the DOS platform driver needs a free-space
# query. Each of those is a real "does it even build" question that a
# 10-line program answers before any patch is written.
#
# Usage: DJGPP_PREFIX=~/emulators/tools/djgpp ./run.sh
# Results are recorded in README.md next to this script.

set -u
DJGPP_PREFIX="${DJGPP_PREFIX:-$HOME/emulators/tools/djgpp}"
CXX="$DJGPP_PREFIX/bin/i586-pc-msdosdjgpp-g++"
CC="$DJGPP_PREFIX/bin/i586-pc-msdosdjgpp-gcc"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
cd "$WORK" || exit 1

"$CXX" --version | head -1
printf '\n%s\n' "gthreads config macros (empty means libstdc++ has no std::thread/std::mutex):"
echo '#include <bits/c++config.h>' | "$CXX" -x c++ -std=c++11 -dM -E - | grep -E "GTHREADS|_GLIBCXX_USE_NANOSLEEP|_GLIBCXX_HAVE_U?SLEEP" || echo "  (none)"
echo

probe() { # name  compiler  source-on-stdin
    name="$1"; comp="$2"; cat > "$name.src"
    if "$comp" -std=c++11 -O2 -o "$name.exe" -x "${3:-c++}" "$name.src" >"$name.log" 2>&1; then
        printf 'PASS  %s\n' "$name"
    else
        printf 'FAIL  %s  (%s)\n' "$name" "$(grep -m1 -E 'error|fatal' "$name.log" | sed 's/^[^:]*:[0-9]*:[0-9]*: //')"
    fi
}

probe std_mutex "$CXX" <<'EOF'
#include <mutex>
std::mutex m;
int main(){ std::lock_guard<std::mutex> l(m); return 0; }
EOF

probe std_condition_variable "$CXX" <<'EOF'
#include <condition_variable>
int main(){ std::condition_variable cv; (void)cv; return 0; }
EOF

probe std_thread "$CXX" <<'EOF'
#include <thread>
int main(){ std::thread t([]{}); t.join(); return 0; }
EOF

probe std_this_thread_sleep_for "$CXX" <<'EOF'
#include <chrono>
#include <thread>
int main(){ auto t=std::chrono::steady_clock::now(); std::this_thread::sleep_for(std::chrono::milliseconds(1)); return t.time_since_epoch().count()>0; }
EOF

probe std_atomic "$CXX" <<'EOF'
#include <atomic>
std::atomic<int> a{0};
int main(){ a.fetch_add(1); return a.load(); }
EOF

probe iconv_h "$CC" c <<'EOF'
#include <iconv.h>
int main(){ return iconv_open("UTF-8","CP437")==(iconv_t)-1; }
EOF

probe locale_mbstowcs_wchar "$CC" c <<'EOF'
#include <locale.h>
#include <wchar.h>
#include <stdlib.h>
int main(){ wchar_t w[8]; setlocale(LC_ALL,""); return (int)mbstowcs(w,"ab",8); }
EOF

probe mmap_mprotect_symbols "$CC" c <<'EOF'
char mmap(); char mprotect();
int main(){ return mmap()+mprotect(); }
EOF

probe sys_io_h "$CC" c <<'EOF'
#include <sys/io.h>
int main(){ return 0; }
EOF

probe allegro_unix_headers "$CC" c <<'EOF'
#include <dirent.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/utsname.h>
#include <inttypes.h>
#include <stdint.h>
int main(){ return 0; }
EOF

probe statfs "$CC" c <<'EOF'
#include <sys/vfs.h>
int main(){ struct statfs s; return statfs(".",&s) ? 1 : (int)(s.f_bsize*s.f_bfree>0); }
EOF
