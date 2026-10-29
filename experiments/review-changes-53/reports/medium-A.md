What this change does: HEAD resolves each process target once for stop/restart, expands shutdown handling for forked children, and adds IPv6-only detection for LAN links.

**Must fix**

1. **Stopping one service can kill an unrelated process** ([control.rs:277](https://github.com/salasebas/ports/blob/31b234c30d9aec825f09936bdd164f86fb12abc9/src-tauri/src/ports/control.rs#L277)).

   **What this is:** The new `escaped` check finds orphaned processes using `process.exe().is_some_and(|exe| programs.contains(exe))`.

   **Problem:** Stop a Python server in an editor’s shared process group while another task forks a Python child and exits. That unrelated child matches the executable, group, session, user and “new process” checks. The condition `if (in_group || escaped || descendants.contains(&pid))` then adds it to the processes sent termination signals.

   **Fix:** Remove the executable-based inference of ownership. Restrict shutdown to verified descendants and groups owned by the selected service; add a regression case with an unrelated orphan.

   **If we skip it:** Stop, Restart or idle cleanup can terminate another task.

2. **Linux’s global IPv6 default hides valid LAN links** ([sockets.rs:44](https://github.com/salasebas/ports/blob/31b234c30d9aec825f09936bdd164f86fb12abc9/src-tauri/src/ports/sockets.rs#L44)).

   **What this is:** `std::fs::read_to_string("/proc/sys/net/ipv6/bindv6only")` determines whether every IPv6 wildcard listener is marked IPv6-only.

   **Problem:** This setting is a default that individual sockets can override. With the default set to `1`, a server explicitly setting `IPV6_V6ONLY=0` still gets marked IPv6-only. The sampler passes that incorrect flag to `lan_url`, which returns `None` despite the server being reachable over IPv4.

   **Fix:** Determine IPv6-only status from each socket’s actual setting. Cover a socket that overrides the host default.

   **If we skip it:** Reachable servers lose their LAN URL on affected Linux hosts.

`git diff --check` passed.

Verdict: fix 1 and 2 first.

Not checked: Tests, builds and runtime reproduction; execution was prohibited by the read-only benchmark constraints.
