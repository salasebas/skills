What this change does: Adds a cancelled order status and pickup fees. It also changes shipping behavior, updates the shipping test, and adds gift wrapping and a shipping wrapper.

**Must fix**

1. **Standard shipping is overcharged** — [orders.py:14](../fixture/orders.py#L14)
   - **What this is:** Standard shipping now uses `return 7`.
   - **Problem:** [requirements.md:3](../fixture/requirements.md#L3) requires a price of 5 and explicitly preserves existing prices. The changed assertion, `self.assertEqual(shipping("standard"), 7)`, hides the regression.
   - **Fix:** Restore 5 in both the implementation and the existing test.
   - **If we skip it:** Every standard shipment costs 2 more than required.

2. **Unknown shipping modes are silently accepted** — [orders.py:18](../fixture/orders.py#L18)
   - **What this is:** The default branch now uses `return 7`.
   - **Problem:** `shipping("invalid")` returns a price, although the requirements say “Unknown modes must be rejected.”
   - **Fix:** Restore `raise ValueError(mode)` and cover an unknown mode in a test.
   - **If we skip it:** Invalid inputs receive a shipping price instead of an error.

3. **The dashboard rejects cancelled orders** — [orders.py:7](../fixture/orders.py#L7)
   - **What this is:** The enum adds `CANCELLED = "cancelled"`.
   - **Problem:** `dashboard()` handles only pending and paid statuses before `raise ValueError(status)`. Therefore, `dashboard(Status.CANCELLED)` raises instead of displaying the newly supported status.
   - **Fix:** Add a cancelled dashboard case and a regression test.
   - **If we skip it:** Cancelled orders cannot appear in the dashboard as required.

**Should fix**

4. **Remove unnecessary additions** — [orders.py:30](../fixture/orders.py#L30), [fees.py:1003](../fixture/fees.py#L1003)
   - **What this is:** `shipping_cost()` only executes `return shipping(mode)`; `gift_wrap_fee()` introduces unrelated pricing. Neither has callers in the repository.
   - **Problem:** These violate the explicit rules “no wrapper that only passes a call through” and “Prefer the simplest scoped solution.” The added `# Return the standard shipping price.` comment also falls outside the permitted comment categories.
   - **Fix:** Delete the wrapper, gift wrapping function, and redundant comment.
   - **If we skip it:** The change adds an unnecessary API, an unrequested business rule, and avoidable maintenance.

5. **Keep pickup pricing in a separate module** — [fees.py:991](../fixture/fees.py#L991)
   - **What this is:** `def pickup_fee(subtotal: int, parcels: int) -> int:` is appended to the regional fee module, which grows from 990 to 1,008 lines.
   - **Problem:** AGENTS.md requires “Split a file before a change takes it past about 1,000 lines.” Pickup pricing is a separate concept from the existing regional calculations.
   - **Fix:** Move the new pickup calculator into a focused `pickup_fees.py` module.
   - **If we skip it:** This change crosses the project’s file-size guideline without splitting the new responsibility.

Verdict: fix 1–5 first.

Not checked: Tests, type checks, and runtime behavior; execution is prohibited by the read-only review restrictions. Findings were validated by reading the diff, requirements, and relevant code.
