# Build modernization patches

These patches let the original `v2.0.1` source compile with a modern host
toolchain (GCC 13, on top of Boost 1.54.0 and OpenSSL 1.0.1h rebuilt from
source to match the original era). Every change here is a **build-tooling
or type-disambiguation fix**, not a logic change. None of them touch
genesis parsing, key/address derivation, transaction serialization, or
consensus rules.

## modernization.patch (root repo)

- **Removed `signals` and `locale` from the required Boost components list.**
  Neither is referenced anywhere in the actual C++ source (verified by
  grep across `libraries/` and `programs/`) — this was dead build
  configuration, likely left over from an earlier version of the code.
  `boost::signals` (v1, deprecated even in 2014) was fully superseded by
  `boost::signals2` (still present, header-only, no linking required) by
  the time this code was written.

- **Qualified ambiguous `int64_t` references as `::int64_t`.** Some
  internal namespace in this codebase has a local `using namespace std;`
  that, combined with `<stdint.h>` also declaring `::int64_t` in the
  global namespace, makes bare `int64_t` ambiguous to a modern compiler
  (older compilers resolved this silently). `::int64_t` and `std::int64_t`
  are the identical 64-bit signed integer type on this platform — this
  change only tells the compiler which spelling to use, it cannot change
  a stored value, a hash input, or a wire format.

- **Hardcoded the git-revision build-info string** instead of calling
  `get_git_head_revision()`, which fails when the source tree is a git
  worktree rather than a full clone. This only affects the string printed
  by `--version`; it is not part of any consensus or network-facing data.

## fc-modernization.patch (fc submodule)

- Same Boost component list fix as above, applied to `fc`'s own
  `CMakeLists.txt`.

- **Increased the reserved buffer size in `fc::fwd<impl,N>` for
  `fc::stringstream`** from 368 to 512 bytes. `fc::fwd` is fc's
  pointer-to-implementation (pimpl) helper: it reserves a fixed-size
  byte buffer to hold an implementation object without a heap
  allocation, and asserts at compile time that the reservation is large
  enough. The actual size of `std::stringstream`'s internals grew
  between the 2014 libstdc++ this code was written against and GCC 13's
  libstdc++. This is purely an in-process memory layout detail — it is
  never serialized, hashed, or transmitted, so it has no effect on
  genesis parsing, consensus, or wire compatibility.

## boost154-coroutine-jamfile-fixed.txt

Boost 1.54's own build system (`b2`) has three conditional alternatives
for `boost_coroutine`'s stack allocator: Windows, segmented-stacks-on,
and a plain POSIX default. On this build's compiler/host combination,
`b2`'s alternative-selection logic reported "No best alternative" instead
of correctly falling through to the POSIX default. The fix removes the
two conditional alternatives that can never apply on this Linux/x86_64,
non-segmented-stack target, leaving only the POSIX allocator — which is
the exact alternative that would have been selected automatically on the
original 2014 Ubuntu 14.04 target. This is a Boost build-system quirk on
newer toolchains, unrelated to and outside of the PTS/fc codebase.

## What was deliberately NOT patched casually

`libraries/fc/src/crypto/base58.cpp` originally failed to compile against
modern OpenSSL 3.x because `BIGNUM` became an opaque type and `BN_init`
was removed. This is address-derivation code — getting an adaptation
wrong here could silently produce different addresses for the same key.
Instead of patching this code, the historically-matched **OpenSSL 1.0.1h
was rebuilt from source** so this file compiles completely unmodified.
The independent Python re-derivation in `EVIDENCE.md` §3 confirms the
result is correct.
