What this change does: Records relationships lost through domain blocks and account suspensions. It adds notifications, a history page, CSV downloads, and purge tracking.

**Must fix**

1. **Downloads expose other accounts’ event metadata** — [severed_relationships_controller.rb:31](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/controllers/severed_relationships_controller.rb#L31)
   - **What this is:** Looks up the event for either CSV download.
   - **Problem:** `@event = AccountRelationshipSeveranceEvent.find(params[:id])` accepts another account’s ID. Although CSV rows are scoped, the filename reveals that event’s private blocked domain and date.
   - **Fix:** Scope the lookup with `where(account: current_account).find(params[:id])`.
   - **If we skip it:** Any signed-in user can enumerate other users’ event metadata.

2. **Unique indexes prevent normal event history and multiple recipients** — [migration:6](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/db/migrate/20240320140159_create_account_relationship_severance_events.rb#L6)
   - **What this is:** Links affected accounts to severance events.
   - **Problem:** Both `t.belongs_to` declarations specify `index: { unique: true }` separately. A second event for one account, or a second recipient of one domain-block event, raises `ActiveRecord::RecordNotUnique`.
   - **Fix:** Use a composite unique index on `(account_id, relationship_severance_event_id)` instead of individual unique indexes.
   - **If we skip it:** Routine blocks and suspensions fail during notification creation, leaving affected users without history entries.

3. **Notifications look up event IDs in the wrong table** — [notification.rb:92](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/models/notification.rb#L92)
   - **What this is:** Supplies the event serialized into notifications.
   - **Problem:** `belongs_to :relationship_severance_event, inverse_of: false` interprets `activity_id` as a `RelationshipSeveranceEvent` ID. Workers pass an `AccountRelationshipSeveranceEvent` ID; these independent sequences diverge.
   - **Fix:** Point this association and its serializer at `AccountRelationshipSeveranceEvent`.
   - **If we skip it:** Notifications show unrelated event metadata, potentially another user’s private block target, or disappear when no matching row exists.

4. **The history page fails whenever it contains an event** — [index.html.haml:20](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/views/severed_relationships/index.html.haml#L20)
   - **What this is:** Chooses between the purge notice and download links.
   - **Problem:** `- if event.purged?` calls a missing method. The account-event model delegates `:purged` only, and its table has no `purged` column to generate the predicate.
   - **Fix:** Delegate `:purged?` too, or call `event.purged`.
   - **If we skip it:** Every populated history page raises `NoMethodError`. The request test misses this because it creates no account-event entry.

**Should fix**

5. **Notifications always display zero lost relationships** — [account_relationship_severance_event_serializer.rb:4](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/serializers/rest/account_relationship_severance_event_serializer.rb#L4)
   - **What this is:** Defines the event payload consumed by the notification card.
   - **Problem:** `attributes :id, :type, :purged, :target_name, :created_at` omits `relationships_count`. The card reads `event.get('relationships_count', 0)`, so every unpurged event displays zero.
   - **Fix:** Include the stored `relationships_count` in the serializer.
   - **If we skip it:** Notifications misstate how many relationships were lost.

Static review completed; `git diff --check` passed with no output.

Verdict: fix 1–4 first.

Not checked: Tests, build, migrations, and running UI; execution was prohibited by the read-only review constraints.
