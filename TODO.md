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

---

## Site hygiene

### ~~Empty `/categories/` and `/tags/` pages~~ — done
All five published posts are tagged, `[taxonomies]` declares only `tag`, so
`/categories/` no longer builds, and `layouts/_default/terms.html` renders
`/tags/` as a real term index. Left here only so nobody acts on the old advice:
suppressing the taxonomies now would undo working tag pages.

### Nine tag pages for five posts
**Seven of the nine list exactly one post**: `celery`, `ci-cd`, `community`,
`data-visualization`, `latex`, `reliability`, `speaking`. Only `python` (4) and
`django` (3) have more. Not urgent and not a bug, but thin term pages are index
bloat, and it is worth deciding whether every tag earns its own page.

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

- ~~The `// Github` link is gone from post headers.~~ No longer true: the
  `layouts/posts/single.html` override exists — tags needed the same file, so
  the Github link came along with them.

---

## SEO — remaining

Eight groups were worked through in Aug 2026; seven are in `main`. What is left:

### Mobile / Core Web Vitals
Google indexes mobile-first, so this is ranking, not polish.
- `console.css` sets `--global-font-size: 14px` below 850px, against 16px on
  desktop. Shrinking the text on the smaller screen is backwards.
- The theme's `render-image.html` emits only `src`/`alt`/`class`, and the CSS
  sets `img{width:100%}`. With no intrinsic dimensions the browser cannot
  reserve height, so every image shifts the layout when it lands — the CLS half
  of Core Web Vitals.
- No `loading="lazy"` anywhere.
- `plot1.png` is 1969x1190 and 597KB for a ~390px screen. It is the LCP element
  of that post on a phone.
- `pre{word-break:break-all}` splits identifiers mid-token
  (`send_order_confirmation_email(orde` / `r)`). Readability, not SEO.

### `og:type="article"` on `/about/` and `/cv/`
They are not articles, and they also carry `article:published_time`. Wrong
signal on two high-value pages. Lives in `layouts/partials/opengraph.html`.

### Search Console
- After the breadcrumb fix (bf1552c) deploys, press **Validate fix** on the
  "field id is missing in itemListElement.item" report.
- Expect a new *warning* (not error) in the Articles report: `image` is missing
  on all five posts. Deliberate — see `layouts/partials/schema.html`. It goes
  away when the image work above is done.
