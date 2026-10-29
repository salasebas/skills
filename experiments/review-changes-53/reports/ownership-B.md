What this change does: It records follows lost through domain blocks and account suspensions. It adds notifications and a page for downloading those relationships.

**Must fix**

1. **Download URLs expose other users’ block information** — [severed_relationships_controller.rb:31](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/controllers/severed_relationships_controller.rb#L31)
   - **What this is:** The controller selects an event with `@event = AccountRelationshipSeveranceEvent.find(params[:id])`.
   - **Problem:** Any signed-in user can request another user’s event ID. Although CSV rows are filtered, the filename exposes that event’s target domain and date.
   - **Fix:** Use `AccountRelationshipSeveranceEvent.where(account: current_account).find(params[:id])`.
   - **If we skip it:** Enumerating download URLs reveals private domain-block history.

2. **Unique indexes reject normal event history** — [migration:6](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/db/migrate/20240320140159_create_account_relationship_severance_events.rb#L6)
   - **What this is:** Both foreign keys receive separate unique indexes: `t.belongs_to :account, foreign_key: { on_delete: :cascade }, null: false, index: { unique: true }`, with the same setting on the event reference.
   - **Problem:** A domain event’s second recipient raises `ActiveRecord::RecordNotUnique`. An account’s second event also fails.
   - **Fix:** Use ordinary foreign-key indexes and one unique index on the account/event pair.
   - **If we skip it:** Ordinary suspensions and repeated domain blocks leave notification history incomplete and jobs failing.

3. **Notifications look up the wrong event table** — [notification.rb:92](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/models/notification.rb#L92)
   - **What this is:** `belongs_to :relationship_severance_event, inverse_of: false` uses `activity_id` to load a `RelationshipSeveranceEvent`.
   - **Problem:** The worker stores an `AccountRelationshipSeveranceEvent` ID there. Once the tables’ ID sequences differ, serialization returns an unrelated event or no event.
   - **Fix:** Set this association’s class to `AccountRelationshipSeveranceEvent`.
   - **If we skip it:** Notifications disappear or display the wrong target, potentially exposing another user’s private block.

4. **The history page crashes whenever it has an event** — [index.html.haml:20](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/views/severed_relationships/index.html.haml#L20)
   - **What this is:** Each row calls `- if event.purged?`.
   - **Problem:** `AccountRelationshipSeveranceEvent` delegates `:purged`, but not `:purged?`, and has no column that generates that predicate. A populated page raises a missing-method error; the request test creates no account-event rows.
   - **Fix:** Call `event.purged` or explicitly delegate `purged?`.
   - **If we skip it:** Users with recorded events cannot open the download page.

**Should fix**

5. **Notifications always report zero lost relationships** — [account_relationship_severance_event_serializer.rb:4](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/serializers/rest/account_relationship_severance_event_serializer.rb#L4)
   - **What this is:** The serializer declares `attributes :id, :type, :purged, :target_name, :created_at`.
   - **Problem:** It omits the stored `relationships_count`. The component reads `event.get('relationships_count', 0)`, so positive counts display as zero.
   - **Fix:** Include `:relationships_count`, alongside correcting finding 3.
   - **If we skip it:** Notifications misstate how many relationships were lost.

Verdict: fix 1–4 first.

Not checked: Tests, migrations, build, and running UI; execution was prohibited by the read-only review constraints.
