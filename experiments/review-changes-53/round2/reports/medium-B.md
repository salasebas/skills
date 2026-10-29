What this change does: It reuses one process lookup for stop/restart, expands shutdown cleanup, and adds IPv6-only detection for LAN links.

**Must fix**

1. **Shutdown can kill unrelated processes** ([control.rs:277](https://github.com/salasebas/ports/blob/31b234c30d9aec825f09936bdd164f86fb12abc9/src-tauri/src/ports/control.rs#L277)).
   - **What this is:** The shared-group sweep identifies orphaned processes partly through `process.exe().is_some_and(|exe| programs.contains(exe))`.
   - **Problem:** While stopping a Python server, an unrelated sibling can fork a Python helper and exit. That helper passes every filter, enters `targets`, and receives a shutdown signal despite having no service ancestry.
   - **Fix:** Remove the executable-based sweep; require established service ancestry before adding shared-group processes.
   - **If we skip it:** Stopping one server can terminate unrelated work.

2. **Linux’s IPv6 default hides working LAN links** ([sockets.rs:44](https://github.com/salasebas/ports/blob/31b234c30d9aec825f09936bdd164f86fb12abc9/src-tauri/src/ports/sockets.rs#L44)).
   - **What this is:** Reading `"/proc/sys/net/ipv6/bindv6only"` marks all IPv6 wildcard listeners as IPv6-only when `value.trim() == "1"`.
   - **Problem:** An application can override that default with `IPV6_V6ONLY=0`. Its socket accepts IPv4, but the new flag makes `lan_url` reject its working IPv4 address.
   - **Fix:** Determine the live socket’s setting; represent unavailable information explicitly.
   - **If we skip it:** Reachable servers lose their LAN links.

Verdict: fix 1 and 2 first.

Not checked: Tests, builds, and runtime reproductions were prohibited. Static review completed; `git diff --check` passed with no output.
