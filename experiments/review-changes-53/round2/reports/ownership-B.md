What this change does: Records follows and followers lost through suspensions or domain blocks. It adds notifications and a page for downloading those relationships as CSV files.

**Must fix**

1. **Downloads expose another user’s blocked domain** ([severed_relationships_controller.rb:31](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/controllers/severed_relationships_controller.rb#L31)).
   - **What this is:** Downloads load events with `AccountRelationshipSeveranceEvent.find(params[:id])`.
   - **Problem:** Any authenticated user can request another user’s event ID. Although CSV rows are scoped, the filename exposes that user’s blocked domain and event date.
   - **Fix:** Use `AccountRelationshipSeveranceEvent.where(account: current_account).find(params[:id])`.
   - **If we skip it:** Users’ private domain-block history remains accessible.

2. **Unique indexes reject normal event creation** ([migration:6](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/db/migrate/20240320140159_create_account_relationship_severance_events.rb#L6)).
   - **What this is:** Both foreign keys individually use `index: { unique: true }`.
   - **Problem:** A domain block affecting two local users fails when creating the second user’s event. A user’s second event also violates uniqueness.
   - **Fix:** Replace individual uniqueness with a composite unique index on `[account_id, relationship_severance_event_id]`.
   - **If we skip it:** Event creation raises `ActiveRecord::RecordNotUnique`, leaving affected users without notifications or download entries.

3. **Notifications fetch the wrong event model** ([notification.rb:92](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/models/notification.rb#L92)).
   - **What this is:** `belongs_to :relationship_severance_event, inverse_of: false` uses `activity_id` to fetch a `RelationshipSeveranceEvent`.
   - **Problem:** The worker stores an `AccountRelationshipSeveranceEvent` ID there. Those tables’ IDs can differ—for example, after a domain block creates a parent event without any affected users.
   - **Fix:** Set this association’s `class_name` to `'AccountRelationshipSeveranceEvent'`.
   - **If we skip it:** Notifications show another event’s domain and details, or disappear because their event resolves to null.

4. **The page fails when it contains an event** ([index.html.haml:20](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/views/severed_relationships/index.html.haml#L20)).
   - **What this is:** Each row calls `event.purged?`.
   - **Problem:** `AccountRelationshipSeveranceEvent` delegates `:purged`, but not `:purged?`; its table has no `purged` column to generate that predicate. The request test creates no account-specific event, so it misses this branch.
   - **Fix:** Delegate `:purged?`, or use the existing `event.purged`.
   - **If we skip it:** Users with recorded events receive an exception instead of the download page.

5. **Notifications always display zero lost relationships** ([serializer:4](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/serializers/rest/account_relationship_severance_event_serializer.rb#L4)).
   - **What this is:** The serializer declares `attributes :id, :type, :purged, :target_name, :created_at`.
   - **Problem:** It omits `relationships_count`, which the notification reads with `event.get('relationships_count', 0)`.
   - **Fix:** Add `:relationships_count` to the serialized attributes.
   - **If we skip it:** Even after fixing the association, notifications report “0 relationships” for actual losses.

**Should fix**

6. **Keep domain-block recording out of shared deletion** ([delete_account_service.rb:274](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/services/delete_account_service.rb#L274)).
   - **What this is:** Every deletion now enters recording logic gated by `return if relationship_severance_event.nil?`.
   - **Problem:** Only `BlockDomainService` supplies this option. This violates the instruction: “Keep feature checks out of shared paths.”
   - **Fix:** Move the two recording loops into `BlockDomainService#suspend_accounts!`, before deletion. Remove the option, guard, accessor, and recording call from `DeleteAccountService`.
   - **If we skip it:** Shared deletion retains feature-specific state and branching for one caller.

7. **Reuse the existing following CSV encoder** ([severed_relationships_controller.rb:35](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/controllers/severed_relationships_controller.rb#L35)).
   - **What this is:** The controller copies `Export#to_following_accounts_csv`, including `csv << [acct(follow.target_account), follow.show_reblogs, follow.notify, follow.languages&.join(', ')]`.
   - **Problem:** The following format and account-address conversion now have two owners, contrary to “reuse the project’s existing helpers.”
   - **Fix:** Let the existing export method accept the scoped relationship collection. Keep CSV encoding in `Export` and HTTP delivery in the controller.
   - **If we skip it:** Export-format changes require synchronized fixes in both implementations.

Static tracing covered the affected models, schema, services, serializers, controllers, UI, and tests. `git diff --check` passed.

Verdict: fix 1–7 first.

Not checked: Tests, migrations, build, HTTP requests, and running UI; execution was prohibited by the read-only review constraints.
