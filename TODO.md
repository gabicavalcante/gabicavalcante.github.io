# TODO

---

## Security hardening

### Add a Hugo `[security]` block — reduce what a theme update can do
The deferred item. Genuinely marginal, so read the reasoning before deciding.

The theme is a Hugo Module: third-party code that executes templates on every
build. Two capability classes matter, and they are **not** equally worth closing:

- **`security.exec.allow` — the valuable half.** Hugo's default lets it spawn
  `go`, `git`, `node`, `postcss`, `tailwindcss`, `sass`. This site needs none of
  the asset-pipeline ones (the theme ships plain CSS). `node` execution is *code
  execution* — strictly worse than data egress. Narrowing to roughly
  `["^go$", "^git$"]` removes a whole capability class.
- **`security.http.urls` — the marginal half.** Closes `resources.GetRemote` as
  an egress channel. Lower value because the default already denies IP-literal
  hosts, `localhost`, and `user@host` URLs, and because
  `security.funcs.getenv` allowlists only `^HUGO_` and `^CI$` — a hostile theme
  **cannot read `GITHUB_TOKEN`**. There is little worth exfiltrating.

Why this is low priority: `go.sum` pins the theme by content hash, so it cannot
change under you — a force-pushed commit produces a *build failure*, not a
silent compromise. This block only matters at the moment you deliberately merge
a theme bump.

**Plan when you want it done:**
1. Read Hugo's security-config docs for the exact deny syntax — the "block
   everything" form is special-cased and worth not guessing.
2. Work in a throwaway copy of the repo, not this one.
3. Establish whether module resolution needs only `go` or also `git`. **Clear
   the Go module cache first** — a warm cache masks the failure.
4. Prove the policy *blocks*, don't just check the build passes: this site never
   calls `GetRemote`, so a green build proves nothing. Add a temporary template
   that calls it, confirm the build fails with a security error, remove it.
5. Confirm with `hugo config --format json`, then apply and push.

Main risk: an over-tight `exec.allow` breaks CI at module resolution. Step 3 is
what de-risks it.

**Defensible alternative:** skip it entirely and rely on the habit already in
CLAUDE.md — read the theme diff before merging a `gomod` bump. Same window,
no moving parts.

### Watch for fallout from the action major upgrades
**Done 2026-07-29** — Dependabot opened PRs #1–#5 immediately and all five major
upgrades were merged the same day:

| action | was | now |
|---|---|---|
| `actions/checkout` | v4.4.0 | v7.0.1 |
| `actions/setup-go` | v5.6.0 | v7.0.0 |
| `actions/configure-pages` | v5.0.0 | v6.0.0 |
| `actions/upload-pages-artifact` | v3.0.1 | v5.0.0 |
| `actions/deploy-pages` | v4.0.5 | v5.0.0 |

Two good outcomes worth recording: Dependabot **preserved SHA pinning** (all
five are still 40-char SHAs with version comments, not tags), and all four
hardening measures survived the bumps untouched — `persist-credentials: false`,
the hardcoded `HUGO_DEB_SHA256`, the checksum step, and the per-job permission
split.

The upgraded workflow **has since built and deployed successfully** — a fresh
deployment landed at 21:55:42 UTC on 2026-07-29 and the full URL set, the
alias redirect, both images and the homepage overrides all verified against it.
So the five bumps are proven working, not just merged.

They were still five major-version jumps merged together, so if the build starts
misbehaving later, this is the first place to look — `upload-pages-artifact`
v3→v5 and `deploy-pages` v4→v5 are the likeliest to have changed behaviour.
`git revert` of the relevant merge commit is the fast way back.

---

## Site hygiene

### Empty `/categories/` and `/tags/` pages
Both build and sit in `sitemap.xml`, and both list nothing — no post declares
any term. Either start tagging posts, or suppress the taxonomies in `hugo.toml`
so you stop publishing two empty pages.

---

## Housekeeping

- **Delete the merged branch**: `rebuild-hugo-source` still exists locally and
  on the remote. Fully merged into `main`; safe to remove.
- **Keep the `pre-hugo-rebuild` tag indefinitely.** It is the only surviving
  copy of the original build output and the thing that makes the migration
  reversible. Do not prune it.
- **`HUGO_DEB_SHA256` must move with `HUGO_VERSION`** in
  `.github/workflows/hugo.yml`. The build fails loudly by design if you forget.
- The one-off conversion scripts (`convert.py`, `assemble.py`, `fidelity.py`)
  lived in a session scratchpad and are gone. Only relevant if you ever want to
  re-audit the migration against the tag; otherwise no loss.

---

## Accepted differences from the pre-2026 site

Not tasks. Recorded so nobody later mistakes them for bugs.

- The `// Github` link is gone from post headers; the current theme reads only
  `linkedin` and `twitter`. Restoring it needs a `layouts/posts/single.html`
  override, declined as not worth the maintenance.
