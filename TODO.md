# TODO

Loose ends from the July 2026 Hugo source reconstruction. Nothing here is
broken — the site builds, deploys and is verified against the `pre-hugo-rebuild`
tag. These are decisions deferred or work deliberately left out of scope.

Roughly ordered by value, not urgency.

---

## Content — your call, not mechanical

### `/about/` and `/cv/` are six years stale
The highest-value item on this list, and the only one a visitor notices.

Both pages still describe 2020: "I work at Cloudia", "Now my challenge is to
optimizate the data processing", and under Education, "2016 - in progress".
`/cv/` has no position after 03/2019–present at Cloudia, and states "planning on
enrolling as an M.Sc. student".

The migration fixed typos only — rewriting your bio is a content decision.
Files: `content/about/index.md`, `content/cv.md`.

### Decide the fate of the 4 draft posts
All four are `draft: true` and currently 404. They were reachable-but-unlisted
before the rebuild.

| post | what it is | suggestion |
|---|---|---|
| `my-first-post` | yours, 2016, OpenCv + Intel Galileo | publish or delete — it's real writing |
| `notes-about-multi-objective-algorithms` | yours, unfinished — stops mid-outline at `### wfg tookit` | finish or delete |
| `introduction`, `what-is-hugo` | the **theme's demo posts**, copied in during 2020 setup | delete; upstream boilerplate, not yours |

Typos in `notes-about-multi-objective-algorithms` were left verbatim on purpose
("undestand", "Wailking Fish Group", "tread-off", "tookit") — no point editing
prose that's getting rewritten.

### Small content defects found but not changed
Judged out of scope for a typo pass:

- `content/posts/matplotlib-seaborn-relplot/index.md` — "You can run the code
  using colab, find the complete tutorial here." Neither "colab" nor "here" was
  ever a link in the original HTML. Dead references; add the URLs or reword.
- `content/cv.md:146,148` — the same talk listed twice, same conference
  ("Campus Party Recife 2016"), conflicting dates `Aug/19` and `Aug/16`. One is
  probably wrong.
- `content/cv.md` — "Out/18" uses the Portuguese month abbreviation in an
  otherwise English CV.
- `content/posts/lets-talk-about-communication/index.md` — "eles podem nunca
  fazer que não estão entendendo" reads garbled ("falar"?). Left alone rather
  than guess at your meaning.

### Is `me2.jpg` meant to be visible?
It's only the `og:image` for social cards, never displayed on the page. That's
faithful to the old site, which had no `<img>` either — but if you meant to have
a photo on `/about/`, it never appeared.

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

These were five major-version jumps merged together, so if the build starts
misbehaving, this is the first place to look — `upload-pages-artifact` v3→v5 and
`deploy-pages` v4→v5 are the likeliest to have changed behaviour. `git revert`
of the relevant merge is the fast way back.

### Confirm the CI runs actually went green
Never verified per-run status — `gh` isn't authenticated in the environment
where this work was done, so only the live site's `last-modified` header was
available as evidence. That confirmed *a* deployment landed, but not that every
individual run succeeded, across ten commits (five hardening + five Dependabot
merges). One glance at the Actions tab closes this out.

---

## Site hygiene

### Empty `/categories/` and `/tags/` pages
Both build and sit in `sitemap.xml`, and both list nothing — no post declares
any term. Either start tagging posts, or suppress the taxonomies in `hugo.toml`
so you stop publishing two empty pages.

### Hugo deprecation warning on every build
```
WARN  deprecated: .Site.LanguageCode was deprecated in Hugo v0.158.0
```
Traced: **not** our config (which uses `locale`) and **not** the theme (no
`rss.xml`; its `sitemap.xml` doesn't reference it). It comes from Hugo's own
embedded `_internal/rss.xml`. Nothing to fix — it resolves when Hugo updates
that template. Suppressible with a custom `layouts/rss.xml` if the noise ever
bothers you.

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

- Dates render `Aug 15, 2020` instead of `Aug. 15, 2020` — newer Hugo/theme
  `:date_medium` formatting.
- The `// Github` link is gone from post headers; the current theme reads only
  `linkedin` and `twitter`. Restoring it needs a `layouts/posts/single.html`
  override, declined as not worth the maintenance.
- The theme's vendored CSS moved on (terminal 0.7.4, animate 4.1.1 vs the old
  0.7.1 / 3.7.2), so small visual drift is expected.
