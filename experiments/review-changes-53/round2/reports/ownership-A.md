What this change does: Records follows and followers lost through domain blocks or account suspensions. It adds notifications, a history page, and CSV downloads.

**Must fix**

1. **Downloads expose other users’ event metadata** — [severed_relationships_controller.rb:31](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/controllers/severed_relationships_controller.rb#L31)
   - **What this is:** Both CSV endpoints load an event by ID.
   - **Problem:** `@event = AccountRelationshipSeveranceEvent.find(params[:id])` accepts another user’s event. Although CSV rows are filtered, the download filename exposes that event’s target name and date.
   - **Fix:** Scope the lookup with `where(account: current_account).find(params[:id])`.
   - **If we skip it:** Signed-in users can enumerate private event metadata.

2. **Unique indexes prevent normal event history** — [migration:6](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/db/migrate/20240320140159_create_account_relationship_severance_events.rb#L6)
   - **What this is:** These rows connect affected accounts to severance events.
   - **Problem:** Both foreign keys have individually unique indexes. For example, `t.belongs_to :relationship_severance_event, foreign_key: { on_delete: :cascade }, null: false, index: { unique: true }` prevents a second recipient for one event; the account index prevents that account’s second event.
   - **Fix:** Make uniqueness apply to the account/event pair instead.
   - **If we skip it:** Notification creation raises `ActiveRecord::RecordNotUnique` for ordinary domain blocks and subsequent events.

3. **Notifications load the wrong event model** — [notification.rb:92](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/models/notification.rb#L92)
   - **What this is:** The serializer obtains notification details through this association.
   - **Problem:** `belongs_to :relationship_severance_event, inverse_of: false` reads `RelationshipSeveranceEvent` using `activity_id`, but workers store an `AccountRelationshipSeveranceEvent` ID there. Those tables have independent IDs, so a notification can serialize an unrelated event or no event.
   - **Fix:** Point the association at `AccountRelationshipSeveranceEvent` explicitly.
   - **If we skip it:** Notifications show the wrong target or disappear.

4. **The populated history page raises an error** — [index.html.haml:20](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/views/severed_relationships/index.html.haml#L20)
   - **What this is:** Each history row checks whether its data was purged.
   - **Problem:** `- if event.purged?` calls a missing method. `AccountRelationshipSeveranceEvent` delegates `purged`, but neither delegates `purged?` nor has a column generating it.
   - **Fix:** Delegate `purged?` too. Extend the request test to create an account event; its current fixture leaves the event list empty.
   - **If we skip it:** Users with recorded events receive HTTP 500 when opening the page.

5. **Notifications always report zero relationships** — [account_relationship_severance_event_serializer.rb:4](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/serializers/rest/account_relationship_severance_event_serializer.rb#L4)
   - **What this is:** Notification cards display the saved relationship count.
   - **Problem:** `attributes :id, :type, :purged, :target_name, :created_at` omits `relationships_count`. The component consequently uses `event.get('relationships_count', 0)`.
   - **Fix:** Include `relationships_count` in the serializer.
   - **If we skip it:** Even events containing lost relationships display “0 relationships.”

Verdict: fix 1–5 first.

Not checked: Tests, migrations, builds, and runtime behavior were prohibited by the read-only constraints. Static tracing completed; `git diff --check` passed with no output.
