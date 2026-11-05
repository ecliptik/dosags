// Host/DOS fuzz for ags patch 0215: old vs new dos_audio_decode_pcm, sample for sample.
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#define DOS_AUDIO_MIXER_RATE 11025
namespace oldv {
#include "old_body.inc"
}
namespace newv {
#include "new_body.inc"
}
static uint32_t rng = 12345u;
static uint32_t rnd() { rng = rng * 1103515245u + 12345u; return rng >> 8; }
static void put16(std::vector<uint8_t> &v, uint16_t x) { v.push_back(x & 255); v.push_back(x >> 8); }
static void put32(std::vector<uint8_t> &v, uint32_t x) { put16(v, x & 0xffff); put16(v, x >> 16); }
// kind 0 random, 1 runs of repeats, 2 extremes, 3 ramp, 4 small-step noise
static uint8_t sample_byte(int kind, size_t k, uint8_t prev)
{
    switch (kind) {
    case 0: return (uint8_t)rnd();
    case 1: return (rnd() % 4 == 0) ? (uint8_t)rnd() : prev;
    case 2: return (rnd() & 1) ? 0xff : 0x00;
    case 3: return (uint8_t)(k * 7);
    default: return (uint8_t)(prev + (int)(rnd() % 5) - 2);
    }
}
static std::vector<uint8_t> make_wav(int rate, int ch, int bits, size_t frames, int kind)
{
    std::vector<uint8_t> body;
    uint8_t prev = 128;
    size_t nbytes = frames * ch * (bits / 8) + (rnd() % 3 == 0 ? rnd() % 3 : 0); // odd tails too
    for (size_t k = 0; k < nbytes; k++) { prev = sample_byte(kind, k, prev); body.push_back(prev); }
    std::vector<uint8_t> v;
    v.insert(v.end(), {'R','I','F','F'}); put32(v, 36 + (uint32_t)body.size());
    v.insert(v.end(), {'W','A','V','E','f','m','t',' '}); put32(v, 16);
    put16(v, 1); put16(v, ch); put32(v, rate); put32(v, rate * ch * bits / 8); put16(v, ch * bits / 8); put16(v, bits);
    v.insert(v.end(), {'d','a','t','a'}); put32(v, (uint32_t)body.size());
    v.insert(v.end(), body.begin(), body.end());
    return v;
}
static std::vector<uint8_t> make_voc(size_t blocks, int kind)
{
    std::vector<uint8_t> v(26, 0);
    std::memcpy(v.data(), "Creative Voice File\x1a", 20);
    v[20] = 26; v[21] = 0;
    uint8_t prev = 128;
    for (size_t b = 0; b < blocks; b++) {
        size_t n = 50 + rnd() % 3000;
        uint8_t rate_byte = (uint8_t)(100 + rnd() % 150);
        v.push_back(1); uint32_t len = (uint32_t)n + 2;
        v.push_back(len & 255); v.push_back((len >> 8) & 255); v.push_back(len >> 16);
        v.push_back(rate_byte); v.push_back(0);
        for (size_t k = 0; k < n; k++) { prev = sample_byte(kind, k, prev); v.push_back(prev); }
    }
    v.push_back(0);
    return v;
}
int main(int argc, char **argv)
{
    const int cases = argc > 1 ? atoi(argv[1]) : 2000;
    static const int rates[] = { 8000, 11000, 11025, 16000, 22050, 24000, 32000, 44100, 48000, 5512, 7350, 12345, 96000 };
    long long samples = 0, mism = 0, lenmism = 0;
    for (int c = 0; c < cases; c++) {
        std::vector<uint8_t> clip;
        const int kind = rnd() % 5;
        if (c % 10 == 9) clip = make_voc(1 + rnd() % 4, kind);
        else {
            const int rate = rates[rnd() % (sizeof(rates) / sizeof(rates[0]))];
            const int ch = 1 + rnd() % 3;
            const int bits = (rnd() & 1) ? 8 : 16;
            clip = make_wav(rate, ch, bits, 1 + rnd() % 20000, kind);
        }
        std::vector<int16_t> a, b;
        const bool ra = oldv::dos_audio_decode_pcm(clip.data(), clip.size(), a);
        const bool rb = newv::dos_audio_decode_pcm(clip.data(), clip.size(), b);
        if (ra != rb || a.size() != b.size()) { lenmism++; continue; }
        samples += (long long)a.size();
        for (size_t k = 0; k < a.size(); k++)
            if (a[k] != b[k]) { if (mism < 5) printf("case %d sample %lu old %d new %d\n", c, (unsigned long)k, a[k], b[k]); mism++; }
    }
    printf("FUZZ0215 cases=%d samples=%lld mismatches=%lld length_or_result_mismatches=%lld\n", cases, samples, mism, lenmism);
    return (mism || lenmism) ? 1 : 0;
}
