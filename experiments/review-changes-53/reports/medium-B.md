What this change does: It reuses one process lookup for stop and restart, expands shutdown tracking in shared process groups, and adds IPv6-only detection for LAN links.

**Must fix**

1. **Stopping one service can kill an unrelated task** ([control.rs:277](https://github.com/salasebas/ports/blob/31b234c30d9aec825f09936bdd164f86fb12abc9/src-tauri/src/ports/control.rs#L277)).
   - **What this is:** The new shutdown sweep identifies orphaned processes using `process.exe().is_some_and(|exe| programs.contains(exe))`.
   - **Problem:** While stopping a Python server, an unrelated Python task can fork a worker and exit in the same shared group. That worker meets every `escaped` condition, and `if (in_group || escaped || descendants.contains(&pid))` admits it without proving ancestry.
   - **Fix:** Remove executable matching as independent ownership evidence. Signal only verified descendants or members of a verified service group.
   - **If we skip it:** Stop and restart can terminate unrelated work.

2. **Linux socket defaults hide working LAN links** ([sockets.rs:44](https://github.com/salasebas/ports/blob/31b234c30d9aec825f09936bdd164f86fb12abc9/src-tauri/src/ports/sockets.rs#L44)).
   - **What this is:** The new Linux path marks wildcard IPv6 sockets as IPv6-only when the system default passes `.is_ok_and(|value| value.trim() == "1")`.
   - **Problem:** With `bindv6only=1`, a server can explicitly set `IPV6_V6ONLY=0`. Its IPv4 LAN link works, but the new classification passes `true` to URL generation, where `bound.is_ipv6() && !v6only` rejects it.
   - **Fix:** Remove the default-based classification; determine IPv6-only status from the socket’s actual setting.
   - **If we skip it:** Valid IPv4 LAN links disappear for dual-stack listeners that override the default.

Verdict: fix 1 and 2 first.

Not checked: tests, builds, runtime reproductions, and external platform documentation under the read-only restrictions. Static caller tracing completed; `git diff --check` passed.
