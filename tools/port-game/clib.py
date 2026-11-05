#!/usr/bin/env python3
"""clib.py -- read/write support for AGS's MFL ("CLIB") asset library
format, transcribed directly from the pinned engine source
(vendor/ags/Common/data/multifilelib.cpp, MFLUtil namespace) rather than
guessed or reused from tests/fixtures/minimal-game-package/build_fixture.py
(that file only ever wrote the old kMFLVersion_SingleLib==6 format for a
synthetic bring-up fixture at one specific DataVersion; a real shipped
game's CLIB is a different, later format entirely -- confirmed by
inspecting a real notes.exe, whose CLIB header decodes to lib_version=15,
squarely in the 10-19 "old format, longer filenames absent, decrypted"
range multifilelib.cpp's ReadV10 handles).

Read support covers every version the engine itself can read
(SingleLib=6, V10/11, V15, V20, V21, V30) so `inspect` can open any real
golden-reference game regardless of which AGS Editor version built it.
Write support only emits V30 (the one format multifilelib.cpp itself can
write -- WriteHeader() always calls WriteV30() for the base datafile;
there never was a V10/V15/V20/V21 *writer* in the engine, only readers for
files older builds already produced), which `repack.py` uses regardless of
the source game's own original version -- the engine's own ReadHeader()
accepts any supported version on load, so re-emitting a newer version than
the original is not a compatibility problem for our own engine build.

License: MIT (this file, dosags's own tooling). See LICENSE in repo root.
"""
import struct
from dataclasses import dataclass, field

HEAD_SIG = b"CLIB\x1a"
HEAD_SIG_MINIMAL = b"CLIB"
TAIL_SIG = b"CLIB\x01\x02\x03\x04SIGE"

SINGLE_FILE_PSW_LEN = 13
MAX_ASSET_FILE_LEN = 100
MAX_DATA_FILE_LEN = 50
V10_LIB_FILE_LEN = 20
V10_ASSET_FILE_LEN = 25

ENCRYPTION_STRING = b"My\x01\xde\x04Jibzle"  # MFLUtil::EncryptionString, multifilelib.cpp:38

MFL_SINGLE_LIB = 6
MFL_MULTI_V10 = 10
MFL_MULTI_V11 = 11
MFL_MULTI_V15 = 15
MFL_MULTI_V20 = 20
MFL_MULTI_V21 = 21
MFL_MULTI_V30 = 30

SUPPORTED_VERSIONS = (MFL_SINGLE_LIB, MFL_MULTI_V10, MFL_MULTI_V11, MFL_MULTI_V15,
                      MFL_MULTI_V20, MFL_MULTI_V21, MFL_MULTI_V30)


class MFLError(Exception):
    pass


@dataclass
class AssetInfo:
    file_name: str
    size: int
    offset: int = 0     # absolute offset into the source file, filled in by the reader
    lib_uid: int = 0


@dataclass
class AssetLib:
    lib_version: int
    lib_file_names: list = field(default_factory=list)
    assets: list = field(default_factory=list)   # list[AssetInfo]
    base_file_offset: int = 0


def _decrypt_text(raw: bytes) -> bytes:
    """MFLUtil::DecryptText (multifilelib.cpp:450-465): text[i] -=
    EncryptionString[adx], stops at the first byte that becomes 0, adx
    wraps to 0 once it exceeds 10."""
    out = bytearray()
    adx = 0
    for b in raw:
        v = (b - ENCRYPTION_STRING[adx]) & 0xFF
        if v == 0:
            break
        out.append(v)
        adx += 1
        if adx > 10:
            adx = 0
    return bytes(out)


def _read_cstr(data: bytes, pos: int):
    end = data.index(b"\x00", pos)
    return data[pos:end].decode("latin1"), end + 1


def _find_header_signature(data: bytes):
    """MFLUtil::ReadSigsAndVersion (multifilelib.cpp:143-209), the
    "signature not at start of file" branch only (appended-to-EXE case) --
    the plain "signature at file start" case is handled by the caller
    before reaching here. Returns the absolute offset of HEAD_SIG."""
    if len(data) < len(TAIL_SIG):
        raise MFLError("file too small to contain a CLIB tail signature")
    tail_abs_offset = len(data) - len(TAIL_SIG)
    if data[tail_abs_offset:tail_abs_offset + len(TAIL_SIG)] != TAIL_SIG:
        raise MFLError("no CLIB head or tail signature found")
    off64_pos = tail_abs_offset - 8
    abs_offset_64 = struct.unpack_from("<q", data, off64_pos)[0]
    abs_offset_32 = struct.unpack_from("<i", data, off64_pos + 4)[0]
    for abs_offset in (abs_offset_64, abs_offset_32):
        if 0 < abs_offset < tail_abs_offset - len(HEAD_SIG):
            sig = data[abs_offset:abs_offset + len(HEAD_SIG)]
            if sig == HEAD_SIG or sig[:4] == HEAD_SIG_MINIMAL:
                return abs_offset
    raise MFLError("tail signature present but neither 32-bit nor 64-bit "
                    "offset field points at a real head signature")


def read_header(data: bytes) -> AssetLib:
    """Mirrors MFLUtil::ReadHeader. `data` is the *whole* file (a
    standalone .ags, or a notes.exe-style EXE with the CLIB appended --
    either is handled the same way the real engine handles it)."""
    if data[:len(HEAD_SIG)] == HEAD_SIG or data[:4] == HEAD_SIG_MINIMAL:
        base = 0
    else:
        base = _find_header_signature(data)

    pos = base + len(HEAD_SIG)
    lib_version = data[pos]
    pos += 1
    if lib_version not in SUPPORTED_VERSIONS:
        raise MFLError(f"unsupported CLIB lib_version {lib_version}")

    lib = AssetLib(lib_version=lib_version)

    if lib_version < MFL_MULTI_V10:
        # ReadSingleFileLib (multifilelib.cpp:211-244)
        passwmodifier = data[pos]; pos += 1
        pos += 1  # unused byte
        asset_count = struct.unpack_from("<H", data, pos)[0]; pos += 2
        lib.lib_file_names = [""]
        pos += SINGLE_FILE_PSW_LEN  # password dooberry, skipped
        names = []
        for _ in range(asset_count):
            raw = data[pos:pos + SINGLE_FILE_PSW_LEN]; pos += SINGLE_FILE_PSW_LEN
            # ReadSingleFileLib's own loop (multifilelib.cpp:226-227):
            # `for (char *c = fn_buf; *c; ++c) *c -= passwmodifier;` walks
            # the RAW (undecrypted) bytes and stops at the first one that
            # is already zero -- it never decrypts, or includes, anything
            # from that point on (padding included). Decrypting the whole
            # fixed-length field first and THEN stripping NULs (as this
            # code used to) is wrong: subtracting passwmodifier from a
            # raw zero PADDING byte produces a non-zero garbage byte, so
            # the trailing padding survives into the name instead of
            # being dropped -- confirmed against a real V6 SingleLib
            # CLIB (Maniac Mansion Deluxe's speech.vox), the first golden
            # reference to ever exercise this code path.
            name_bytes = bytearray()
            for b in raw:
                if b == 0:
                    break
                name_bytes.append((b - passwmodifier) & 0xFF)
            names.append(name_bytes.decode("latin1"))
        sizes = []
        for _ in range(asset_count):
            sizes.append(struct.unpack_from("<I", data, pos)[0]); pos += 4
        pos += 2 * asset_count  # flags & ratio, skipped
        offset = pos
        for name, size in zip(names, sizes):
            lib.assets.append(AssetInfo(file_name=name, size=size, offset=offset, lib_uid=0))
            offset += size
    else:
        file_number = data[pos]; pos += 1
        if file_number != 0:
            raise MFLError("not the base datafile in this CLIB chain")

        if lib_version >= MFL_MULTI_V30:
            pos += 4  # reserved options (int32), WriteV30/ReadV30
            mf_count = struct.unpack_from("<i", data, pos)[0]; pos += 4
            for _ in range(mf_count):
                name, pos = _read_cstr(data, pos)
                lib.lib_file_names.append(name)
            asset_count = struct.unpack_from("<i", data, pos)[0]; pos += 4
            for _ in range(asset_count):
                name, pos = _read_cstr(data, pos)
                lib_uid = data[pos]; pos += 1
                offset, size = struct.unpack_from("<qq", data, pos); pos += 16
                lib.assets.append(AssetInfo(file_name=name, size=size, offset=offset, lib_uid=lib_uid))
        elif lib_version >= MFL_MULTI_V21:
            raise MFLError("MultiV21 (encrypted, RNG-keyed) read not implemented -- "
                            "no golden-reference game has needed it yet")
        elif lib_version == MFL_MULTI_V20:
            mf_count = struct.unpack_from("<i", data, pos)[0]; pos += 4
            for _ in range(mf_count):
                name, pos = _read_cstr(data, pos)  # String::Read(MaxDataFileLen) truncates; cstr is close enough
                lib.lib_file_names.append(name)
            asset_count = struct.unpack_from("<i", data, pos)[0]; pos += 4
            names = []
            for _ in range(asset_count):
                strlen = struct.unpack_from("<H", data, pos)[0]; pos += 2
                strlen //= 5  # ReadV20's own "CHECKME: why 5?", multifilelib.cpp:322
                raw = data[pos:pos + strlen]; pos += strlen
                names.append(_decrypt_text(raw).decode("latin1"))
            offsets = []
            for _ in range(asset_count):
                offsets.append(struct.unpack_from("<I", data, pos)[0]); pos += 4
            sizes = []
            for _ in range(asset_count):
                sizes.append(struct.unpack_from("<I", data, pos)[0]); pos += 4
            lib_uids = []
            for _ in range(asset_count):
                lib_uids.append(data[pos]); pos += 1
            for name, off, size, uid in zip(names, offsets, sizes, lib_uids):
                lib.assets.append(AssetInfo(file_name=name, size=size, offset=off, lib_uid=uid))
        else:
            # ReadV10 (multifilelib.cpp:270-301), covers versions 10-19
            mf_count = struct.unpack_from("<i", data, pos)[0]; pos += 4
            for _ in range(mf_count):
                raw = data[pos:pos + V10_LIB_FILE_LEN]; pos += V10_LIB_FILE_LEN
                lib.lib_file_names.append(raw.rstrip(b"\x00").decode("latin1"))
            asset_count = struct.unpack_from("<i", data, pos)[0]; pos += 4
            names = []
            for _ in range(asset_count):
                raw = data[pos:pos + V10_ASSET_FILE_LEN]; pos += V10_ASSET_FILE_LEN
                if lib_version >= MFL_MULTI_V11:
                    names.append(_decrypt_text(raw).decode("latin1"))
                else:
                    names.append(raw.rstrip(b"\x00").decode("latin1"))
            offsets = []
            for _ in range(asset_count):
                offsets.append(struct.unpack_from("<i", data, pos)[0]); pos += 4
            sizes = []
            for _ in range(asset_count):
                sizes.append(struct.unpack_from("<i", data, pos)[0]); pos += 4
            lib_uids = []
            for _ in range(asset_count):
                lib_uids.append(data[pos]); pos += 1
            for name, off, size, uid in zip(names, offsets, sizes, lib_uids):
                lib.assets.append(AssetInfo(file_name=name, size=size, offset=off, lib_uid=uid))

    # ReadHeader's own "apply absolute offset for assets contained in the
    # base data file" step (multifilelib.cpp:122-132): only meaningful for
    # the appended-to-EXE case (base != 0); a standalone .ags has base==0
    # and this is a no-op.
    if base > 0:
        lib.base_file_offset = base
        for a in lib.assets:
            if a.lib_uid == 0:
                a.offset += base
    return lib


def write_v30(lib_file_names, assets_with_data, out_path):
    """Mirrors MFLUtil::WriteHeader (lib_index=0) + WriteV30 + WriteEnder
    for a single-part, standalone base library (multifilelib.cpp:399-440).
    `assets_with_data`: list of (file_name: str, data: bytes), written in
    order; offsets are computed here, not passed in, so a caller can just
    hand over (name, bytes) pairs from convert.py's own output without
    tracking layout math itself. lib_uid is always 0 (single-part lib --
    every port-game golden reference is one CLIB, no multi-part chains)."""
    header = bytearray()
    header += HEAD_SIG
    header += struct.pack("<B", MFL_MULTI_V30)
    header += struct.pack("<B", 0)  # lib_index (file number) -- base file

    toc = bytearray()
    toc += struct.pack("<i", 0)  # reserved options
    toc += struct.pack("<i", len(lib_file_names))
    for name in lib_file_names:
        toc += name.encode("latin1") + b"\x00"
    toc += struct.pack("<i", len(assets_with_data))

    # Two passes: offsets depend on the total TOC size, which depends on
    # every asset's own filename length -- so lay out names first, then
    # fill in offsets once the payload's start position is known.
    per_asset_header_len = []
    for name, _data in assets_with_data:
        per_asset_header_len.append(len(name) + 1 + 1 + 8 + 8)  # cstr + lib_uid(i8) + offset(i64) + size(i64)
    toc_asset_section_len = sum(per_asset_header_len)
    payload_start = len(header) + len(toc) + toc_asset_section_len

    offset = payload_start
    asset_toc = bytearray()
    payload = bytearray()
    for name, data in assets_with_data:
        asset_toc += name.encode("latin1") + b"\x00"
        asset_toc += struct.pack("<b", 0)  # lib_uid
        asset_toc += struct.pack("<q", offset)
        asset_toc += struct.pack("<q", len(data))
        payload += data
        offset += len(data)

    lib_offset = 0  # this file's own CLIB starts at byte 0 -- a standalone .ags, never appended to an EXE
    ender = struct.pack("<q", lib_offset) + TAIL_SIG

    with open(out_path, "wb") as f:
        f.write(header)
        f.write(toc)
        f.write(asset_toc)
        f.write(payload)
        f.write(ender)


def read_main_game_file_header(data: bytes, asset_offset: int):
    """OpenMainGameFileBase (main_game_file.cpp:162-191): 30-byte
    signature, int32 DataVersion, then a length-prefixed CompiledWith
    string (present unconditionally since AGS 2.30, i.e. every DataVersion
    this tool will ever see -- kGameVersion_230==12 is far below the
    kGameVersion_250==18 floor `inspect` already requires)."""
    SIG = b"Adventure Creator Game File v2"
    pos = asset_offset
    sig = data[pos:pos + len(SIG)]
    if sig != SIG:
        raise MFLError(f"expected main game file signature at offset {asset_offset}, got {sig!r}")
    pos += len(SIG)
    data_version = struct.unpack_from("<i", data, pos)[0]; pos += 4
    strlen = struct.unpack_from("<i", data, pos)[0]; pos += 4
    compiled_with = data[pos:pos + strlen].decode("latin1"); pos += strlen
    # gamename: String::ReadCount(50) (gamesetupstructbase.cpp) -- a fixed
    # 50-byte buffer, NUL-padded, immediately following CompiledWith.
    gamename_raw = data[pos:pos + 50]
    gamename = gamename_raw.split(b"\x00", 1)[0].decode("latin1")
    return {"data_version": data_version, "compiled_with": compiled_with, "gamename": gamename}
