What this change does: Resolves services once for stop/restart operations and extends shutdown tracking to orphaned children in shared process groups. It also adds IPv6-only detection when generating LAN links.

**Must fix**

1. **Stopping a server can kill unrelated processes** ([control.rs:277](https://github.com/salasebas/ports/blob/31b234c30d9aec825f09936bdd164f86fb12abc9/src-tauri/src/ports/control.rs#L277)).
   - **What this is:** The new shutdown search identifies orphaned processes partly through `process.exe().is_some_and(|exe| programs.contains(exe))`.
   - **Problem:** While a Python server is shutting down, another editor task can launch an unrelated Python worker through a short-lived parent. If it inherits the shared group and session, then becomes orphaned, it satisfies every `escaped` condition. Line 287 admits it independently of verified ancestry, and line 310 signals it.
   - **Fix:** Remove the executable-based orphan inference from shared groups; signal only processes with established service membership.
   - **If we skip it:** Stop, Restart, or idle cleanup can terminate unrelated work.

2. **Linux’s current default is mistaken for each socket’s setting** ([sockets.rs:44](https://github.com/salasebas/ports/blob/31b234c30d9aec825f09936bdd164f86fb12abc9/src-tauri/src/ports/sockets.rs#L44)).
   - **What this is:** Reading `/proc/sys/net/ipv6/bindv6only` and testing `value.trim() == "1"` marks every IPv6 wildcard listener as IPv6-only.
   - **Problem:** A server can explicitly set `IPV6_V6ONLY=0` despite that default. Its working IPv4 LAN link now disappears because the sampler passes this inferred flag into `lan_url`, which rejects IPv4 when `v6only` is true. Changing the default after a socket opens produces the same error.
   - **Fix:** Read the socket’s actual setting through Linux socket diagnostics instead of treating the system default as socket state.
   - **If we skip it:** Reachable dual-stack servers lose their LAN sharing link.

Verdict: fix 1 and 2 first.

Not checked: Tests, builds, lint, and live process/socket behavior; execution is prohibited in this read-only review. `git diff --check` passed.
