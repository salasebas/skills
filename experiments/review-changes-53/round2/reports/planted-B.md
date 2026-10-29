What this change does: Adds a cancelled status and pickup and gift-wrap fee calculators. It also changes shipping prices and error handling.

**Must fix**

1. **Standard shipping charges the wrong price** ([orders.py:14](../../fixture/orders.py#L14)).
   - **What this is:** The standard shipping price.
   - **Problem:** `return 7` contradicts the required price of 5. The [test](../../fixture/test_orders.py#L8) now expects 7, masking the regression.
   - **Fix:** Restore both the price and test expectation to 5.
   - **If we skip it:** Every standard shipment costs 2 too much.

2. **Unknown shipping modes are accepted** ([orders.py:18](../../fixture/orders.py#L18)).
   - **What this is:** Handling for unsupported modes.
   - **Problem:** The fallback now uses `return 7`. For example, `shipping("overnight")` returns a price, although requirements explicitly demand rejection.
   - **Fix:** Restore `raise ValueError(mode)`.
   - **If we skip it:** Invalid or misspelled modes receive valid-looking prices.

3. **Cancelled orders fail in the dashboard** ([orders.py:7](../../fixture/orders.py#L7)).
   - **What this is:** The new `CANCELLED = "cancelled"` status.
   - **Problem:** `dashboard` handles only pending and paid, so `dashboard(Status.CANCELLED)` reaches `raise ValueError(status)`. Requirements say every supported status must appear.
   - **Fix:** Add a cancelled dashboard branch.
   - **If we skip it:** Displaying a cancelled order raises an error.

**Should fix**

4. **Keep the fee addition focused** ([fees.py:991](../../fixture/fees.py#L991)).
   - **What this is:** The new `pickup_fee` and `gift_wrap_fee` functions.
   - **Problem:** Gift wrapping is unrequested and unused. These additions also grow the regional fee module from 990 to 1,008 lines, contrary to the scoped-change and file-splitting instructions; no exception is identified.
   - **Fix:** Delete `gift_wrap_fee` and put `pickup_fee` in a focused `pickup_fees.py` module.
   - **If we skip it:** An unrelated feature adds maintenance work while the module exceeds the project’s size guideline.

5. **Delete the forwarding wrapper** ([orders.py:30](../../fixture/orders.py#L30)).
   - **What this is:** `shipping_cost` contains only `return shipping(mode)`.
   - **Problem:** It has no callers and violates the explicit instruction against wrappers that only pass calls through.
   - **Fix:** Delete `shipping_cost`.
   - **If we skip it:** Two public names represent the same operation without adding behavior.

Verdict: fix 1–5 first.

Not checked: Tests and runtime checks were prohibited by the read-only constraint. Static diff checking passed; pickup pricing rules are unspecified in the repository requirements.
