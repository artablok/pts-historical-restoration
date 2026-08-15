# pts-historical-restoration

**We recovered a 12-year-old dead blockchain from raw git history — traced
its genesis back to the exact final block of the original PoW chain,
rebuilt the historical toolchain from source, and got it producing
DPoS blocks again.** Full forensic writeup and reproducible evidence below.

Community-led historical restoration of **BitShares PTS / ProtoShares**
infrastructure (2013–2014).

---

## What this is

This is not a new token wearing an old name. This is an archival
restoration project: we traced the historical PTS genesis file back to
its exact source commit and the raw PoW-chain snapshot it was generated
from, rebuilt the 2014-era build toolchain (Boost 1.54.0, OpenSSL 1.0.1h)
from source so the original code compiles unmodified where it matters
(cryptography, address derivation, consensus), and independently verified
the result cryptographically — twice, in two separately-built
environments.

## What this is NOT

- Not a claim to be the original 2013–2014 development team.
- Not a claim of ownership over historical balances — those belong to
  whoever holds the corresponding private keys, full stop.
- Not (yet) a live public network. Everything documented here runs on
  isolated, clearly-labeled test infrastructure.
- Not a guarantee of any economic value, exchange listing, or continuity
  recognition from any third party, including CoinMarketCap.

## Documents in this repository

| File | What it shows |
|---|---|
| [`EVIDENCE.md`](./EVIDENCE.md) | Full provenance chain: PoW chain block #81688 → raw balance snapshot → `make-genesis.sh` → the historical `genesis.json` → tags `v2.0`/`v2.0.1`. Every claim backed by a SHA-256 checksum you can verify yourself. |
| [`TESTNET-RESULTS.md`](./TESTNET-RESULTS.md) | Two independently-built environments running the recovered code as a live, multi-node DPoS network: block production, real P2P sync, a signed transaction, a peer-failure/recovery test, and an unattended 11h45m+ stability run at 100% delegate participation. |
| [`evidence/`](./evidence) | The raw artifacts themselves — genesis.json, the original balance snapshot, the historical genesis-generation script, delegate name list, and checksums for all of it. |
| [`build-patches/`](./build-patches) | Every change needed to compile the 2014 codebase on a modern host, each one explained and scoped — none of them touch consensus, key derivation, or serialization logic. |
| [`verify_address.py`](./verify_address.py) | A from-scratch, independent Python re-implementation of the PTS address algorithm, used to confirm the compiled code produces historically-correct addresses from a given key. |

## Status

Actively under development. Current focus: long-running stability testing
and public documentation. Historical delegate participation and network
parameters are being researched before any further steps are taken.

## Contributing

If you held a historical PTS delegate key, or you're interested in
running a node for the restored test network, open an issue — this is
meant to be community-led, not run by one person deciding things
unilaterally.
