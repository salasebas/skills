What this change does: Adds API endpoints to feature and unfeature hashtags, plus a `featuring` response field. It also changes featured-tag validation and creation.

**Must fix**

1. **Federated hashtag removals call a deleted scope** ([featured_tag.rb](https://github.com/mastodon/mastodon/blob/ba536ea867afa7f281648b0dd8d63e09d3d6cf54/app/models/featured_tag.rb#L29))
   - **What this is:** The change removes `FeaturedTag.by_name`.
   - **Problem:** Incoming hashtag removals still execute `featured_tag = FeaturedTag.by_name(name).find_by(account: @account)` at [remove.rb:34](https://github.com/mastodon/mastodon/blob/ba536ea867afa7f281648b0dd8d63e09d3d6cf54/app/lib/activitypub/activity/remove.rb#L34), raising `NoMethodError`.
   - **Fix:** Retain the scope or update this caller to use the equivalent normalized lookup.
   - **If we skip it:** Remote users’ hashtag removals fail, leaving stale featured tags.

2. **The two creation APIs disagree about existing tags** ([create_featured_tag_service.rb:15](https://github.com/mastodon/mastodon/blob/ba536ea867afa7f281648b0dd8d63e09d3d6cf54/app/services/create_featured_tag_service.rb#L15))
   - **What this is:** The new endpoint initializes by `tag`, leaving `name` unset. The older endpoint uses `account.featured_tags.find_or_initialize_by(name: name_or_tag)`.
   - **Problem:** Feature an existing `foo` tag through `/api/v1/tags/foo/feature`, then submit `name=foo` to `/api/v1/featured_tags`. The lookup misses the existing record, and `validates :tag_id, uniqueness: { scope: :account_id }` rejects the duplicate with HTTP 422.
   - **Fix:** Resolve both input forms to the canonical tag and look up the featured record by that tag.
   - **If we skip it:** Repeating the same operation through another client fails despite the new success behavior for existing featured tags.

Verdict: fix 1 and 2 first.

Not checked: Tests, build, and runtime behavior of the new-tag callbacks; execution is prohibited. Static diff checks passed.
