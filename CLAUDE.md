# CLAUDE.md

## What this repo is

The Hugo **source** for a personal blog published at
<https://gabicavalcante.dev> via GitHub Pages. The apex is the canonical
address; the old `gabicavalcante.github.io` still resolves, because GitHub
redirects it to the custom domain. The repo name — and so the `go.mod` module
path — keeps the `github.io` spelling and should not be changed to match.

`public/` is **built by CI and never committed.** Pages is configured with
Source = "GitHub Actions", not "deploy from a branch". Committing build output
back into this repo is what previously left four posts as live-but-unlisted URLs:
Hugo does not prune deleted pages from an existing `public/`.

## Setup

Both tools are already installed and on the interactive `PATH`:

- `hugo` 0.164.0 → `~/.local/bin/hugo` (standard edition; the theme ships plain
  CSS, so extended is not needed)
- `go` 1.26.5 → `/usr/local/go/bin/go` — required because the theme is a Hugo
  Module and Hugo shells out to the Go toolchain

```bash
hugo server -D          # local preview; -D is required to see the 4 drafts
hugo --gc --minify      # production build, same flags CI uses
hugo mod get -u github.com/mrmierzejewski/hugo-theme-console   # update theme
```

## Layout

```
hugo.toml                 baseURL, nav (params.navlinks), monokai highlighting
go.mod / go.sum           theme module, pinned by commit
layouts/index.html        homepage override — see below, do not delete
layouts/posts/single.html post override: Github link + tag links
layouts/_default/terms.html  /tags/ index — see Taxonomy below
layouts/partials/twitter_cards.html  empty on purpose; the theme's baseof calls
                          this partial unconditionally and it emitted twitter:
                          meta on every page. og:* still covers link previews.
static/CNAME              the custom domain; see Domain below
.github/workflows/hugo.yml
content/
  about/index.md              page bundle; no image (me2.jpg was removed)
  cv.md                      
  posts/_index.md             cascades linkedin/github to every post
  posts/<slug>/index.md       one bundle per post
```

## Conventions

- **TOML front matter** (`+++`), matching the theme's own examples.
- **Every post is a page bundle** (`posts/<slug>/index.md`), so images sit beside
  the post that uses them. The theme's image render hook resolves plain relative
  paths, so `![alt](plot1.png)` just works inside a bundle.
- **Social links come from `content/posts/_index.md`'s `[cascade]`**, not from
  eight copies of the same front matter. The theme reads `.Params.linkedin` per
  page.
- **`<!--more-->` in every published page.** Summaries are explicit rather than
  dependent on Hugo's 70-word counting, which pulls a second paragraph into
  listings and shifts if the prose is edited.
- **Renaming a slug requires an `aliases` entry.** `matplotlib-seaborn-relplot`
  carries `aliases = ["/posts/matplotlib-searborn-replot/"]` so the old
  misspelled URL still redirects. Do the same for any future rename.
- **2 posts are drafts** (`notes-about-multi-objective-algorithms`,
  `take-picture-with-opencv-galileo`) and produce no pages. Confirm with
  `hugo list drafts` rather than trusting this line. The theme's own demo
  content (`introduction`, `what-is-hugo`, `my-first-post`), copied in during
  the 2020 setup, was deleted in 54ece1d; it still exists at the
  `pre-hugo-rebuild` tag, which is why the old site has those URLs.
- Post content is mixed English and Brazilian Portuguese while the site declares
  `en-us`. Keep a post in whatever language it already uses.

## Why `layouts/index.html` exists

It is not decoration — the theme's homepage is unusable without it. Upstream
`layouts/index.html`:

1. **Hardcodes its own blurb** ("Console is a minimal, responsive and light theme
   for Hugo…") with no config hook. The override sources the blurb from the about
   page's summary instead, so the homepage and `/about/` cannot drift apart.
2. Lists `first 3` posts; this site has always shown 4.
3. Prints a `<h1>Latest photos</h1>` heading *outside* the `with` guard that
   checks whether a `/photos` section exists, so a site without photos renders a
   stray empty heading.

Keep it close to upstream so it stays easy to diff after a theme update.

## Theme

[hugo-theme-console](https://github.com/mrmierzejewski/hugo-theme-console),
pulled in as a Hugo Module. 
The theme is based on a modern and minimal [Terminal CSS](https://terminalcss.xyz/) framework.
**Upstream publishes no git tags**, so `go.mod` pins
a commit pseudo-version (`v0.0.0-20260618131919-0418631e543a`) and `go.sum` locks
the hash. Pin a new commit deliberately; don't float.

Known limits, all upstream:

- Only `linkedin` renders in post headers, and tags render nowhere at all.
  Both are fixed by `layouts/posts/single.html`, which is why
  that override now exists. The Github link had been declined on its own as
  not worth the maintenance; tags needed the same file, so it came along.
- The theme can never emit `article:tag` OpenGraph meta.
  `partials/opengraph.html` nests the tag loop inside
  `range .Site.Params.Authors`, which rebinds `.` to the author map, so
  `.Params.tags` is empty inside it. Setting `[[params.Authors]]` does not
  help; it only makes the sibling line emit an empty `article:section`.
  Fixing it means overriding the partial, which is not worth it.
- The build prints a `.Site.LanguageCode was deprecated` warning. It is neither
  this config (which uses `locale`) nor the theme (no `rss.xml`, and its
  `sitemap.xml` doesn't reference it) — it comes from Hugo's own embedded
  `_internal/rss.xml`. Nothing to fix locally.

## CI security posture — don't undo these

The workflow is hardened against the 2025 Actions supply-chain pattern. Four
rules, all of which look like noise until they matter:

- **Actions are pinned to full commit SHAs**, with the version in a trailing
  comment. Never "simplify" these back to `@v4`. Tags are mutable — the
  tj-actions/changed-files compromise (CVE-2025-30066) retagged existing
  versions to a commit that leaked runner secrets into public build logs.
- **`HUGO_DEB_SHA256` must be updated whenever `HUGO_VERSION` changes**, or the
  build fails the integrity check by design. Get the value from the release's
  `hugo_<version>_checksums.txt` and confirm it against a local `sha256sum`.
- **`pages: write` / `id-token: write` live on the `deploy` job only.** Don't
  move them back to the workflow level; the build job runs third-party code and
  should not be able to publish.
- **`persist-credentials: false` on checkout.** Nothing pushes from CI, so no
  token should sit in `.git/config`.

Dependabot watches `github-actions` and `gomod` weekly. Actions bumps are
routine; **theme bumps deserve a diff read**, because a Hugo Module executes
templates during the build. Hugo's default policy limits the damage —
`security.funcs.getenv` allowlists only `^HUGO_` and `^CI$`, so a theme cannot
read `GITHUB_TOKEN` — but `resources.GetRemote` can still reach any HTTPS host.
Inspect the effective policy with `hugo config --format json`.

There are **no secrets in this repo** and the workflow has no `pull_request` or
`issue_comment` trigger, so fork PRs execute nothing. Keep it that way: adding
`pull_request_target` would open the "pwn request" class that most public-repo
Actions compromises rely on.

## Working here

- Pushing to `main` deploys. There is no review gate, so push only when asked.
- The `github-pages` environment carries a **deployment-branch policy**. It was
  created pinned to `master`, so the rename to `main` made every deploy fail with
  *"Branch main is not allowed to deploy to github-pages due to environment
  protection rules"* while the build itself passed. If the default branch is ever
  renamed again, update Settings → Environments → `github-pages` → Deployment
  branches first.
- Before changing content, check the rendered result against the
  `pre-hugo-rebuild` tag if fidelity matters.
- `about/` and `cv/` were rewritten on 2026-07-30 against a CV PDF kept outside
  the repo (`.local/`, gitignored). **That PDF is the source of truth for dates**
  — it is what settled two one-month disagreements the old page had. Update it
  first, then the page.

## Domain

The custom domain `gabicavalcante.dev` was configured in Settings → Pages on
2026-08-28. Two things hold it in place, and they are independent:

- **`static/CNAME`** — one line, `gabicavalcante.dev`, no `www`, no blank
  second line. Hugo copies `static/` into `public/` on every build, so the file
  rides along in the Pages artifact. Without it a deploy can clear the custom
  domain setting, because with Source = "GitHub Actions" there is no branch
  holding a `CNAME` for GitHub to read back.
- **`baseURL` in `hugo.toml`** — `https://gabicavalcante.dev/`, trailing slash.
  It feeds absolute URLs, `og:url`, the sitemap, RSS, and alias redirects. A
  mismatch between the served domain and `baseURL` is why the old
  `gabicavalcante.me` domain misbehaved.

**But the CI build overrides `baseURL`.** The workflow runs

```
hugo --gc --minify --baseURL "${{ steps.pages.outputs.base_url }}/"
```

and the flag beats the config file. So `hugo.toml`'s `baseURL` governs local
builds only; in CI the domain comes from `actions/configure-pages`, which reads
it from the Pages API — i.e. from the custom domain setting. Both are correct
today and agree with each other. The consequence worth knowing: if the custom
domain is ever cleared in Settings, CI silently goes back to emitting
`github.io` links even though `hugo.toml` still says `.dev`. Dropping the
`--baseURL` flag would make `hugo.toml` the single source of truth; that has
not been done.

Verify a change to either with `hugo --gc --minify` into a throwaway
`--destination` and grep the output for the old domain — never build into
`public/` just to check.

## Taxonomy

`tags` is the only taxonomy. `[taxonomies] tag = "tags"` in `hugo.toml`
*replaces* Hugo's defaults, which are tags **and** categories; nothing here
sets a category, and the default was building an empty `/categories/` page
into the site and the sitemap.

Hugo's two taxonomy template names are the reverse of what they sound like.
Verified on 0.164, so don't re-derive it from the names:

| URL | Page kind | Template |
|---|---|---|
| `/tags/` | `taxonomy` | `layouts/_default/terms.html` |
| `/tags/<term>/` | `term` | `layouts/_default/taxonomy.html` |

Only `terms.html` is overridden. Term pages have no `taxonomy.html`, so they
fall through to the theme's `_default/list.html`, and a dated list of posts
with summaries is the right thing there. `terms.html` exists because that same
list template rendered each *term* as a fake post: empty summary, plus a
meaningless date inherited from the newest post carrying it.

`capitalizeListTitles = false` keeps term titles lowercase, so
`data-visualization` does not render as `Data-Visualization`. It has to stay at
the **top level** of `hugo.toml`; appended after `[params]` it silently becomes
a param that nothing reads.

Tags are lowercase and hyphenated, and posts carry two to four. Adding one is
just `tags = [...]` in the post's front matter; every page under `/tags/` is
generated, so never create files there.
