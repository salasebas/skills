What this change does: Adds API endpoints to feature and unfeature hashtags, and adds `featuring` to authenticated tag responses. It also updates the shared creation and removal services.

**Must fix**

1. **Deleting `by_name` breaks incoming hashtag removals** ([featured_tag.rb](https://github.com/mastodon/mastodon/blob/ba536ea867afa7f281648b0dd8d63e09d3d6cf54/app/models/featured_tag.rb#L31)).
   - **What this is:** Remote servers send `Remove` activities when users unfeature hashtags.
   - **Problem:** This change deletes the scope, but [remove.rb:34](https://github.com/mastodon/mastodon/blob/ba536ea867afa7f281648b0dd8d63e09d3d6cf54/app/lib/activitypub/activity/remove.rb#L34) still calls `FeaturedTag.by_name(name).find_by(account: @account)`. A valid hashtag removal raises `NoMethodError`.
   - **Fix:** Restore the scope or update its remaining caller.
   - **If we skip it:** Remote featured hashtags remain visible after removal, and processing jobs fail.

2. **Duplicate creation fails across the two API endpoints** ([create_featured_tag_service.rb:15](https://github.com/mastodon/mastodon/blob/ba536ea867afa7f281648b0dd8d63e09d3d6cf54/app/services/create_featured_tag_service.rb#L15)).
   - **What this is:** The updated request spec expects creating an already featured tag to succeed.
   - **Problem:** `/tags/foo/feature` creates the relationship with `name: nil`. A later `/featured_tags` request with `name=foo` uses `find_or_initialize_by(name: name_or_tag)`, misses that relationship, and fails the `tag_id` uniqueness validation with HTTP 422.
   - **Fix:** Resolve string input to the canonical tag and find the existing relationship by tag, preserving the submitted display name for new records.
   - **If we skip it:** The same creation request succeeds or fails depending on which endpoint originally featured the tag.

Verdict: fix 1 and 2 first.

Not checked: Tests, builds, and runtime reproduction were prohibited by the read-only restriction. `git diff --check` passed.
