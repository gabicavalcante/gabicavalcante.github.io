# CLAUDE.md

## What this repo is

The Hugo **source** for a personal blog published at
<https://gabicavalcante.github.io> via GitHub Pages.

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
.github/workflows/hugo.yml
content/
  about/index.md + me2.jpg    page bundle; me2.jpg is the og:image
  cv.md                       12 markdown tables
  posts/_index.md             cascades linkedin/twitter to every post
  posts/<slug>/index.md       one bundle per post
```

## Conventions

- **TOML front matter** (`+++`), matching the theme's own examples.
- **Every post is a page bundle** (`posts/<slug>/index.md`), so images sit beside
  the post that uses them. The theme's image render hook resolves plain relative
  paths, so `![alt](plot1.png)` just works inside a bundle.
- **Social links come from `content/posts/_index.md`'s `[cascade]`**, not from
  eight copies of the same front matter. The theme reads `.Params.linkedin` and
  `.Params.twitter` per page.
- **`<!--more-->` in every published page.** Summaries are explicit rather than
  dependent on Hugo's 70-word counting, which pulls a second paragraph into
  listings and shifts if the prose is edited.
- **Renaming a slug requires an `aliases` entry.** `matplotlib-seaborn-relplot`
  carries `aliases = ["/posts/matplotlib-searborn-replot/"]` so the old
  misspelled URL still redirects. Do the same for any future rename.
- **4 posts are drafts** (`introduction`, `what-is-hugo`, `my-first-post`,
  `notes-about-multi-objective-algorithms`) and produce no pages. The first two
  are the *theme's own demo content*, copied in during the 2020 setup — that is
  why their titles look swapped. Not Gabi's writing.
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

- Only `linkedin` and `twitter` render in post headers. The pre-2026 site also
  showed a Github link; restoring it needs a `layouts/posts/single.html`
  override, which was declined as not worth the maintenance.
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
- The `about/` and `cv/` text is **stale as of 2026** — it describes working at
  Cloudia and "planning on enrolling as an M.Sc. student". Left as-is on purpose;
  rewriting it is a content decision, not a migration one.
- `categories/` and `tags/` pages generate but are empty: no post declares terms.
- If a `CNAME` is ever re-added, `baseURL` in `hugo.toml` must change with it.
  That mismatch is why the old `gabicavalcante.me` domain misbehaved.
