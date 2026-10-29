What this change does: HEAD adds cancelled status and pickup and gift-wrap fee calculators. It also changes shipping prices, accepts unknown shipping modes, and adds a shipping wrapper.

**Must fix**

1. **Standard shipping is overcharged** ([orders.py:14](../../fixture/orders.py#L14)).
   - **What this is:** The standard branch now says `return 7`.
   - **Problem:** `shipping("standard")` returns 7, while requirements.md explicitly requires 5 and says to keep existing prices. The changed assertion, `self.assertEqual(shipping("standard"), 7)`, hides this regression.
   - **Fix:** Restore both the price and the test expectation to 5.
   - **If we skip it:** Every standard shipment costs 2 more than required.

2. **Unknown shipping modes are silently accepted** ([orders.py:18](../../fixture/orders.py#L18)).
   - **What this is:** The default branch now says `return 7`.
   - **Problem:** An input such as `shipping("invalid")` receives a price instead of being rejected, contradicting requirements.md and the instruction to avoid silent fallbacks.
   - **Fix:** Restore `raise ValueError(mode)` and add coverage for an unknown mode.
   - **If we skip it:** Invalid shipping selections appear valid.

3. **Cancelled orders cannot appear in the dashboard** ([orders.py:7](../../fixture/orders.py#L7)).
   - **What this is:** The enum adds `CANCELLED = "cancelled"`.
   - **Problem:** `dashboard()` handles only pending and paid, then executes `raise ValueError(status)`. Consequently, `dashboard(Status.CANCELLED)` raises instead of displaying the required status.
   - **Fix:** Add a cancelled branch and a regression test.
   - **If we skip it:** The newly supported status breaks dashboard rendering.

**Should fix**

4. **Remove the redundant shipping wrapper** ([orders.py:30](../../fixture/orders.py#L30)).
   - **What this is:** `shipping_cost()` contains only `return shipping(mode)`.
   - **Problem:** No repository caller uses it. It directly violates “no wrapper that only passes a call through.”
   - **Fix:** Delete `shipping_cost()`.
   - **If we skip it:** Shipping has two public entry points to maintain without any added behavior.

5. **Remove the unrelated gift-wrap calculator** ([fees.py:1003](../../fixture/fees.py#L1003)).
   - **What this is:** The change adds `def gift_wrap_fee(items: int) -> int:`.
   - **Problem:** The requirements request local pickup, and no repository caller uses gift wrapping. This violates the instruction to avoid unrelated work.
   - **Fix:** Delete `gift_wrap_fee()`.
   - **If we skip it:** The project acquires an unused pricing rule without a stated requirement.

6. **Split the new fee logic before crossing the file-size limit** ([fees.py:991](../../fixture/fees.py#L991)).
   - **What this is:** `def pickup_fee(subtotal: int, parcels: int) -> int:` is appended to the regional fee module.
   - **Problem:** The additions grow fees.py from 990 to 1,008 lines. AGENTS.md requires splitting before passing about 1,000 lines or naming an applicable exception; none is stated.
   - **Fix:** Put the pickup calculator in a focused module, such as `pickup.py`.
   - **If we skip it:** The change bypasses the project’s explicit file-size rule.

7. **Delete the comment that restates the code** ([orders.py:13](../../fixture/orders.py#L13)).
   - **What this is:** `# Return the standard shipping price.` describes the immediately following return.
   - **Problem:** It fits none of the comment categories permitted by AGENTS.md.
   - **Fix:** Delete the comment.
   - **If we skip it:** The change retains an explicit instruction violation and redundant prose.

Verdict: fix 1–7 first.

Not checked: Tests, typechecks, builds, and runtime behavior; execution was prohibited by the read-only review constraints. Findings were validated against the diff, requirements, and code.
