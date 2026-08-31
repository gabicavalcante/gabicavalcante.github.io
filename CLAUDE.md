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
hugo.toml                 baseURL, nav (params.navlinks), monokai highlighting,
                          [taxonomies], [params.author] for the JSON-LD, and
                          ignoreFiles. Careful in here: key placement and
                          anchoring both bite. See Conventions for the TOML
                          table rule, Taxonomy for capitalizeListTitles, and
                          the ignoreFiles comment itself — that one is matched
                          against the ABSOLUTE path, so anchoring it with ^ is
                          what breaks it.
go.mod / go.sum           theme module, pinned by commit
layouts/index.html        homepage override — see below, do not delete
layouts/posts/single.html post override: Github link + tag links
layouts/_default/terms.html  /tags/ index — see Taxonomy below
layouts/_default/baseof.html  <head> override — see Theme below. Upstream verbatim
                          from <body> down; keep it that way so it stays
                          diffable after a theme bump.
layouts/partials/seo-description.html  returns one page's description. Its own
                          partial because baseof and opengraph both need the
                          identical string and must not drift.
layouts/partials/opengraph.html  fixes empty og:description and missing
                          article:tag — see Theme below.
layouts/partials/schema.html  JSON-LD, as a single @graph on each page that
                          gets any: BlogPosting on posts, Person on /about/,
                          BreadcrumbList everywhere with real ancestors. The
                          home page, 404 and the alias stub emit nothing.
                          Identity comes from [params.author] in hugo.toml,
                          separate from the linkedin/github cascade — that one
                          drives the visible per-post links.
layouts/robots.txt        adds the Sitemap line Hugo's built-in one omits.
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
- **In `hugo.toml`, table headers go below the scalar keys they share a section
  with.** A TOML table header captures every scalar that follows it until the
  next header, so a `[params.author]` declared above `animateStyle` turns it
  into `params.author.animateStyle` and whatever reads it silently gets
  nothing. This has bitten twice: once as `capitalizeListTitles` landing under
  `[params]` (see Taxonomy), once as `animateStyle` landing under
  `[params.author]`, which dropped the theme's load animation from every page.
  Neither fails the build. Check with `hugo config --format json`.
- **Every post is a page bundle** (`posts/<slug>/index.md`), so images sit beside
  the post that uses them. The theme's image render hook resolves plain relative
  paths, so `![alt](plot1.png)` just works inside a bundle.
- **Social links come from `content/posts/_index.md`'s `[cascade]`**, not from
  eight copies of the same front matter. The theme reads `.Params.linkedin` per
  page.
- **`<!--more-->` in every published page.** Summaries are explicit rather than
  dependent on Hugo's 70-word counting, which pulls a second paragraph into
  listings and shifts if the prose is edited.
- **A materially revised post gets `lastmod`.** Without it Hugo falls back to
  `.Date`, so the JSON-LD `dateModified` just repeats `datePublished` and the
  revision is invisible to a crawler. Set it to the date of the commit that
  made the change, not today, and only for edits a reader would notice — a
  typo or a front-matter tweak does not count. `matplotlib-seaborn-relplot` is
  the worked example. `enableGitInfo` is off, so the front matter is the only
  source.
- **Renaming a slug requires an `aliases` entry.** `matplotlib-seaborn-relplot`
  carries `aliases = ["/posts/matplotlib-searborn-replot/"]` so the old
  misspelled URL still redirects. Do the same for any future rename.
- **3 posts are drafts** (`notes-about-multi-objective-algorithms`,
  `take-picture-with-opencv-galileo`, `parse-dont-validate-in-python` — the
  last still untracked) and produce no pages. Confirm with
  `hugo list drafts` rather than trusting this line. The theme's own demo
  content (`introduction`, `what-is-hugo`, `my-first-post`), copied in during
  the 2020 setup, was deleted in 54ece1d; it still exists at the
  `pre-hugo-rebuild` tag, which is why the old site has those URLs.
- Post content is mixed English and Brazilian Portuguese while the site declares
  `en-us`. Keep a post in whatever language it already uses — **and set
  `contentLang = "pt-br"` in its front matter** when it is not English, so the
  page ships the right `<html lang>`. Without it a Portuguese post is served
  labelled `en-us`, and search engines hand it to English readers who bounce.
  The key is `contentLang`; `lang` is reserved and fails the build.

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
- The theme's `partials/opengraph.html` emitted no `article:tag` and an empty
  `og:description` on every page. Both are fixed by
  `layouts/partials/opengraph.html`. The tag bug is that upstream nests the tag
  loop inside `range .Site.Params.Authors`, which rebinds `.` to the author
  map, so `.Params.tags` is always empty there; the override lifts the loop out
  of that range. Lifting it also frees the sibling `article:section` line,
  which then has to be guarded with `with` — `/about/` and `/cv/` have no
  section and emitted `content=""`. This was previously recorded here as not
  worth an override; the empty `og:description` changed that calculation.
  The same override also fixes `og:title`, which on tag pages was the bare term
  ("python") rather than the title element's "Posts tagged python", and
  `og:site_name`, which never emitted because upstream reads
  `.Site.Params.title` while the site title is a top-level key.
- The theme marks the **nav menu** up as a schema.org `BreadcrumbList` in RDFa.
  It is not a breadcrumb: the same three links in the same order on every page,
  never containing the page you are on. Search Console flagged it as *"field id
  is missing in itemListElement.item"*. `layouts/_default/baseof.html` strips
  that markup and `partials/schema.html` emits a real trail from `.Ancestors`.
  Worth knowing if you ever re-derive this: a conformant RDFa parser resolves
  `@href` fine (RDFa Core 1.1 §7.5, verified with pyRdfa3) — the blank node is
  a last resort. Google's extractor just is not conformant; it reads RDFa
  through microdata's nested-entity path. The markup was wrong on the merits
  regardless, which is the reason it went.
- The build used to print a `.Site.LanguageCode was deprecated` warning. It was
  the theme after all — the first line of its `_default/baseof.html` is
  `<html lang="{{ .Site.LanguageCode }}">`. (This file previously blamed Hugo's
  embedded `_internal/rss.xml`; that was wrong.) The baseof override replaces
  that line, so the warning is gone and the lang attribute is now per page, via
  `.Params.contentLang | default .Site.Language.Locale`. **The param is `contentLang`, never `lang`:**
  `lang` in front matter is reserved — Hugo deprecated it in v0.144 and removed
  it, and using it does not fall back silently, it fails the build with
  `error building site`.

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
just `tags = [...]` in the post's front matter. **Never create term files**
(`content/tags/python.md`) — every term page is generated, and a hand-written
one shadows the generated page. A taxonomy `content/tags/_index.md` is a
supported Hugo hook rather than a term file, but it comes with a trap: without
an explicit `title` key it overrides the auto-generated title with an empty
string, and `terms.html` then renders `<h1></h1>`. `/tags/` gets its meta
description from `partials/seo-description.html` instead, which is why no such
file exists.
