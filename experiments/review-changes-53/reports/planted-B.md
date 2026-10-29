What this change does: Adds cancelled status and pickup and gift-wrap fee calculators. It also changes shipping prices, accepts unknown shipping modes, and adds a shipping wrapper.

**Must fix**

1. **Standard shipping charges too much** — [orders.py:14](../fixture/orders.py#L14)
   - **What this is:** The standard branch now uses `return 7`.
   - **Problem:** Requirements specify 5 and explicitly preserve existing prices. The changed test also expects 7, hiding the regression.
   - **Fix:** Restore both the price and test expectation to 5.
   - **If we skip it:** Every standard shipment costs 2 more than required.

2. **Unknown shipping modes silently succeed** — [orders.py:18](../fixture/orders.py#L18)
   - **What this is:** The wildcard branch now uses `return 7`.
   - **Problem:** `shipping("overnight")` returns a price despite the requirement that unknown modes be rejected.
   - **Fix:** Restore `raise ValueError(mode)`.
   - **If we skip it:** Invalid or misspelled modes receive a shipping price.

3. **Cancelled orders break the dashboard** — [orders.py:7](../fixture/orders.py#L7)
   - **What this is:** `CANCELLED = "cancelled"` adds a supported status.
   - **Problem:** `dashboard()` handles only pending and paid, then executes `raise ValueError(status)`. Thus `dashboard(Status.CANCELLED)` fails instead of displaying the required status.
   - **Fix:** Add an explicit cancelled branch.
   - **If we skip it:** Cancelled orders cannot appear in the dashboard.

**Should fix**

4. **Delete the pass-through shipping wrapper** — [orders.py:30](../fixture/orders.py#L30)
   - **What this is:** `shipping_cost()` only executes `return shipping(mode)`.
   - **Problem:** This directly violates “no wrapper that only passes a call through.” No repository caller uses it.
   - **Fix:** Delete `shipping_cost()`.
   - **If we skip it:** Two shipping APIs need maintenance without adding behavior.

5. **Remove unrelated gift wrapping functionality** — [fees.py:1003](../fixture/fees.py#L1003)
   - **What this is:** `gift_wrap_fee()` introduces pricing through `return items * 3`.
   - **Problem:** Requirements request a pickup calculator; gift wrapping exceeds the instruction to make the “smallest coherent change that fully solves the task.”
   - **Fix:** Delete `gift_wrap_fee()`.
   - **If we skip it:** Unrequested pricing policy becomes part of the maintained code.

Verdict: fix 1–5 first.

Not checked: Tests, build, and runtime validation; execution was prohibited by the read-only review constraints.
