# PTS Historical Restoration — Testnet Results

**Date:** 2026-08-14
**Implementation:** PTS v2.0.1 (historical source, `92a40f2d` genesis)
**Scope:** Two independent test environments, run in parallel by two different operators

## 1. Objective

Verify that the recovered PTS v2.0.1 codebase is not merely buildable
source code, but a functioning DPoS blockchain — capable of block
production, multi-node P2P synchronization, transaction processing, and
recovery after node failure.

Two independent environments tested this, using different methods, and
cross-checked the results:

- **Environment A** (operator-run): Ubuntu 14.04 Docker container, real
  wall-clock time via NTP, multiple real P2P processes.
- **Environment B** (this session): modern host toolchain rebuilt against
  historical Boost 1.54.0 / OpenSSL 1.0.1h, deterministic simulated time
  via the codebase's own `debug_start_simulated_time` / `debug_advance_time`
  test harness.

Agreement between two independently-built, independently-operated
environments is stronger evidence than either alone.

## 2. Chain Initialization

Both environments initialized successfully from `tests/test_genesis.json`
(the project's own regression-test genesis: 101 named delegates,
`init0`–`init100`/`delegate0`–`delegate100`, using the historical WIF test
keys committed in `tests/regression_tests/_common_logs/import_delegate_keys.log`).

Observed chain parameters (both environments):
- Symbol: PTS, address prefix: PTS
- Block interval: 10 seconds
- Delegate count: 101
- `blockchain_share_supply`: 999,999,999.999907 PTS (identical in both)

This is the project's own historical test fixture, not the production
genesis — see `EVIDENCE.md` for the historical-genesis provenance chain
(block #81688, `92a40f2d`), which is a separate, already-verified artifact.

## 3. DPoS Block Production

**Environment A:** Real wall-clock production. First observed block #1 at
`2026-08-14T16:15:40` (`delegate0`). Chain reached block #263+ over the
session, each block signed by a distinct rotating delegate.

**Environment B:** Deterministic production via simulated time, advanced
in fixed 10-second steps. Produced blocks #1–#7 in sequence, each with a
unique `delegate_signature`, timestamps advancing exactly 10s apart
(`14:40:30` → `14:41:30`), matching `BTS_BLOCKCHAIN_BLOCK_INTERVAL_SEC`
exactly.

Both environments confirm: block signatures are unique per block, block
timestamps advance exactly on the configured interval, and the delegate
schedule rotates through the full 101-delegate pool.

## 4. Multi-Node P2P Test

Environment A ran two independent `pts_client` processes ("node A" as
producer, "node B" as a connect-only peer via `--connect-to 127.0.0.1:3777`).

Observed:
- Node B reported `"our last block is 23 minutes old"` → `"in sync with p2p network"` after connecting — real chain-download/sync logic, not a shared data directory.
- `network_num_connections: 1` on both sides.
- Block hashes queried independently on node B (`blockchain_get_block_hash 1/6/10/234/253/...`) returned **identical values across repeated queries at different points in time**, confirming a deterministic, non-forking chain shared correctly over P2P.

## 5. End-to-End Transaction Test

Environment A performed a live signed transfer, not just empty blocks:

- `delegate0` → `receiver` account, 1.000000 PTS, memo `test-payment`.
- Included in block #94, with `user_transaction_ids: ["f5fbaeed..."]` present in the raw block data (not just wallet-side history).
- Receiving account balance and transaction history both correctly reflect the transfer, fee `0.000000 PTS`.

This confirms the transaction-processing and balance-update path works
end-to-end over a real P2P connection between two independent processes.

## 6. Peer Failure / Recovery Test

Environment A: the producer node (node A) was stopped mid-round.

Observed on node B:
- `--- there are now 0 active connections to the p2p network`
- Node B's head block height froze (no new blocks — expected, node B holds no delegate keys) but continued responding to RPC queries normally; no crash, no corruption.
- On producer restart: `--- there are now 1 active connections to the p2p network`, followed by automatic re-sync and continued height progression — **no manual intervention required**.
- The gap period appears honestly in `blockchain_list_blocks` as consecutive `MISSED` slots for the delegates whose turn fell during the outage, with the chain correctly resuming from the last valid block afterward.

## 7. Producer Failure / Recovery Test

Same underlying event as §6, viewed from the production side: after the
producer process restarted and reconnected, `wallet_delegate_set_block_production ALL true`
resumed normal signing on the next eligible slot, `blockchain_delegate_pay_rate`
began accruing again (`0.000206 PTS`), and `blockchain_average_delegate_participation`
climbed back from a post-outage low toward steady state as slots were
filled again.

## 8. Long-Running Stability Test

Both Environment A processes (producer node and P2P-connected explorer
backend node) were left running unattended overnight, with no restarts,
no manual intervention, and no supervision process.

Observed after **11h45m** (producer) / **11h32m** (peer) continuous uptime:

- `blockchain_head_block_num`: 4,473 (up from 263 at the end of the prior
  session — chain kept advancing correctly the entire time)
- `blockchain_average_delegate_participation`: **100%** — zero missed
  slots across the entire overnight window
- `ntp_time_error`: 0.0008s — clock sync remained tight throughout
- `network_num_connections`: 1 — the P2P link between the two processes
  never dropped
- Process state: both `pts_client` processes remained in normal sleeping
  multi-threaded state (`Sl`/`Sl+`), no crash, no restart, no zombie state
- The explorer's HTTP API (`/api/block/4473`) continued serving correct,
  fully-formed block data (signature, chain-secret linkage, hash) without
  interruption

This is a materially different kind of evidence from the earlier
short-session tests: it demonstrates the software can run unattended for
an extended period without drift, leaks, missed-slot accumulation, or
silent failure — not just that it can be started and produce a handful of
blocks under direct observation.

## 9. Verified Capabilities

- Genesis parsing and chain initialization (both environments)
- Deterministic, correctly-timed DPoS block production
- Unique per-block delegate signatures, correct rotation across a 101-delegate pool
- Real multi-process P2P synchronization (not shared storage)
- Signed transaction inclusion, propagation, and balance update over P2P
- Chain-hash consistency across independent queries and across nodes
- Graceful degradation on peer/producer disconnect — no crash, no fork, no manual recovery step
- Automatic re-synchronization after reconnect, with honest MISSED-slot accounting
- Independent verification via two differently-built environments (modern-toolchain cross-compile vs. native Ubuntu 14.04 container) reaching identical chain parameters and share supply
- Unattended long-running stability: 11h45m continuous uptime, 100% delegate participation, zero missed slots, no restarts or manual intervention required

## 10. Conclusion

The recovered PTS v2.0.1 codebase operates as a functional multi-node DPoS
blockchain: producing blocks, propagating chain state over P2P, processing
signed transactions, preserving consensus history across downtime, and
recovering automatically after node/process interruption. These results
were independently reproduced in two separately-built environments, which
is stronger evidence than a single run.

These results establish a reproducible technical Proof of Restoration for
the PTS v2.0.1 codebase and the `tests/test_genesis.json` test fixture.

They do **not**, by themselves, establish continuity with the historical
public PTS network, ownership of historical private keys, current
economic value, exchange recognition, or production security of the
legacy software. Those are separate questions requiring additional
evidence and work — see `EVIDENCE.md` for what has and has not been
established about the historical (non-test) genesis specifically.
