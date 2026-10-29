What this change does: Adds API actions to feature and unfeature hashtags, plus a `featuring` field in tag responses. It also changes featured-tag creation and validation.

**Must fix**

1. **Deleted scope breaks incoming hashtag removals** ([featured_tag.rb:31](https://github.com/mastodon/mastodon/blob/ba536ea867afa7f281648b0dd8d63e09d3d6cf54/app/models/featured_tag.rb#L31))
   - **What this is:** The change removes the `FeaturedTag.by_name` scope.
   - **Problem:** The federation handler still calls `FeaturedTag.by_name(name).find_by(account: @account)` at [remove.rb:34](https://github.com/mastodon/mastodon/blob/ba536ea867afa7f281648b0dd8d63e09d3d6cf54/app/lib/activitypub/activity/remove.rb#L34). An incoming hashtag removal now raises `NoMethodError`.
   - **Fix:** Restore the scope or update its remaining caller to use the equivalent normalized lookup.
   - **If we skip it:** Remote accounts’ removed featured hashtags remain visible locally.

Verdict: fix 1 first.

Not checked: Tests and runtime behavior, including association validation for previously nonexistent tags; execution is prohibited by the read-only constraints.
