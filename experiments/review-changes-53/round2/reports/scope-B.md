What this change does: Adds API endpoints to feature and unfeature hashtags, and exposes a `featuring` flag in tag responses. It also updates the featured-tag services and validation.

**Must fix**

1. **Remote featured-tag removal breaks** ([featured_tag.rb:31](https://github.com/mastodon/mastodon/blob/ba536ea867afa7f281648b0dd8d63e09d3d6cf54/app/models/featured_tag.rb#L31))
   - **What this is:** The change deletes the `by_name` model scope.
   - **Problem:** The incoming ActivityPub removal handler still calls `FeaturedTag.by_name(name).find_by(account: @account)` at [remove.rb:34](https://github.com/mastodon/mastodon/blob/ba536ea867afa7f281648b0dd8d63e09d3d6cf54/app/lib/activitypub/activity/remove.rb#L34). A hashtag removal with a nonblank name now raises `NoMethodError`.
   - **Fix:** Retain the scope, or update this caller to look up the normalized tag.
   - **If we skip it:** Remote accounts’ featured tags remain displayed after removal.

Verdict: fix 1 first.

Not checked: Tests, build, and new-tag callback timing; runtime execution is prohibited in this environment.
