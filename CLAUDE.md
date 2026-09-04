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
hugo server -D          # local preview; -D is required to see the drafts
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
layouts/_default/list.html  /posts/ and every /tags/<term>/ page. Fixes the
                          heading hierarchy (entries were h1), drops upstream's
                          <div>-inside-<p>, and formats the date the way the
                          rest of the site does — see the file. Otherwise
                          upstream verbatim.
layouts/_default/terms.html  /tags/ index — see Taxonomy below
layouts/_default/baseof.html  <head> override — see Theme below. Upstream verbatim
                          from <body> down; keep it that way so it stays
                          diffable after a theme bump.
layouts/partials/seo-description.html  returns one page's description. Its own
                          partial because baseof and opengraph both need the
                          identical string and must not drift.
layouts/partials/opengraph.html  fixes empty og:description and missing
                          article:tag — see Theme below.
layouts/partials/hreflang.html  rel="alternate" links pairing a post with its
                          translation — see Translations below.
layouts/partials/schema.html  JSON-LD, as a single @graph on each page that
                          gets any: BlogPosting on posts, Person on /about/,
                          BreadcrumbList everywhere with real ancestors. The
                          home page, 404 and the alias stub emit nothing.
                          Identity comes from [params.author] in hugo.toml,
                          separate from the linkedin/github cascade — that one
                          drives the visible per-post links.
layouts/robots.txt        adds the Sitemap line Hugo's built-in one omits.
layouts/_default/_markup/render-link.html   drops upstream's trailing space —
                          MUST NOT end in a newline, see the file.
layouts/_default/_markup/render-image.html  width/height, lazy loading and a
                          WebP srcset — see Mobile below. Pairs with
                          `height:auto` in assets/css/custom.css.
layouts/_default/_markup/render-table.html  wraps tables in a scrollable box;
                          the theme ships no such hook, so nothing upstream is
                          replaced.
layouts/_default/_markup/render-codeblock.html  wraps each fenced block so it
                          can carry a header row — language label, copy
                          button. See Code blocks below.
assets/js/code-copy.js    the only JavaScript on the site. Adds the copy
                          buttons; loaded with `defer` from the <head> half of
                          baseof.html. See Code blocks below.
layouts/shortcodes/quote.html  a blockquote plus an attribution line —
                          author, time, channel. Only for quotes that need
                          that line; plain `> ` markdown renders identically
                          otherwise, because custom.css styles `blockquote`
                          itself. See Blockquotes below for why the theme's
                          ">" gutter is gone.
layouts/partials/twitter_cards.html  empty on purpose; the theme's baseof calls
                          this partial unconditionally and it emitted twitter:
                          meta on every page. og:* still covers link previews.
static/CNAME              the custom domain; see Domain below
.github/workflows/hugo.yml
.claude/skills/review-post/   the /review-post editorial review. The only part of
                          .claude/ that is versioned, because it calibrates against
                          the posts in content/ and belongs with them. Its
                          references/voice-metrics.py deliberately hardcodes no
                          target numbers; see the skill.
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
- **One date format, `:date_medium`, everywhere.** `layouts/index.html`,
  `layouts/posts/single.html` and `layouts/_default/list.html` all use
  `.Date | time.Format ":date_medium"`. The listing used to keep upstream's
  `.PublishDate.Format "Jan. 2, 2006"`, which read "Sep. 3, 2026" against
  "Sep 3, 2026" on the same post elsewhere — and console.css gives the date a
  130px absolute gutter, so the extra period cut the gap to the title from
  14.8px to 5.2px on any two-digit day and made the column look ragged.
- **A materially revised post gets `lastmod`.** Without it Hugo falls back to
  `.Date`, so the JSON-LD `dateModified` just repeats `datePublished` and the
  revision is invisible to a crawler. Set it to the date of the commit that
  made the change, not today, and only for edits a reader would notice — a
  typo or a front-matter tweak does not count. `matplotlib-seaborn-relplot` is
  the worked example. `enableGitInfo` is off, so the front matter is the only
  source.
- **Renaming a slug requires an `aliases` entry.** `matplotlib-seaborn-relplot`
  carries `aliases = ["/posts/matplotlib-searborn-replot/"]` so the old
  misspelled URL still redirects. Do the same for any future rename — with one
  exception, recorded under Translations: never alias a path that another page
  now occupies. Hugo does not refuse it, it overwrites that page with the
  redirect stub, and prints nothing.
- **Some posts are drafts** and produce no pages. `hugo list drafts` is the
  only answer worth trusting; a count written down here goes stale on the next
  post. The theme's own demo content (`introduction`, `what-is-hugo`,
  `my-first-post`), copied in during the 2020 setup, was deleted in 54ece1d; it
  still exists at the `pre-hugo-rebuild` tag, which is why the old site has
  those URLs.
- Post content is mixed English and Brazilian Portuguese while the site declares
  `en-us`. Keep a post in whatever language it already uses — **and set
  `contentLang = "pt-br"` in its front matter** when it is not English, so the
  page ships the right `<html lang>`. Without it a Portuguese post is served
  labelled `en-us`, and search engines hand it to English readers who bounce.
  The key is `contentLang`; `lang` is reserved and fails the build.

## Blockquotes

`terminal.css` paints every blockquote with a column of `>` characters
(`blockquote::after`, a hundred of them separated by `\A`). That is the
email-reply convention, and **nothing on this site is a quotation of someone
else.** Audited when the rule was added: the seaborn post's "Update, August
2026" note and the three margin notes on the multi-objective post are asides
in the author's own voice, and the BLUF examples are status messages. The
`take-picture-with-opencv-galileo` post's `>` lines are a shell
heredoc inside a fenced code block, not blockquotes at all. The gutter also
renders the blank line between two paragraphs as a lone `>` floating in the
margin.

`custom.css` replaces it with a 2px `--primary-color` rule down the left,
keeping terminal.css's own `2ch` indent so the text does not move. Not a box
and not a background: the theme paints `pre` with a border *and*
`--block-background-color`, so a bordered box mid-paragraph competes with
every code block on the page.

`layouts/shortcodes/quote.html` is the same element with an attribution line
on top — `from`, `time`, `channel`, all optional. It emits a real
`<blockquote>`, so it and plain `> ` markdown are the same thing to a reader
and to a screen reader; the shortcode only earns its keep when the meta line
is wanted. With no params it renders identically to markdown, so use markdown.

## Code blocks

Four things were wrong at once, and they compounded. Measured in headless
Chromium across three code-heavy posts at 1200px and 390px, in both schemes.

- **A block had no surface.** `terminal.css` declares
  `--block-background-color: var(--background-color)` and nothing overrode it,
  so a code block was exactly page-coloured and existed only as a 1px
  hairline — while *inline* `code` got a real tint from `--code-bg-color`. A
  two-word snippet in a sentence was more distinct than a thirty-line block.
  `custom.css` now sets the variable: `#f6f8fa` light (1.065:1 against the
  page), `#2a2a2e` dark (1.110:1). **Set the theme's variable, never Chroma's
  own background** — `terminal.css` paints `pre` and `pre code` separately, so
  a background that reaches only the `pre` shows up as a frame in the padding.
  That is the bug the `[markup.highlight]` comment in `hugo.toml` records.
- **The border was 1.5x louder in the dark.** `#727578` on white is 4.63:1;
  `#a3abba` on `#222225` is 6.87:1, so the Celery post read as a ladder of 28
  bright frames. With a surface underneath, the border only marks an edge:
  `--block-border-color`, `#dfe3e8` / `#3a3a42`.
- **Code was set at prose leading.** `--global-line-height` is 1.6em, so every
  line of Python got 25.6px of box. Now 1.45. `pre code` has to be named
  alongside `pre`, because `terminal.css` sets line-height on a
  `blockquote,code,em,strong` group and `code` would otherwise keep its own.
- **Padding was 10px against a 16px font** — loose vertically, cramped
  horizontally, at the same time. 1em, and 0.75em below 850px because
  horizontal padding on a phone comes straight out of the line length, which
  the Mobile section works hard to protect.

The header row is a real cost, not free: at the theme's own leading it was
24.5px a block, 686px on the Celery post, which would have handed back most of
what the tighter code leading saved. It is pinned to `line-height: 1.4` for
that reason. Net on that post: 17043px -> 17775px of page, for 28 language
labels and 28 copy buttons.

`.code-head` is emitted even for the 14 fences that carry no language (11 in
the postgres draft, 3 in Celery), because the button still needs somewhere to
land; empty, it collapses.

**The label is server-rendered and the button is not.** A reader with
JavaScript off keeps the language and simply has no button, rather than one
that does nothing. `code-copy.js` also returns early when
`navigator.clipboard` is missing — that API needs a secure context, so it is
absent over plain http on a LAN address. **This means the button does not
appear if you preview with `hugo server --bind` on a LAN IP; localhost is a
secure context and works.**

The copy is the block's text exactly as rendered, prompts included. Some bash
blocks open with `$ ` and the Galileo post has a heredoc whose continuation
lines start with `> `. Stripping those would produce something that looks
pasteable and is not, so nothing is stripped.

Still deliberately untouched: **inline code is double-marked**, with literal
backtick glyphs from `terminal.css`'s `code::before/after` *plus* the tint.
Two signals for one thing, but it is the theme's terminal conceit rather than
a defect.

## The ==== under headings

Upstream switches it on with an **invalid value**, and that is not a typo to
tidy up — it is load-bearing. `terminal.css` draws the rule with
`h1::after { display: var(--display-h1-decoration) }` and sets the variable to
`none`; `console.css` overrides it with `1`. `1` is not a display value, so
the declaration is invalid at computed-value time, and `display` — not an
inherited property — falls back to its initial value, `inline`. The decoration
is on *because* the value is broken.

`custom.css` now sets `--display-h1-decoration: inline`, so the site no longer
depends on that. Nothing moves: `inline` is what the fallback already computed,
and absolute positioning blockifies it to `block` either way. The variable is
still the switch — set it to `none` to turn every ==== off.

Worth knowing when something looks wrong in production: this was investigated
after the decoration appeared missing on the live home page. It was not
missing. Prod rendered it correctly in a clean browser at the time, with
byte-identical markup and the same `custom.min.<hash>.css` as the local build.
The HTML is served with `cache-control: max-age=600` through Fastly, so a page
loaded within ten minutes of a deploy can be a stale copy. **Compare the
fingerprinted asset hash against a local build before chasing a CSS
difference.**

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

## Mobile

Google indexes mobile-first, so the phone rendering is what ranks. Every number
here was measured in headless Chromium — 19 pages x 15 viewports x 2 colour
schemes — because reasoning from the CSS got it wrong three times running.

**No page scrolls sideways any more.** It used to, and worse than a first pass
suggests: at 390px five pages overflowed (147/105/80/203/4 px), and at 320px
seven did, the worst by 272px. Two causes at baseline, plus one the font
restore introduced:

- The terminal prompt (`.logo`) is `display: table-cell` **and** carries
  `.terminal-prompt`'s `white-space: nowrap`. Two overrides fix it,
  `word-break: break-all` and `white-space: normal` — nowrap alone defeats
  word-break, which is why the obvious one-liner does nothing. Overriding the
  table-cell is **not** needed and is deliberately absent: measured, dropping
  it leaves overflow at 0 and the box identical.
- A markdown table cannot be squeezed below its min-content, so
  `table{width:100%}` cannot save a wide one. The Celery post's table was 573px
  in a 390px viewport at the theme's own 14px, and 649px once the font is
  restored. `layouts/_default/_markup/render-table.html` wraps every table in a
  `.table-scroll` box, so the table scrolls and the document does not. That
  wrapper keeps `tabindex="0"` (a scrollable box has to be keyboard-reachable)
  but deliberately carries **no** `role="region"`/`aria-label`: `/cv/` has ten
  tables and nine of them never scroll at any viewport, so that would have
  meant ten landmarks all named "Table". Do not re-add it.
- `console.css` drops `--global-font-size` to 14px below 850px, against 16px on
  desktop. Restored to 16px. On its own this made both overflows worse, which
  is why it and the `.logo` rule belong in the same change.

`terminal.css` also sets `word-break: break-all` on `pre`, which splits
identifiers mid-token. Setting it to `normal` **alone makes things worse**, and
this is the trap: `pre code` is `inline-block; min-width:100%`, so it is sized
by its min-content, which under `normal` becomes the longest token — the Celery
post went 203px -> 306px of overflow in testing. `pre code{overflow-x:scroll}`
does not save it. `overflow-wrap: anywhere` is the fix, because unlike
`break-word` it participates in intrinsic sizing. It also *improves* code
readability: mid-token breaks at 390px went 45 -> 11 on the seaborn post and
56 -> 28 on the Celery one, and to zero at desktop widths.

**`--page-width` differed between light and dark.** `console.css` declares
`--page-width: 60em` inside its `@media (prefers-color-scheme: dark)` block,
among the colour variables, and the light block does not set it — so the site
rendered 160px narrower in the dark at viewports above ~1000px. Overridden back
to 70em so there is one layout, which also makes `sizes` correct in both
schemes. 70em rather than 60em because it unifies on the value light mode --
the default -- already uses, rather than introducing a third width; dark-mode
readers above ~1000px do see the change. 60em for both would be defensible on
line length but is a design change, not a bug fix.

**Images** get intrinsic width/height, `loading="lazy"`, `decoding="async"` and
a WebP `srcset` (480/960/1440, filtered to the original width, plus the
original when no step reaches it, never above it). First load of the seaborn
post went from **1136 kB to 362 kB** at 390px; the PNGs are not fetched at all.
CLS on that post was an intermittent shift -- up to 0.00114, absent on most
loads, nonzero in 3 of 8 runs -- and is now a consistent **0** across every
run. Its LCP went from 2064 ms to
1406 ms on throttled mobile, because 775 kB of PNG had been competing with the
fonts for bandwidth.

`height: auto` in `custom.css` is load-bearing, not tidiness: `terminal.css`
sets `img{width:100%}` and no height, so the height attribute would be taken
literally and stretch the image to 350x1190. With it the attributes act only as
an aspect ratio, which is what reserves the space.

`sizes` is `(min-width: 1120px) 1080px, calc(100vw - 40px)`. The `- 40px` is
`.container`'s padding, and it matters: with a bare `100vw` the 481-520px band
at DPR 1 fetched 80 kB where 30 kB was enough.

The image hook is guarded with `reflect.IsImageResourceProcessable`, which is
the check Hugo's own error message names. An **SVG resolves as a resource but
has no `.Width`, and calling it fails the build outright** — one diagram in a
bundle would turn a content commit into a red deploy. GIF is excluded
separately: it is processable, but `Resize` would flatten an animation to frame
one. Both fall through to a plain `<img>`.

Known and deliberate: the hook lazy-loads unconditionally. Measured, the LCP
element is a `<p>` on every page, so nothing is harmed today — but the first
above-the-fold image ever added (a hero, or `me2.jpg` returning to `/about/`)
would be lazy-loaded as its own LCP element. Add an `.Ordinal` guard then.

Still open, and the largest remaining LCP item: the theme ships four
unsubsetted TTFs totalling 473 kB, of which **two are ever fetched**
(`RobotoMono-Regular` + `-Bold`, 224 KiB); the italics are declared and never
used. No `font-display`, no preload, no WOFF2. LCP is 1.32-1.60 s on throttled
mobile and 0.14-0.21 s unthrottled desktop. See TODO.md.

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

## Translations

One post exists in two languages, as two ordinary sibling bundles:

| URL | Language | Bundle |
|---|---|---|
| `/posts/vamos-conversar-sobre-comunicacao/` | pt-br, the original | `vamos-conversar-sobre-comunicacao/` |
| `/posts/lets-talk-about-communication/` | en, the translation | `lets-talk-about-communication/` |

**This site is deliberately not in Hugo's multilingual mode.** Turning on
`[languages]` for one post out of nine costs more than it gives: with
`defaultContentLanguage = "en"` the English version takes the root path and the
Portuguese one moves under `/pt-br/`, and it also generates a whole thin
`/pt-br/` skeleton — home page, `/pt-br/posts/`, `/pt-br/tags/`, its own RSS —
around a single page, with `about/`, `cv/` and the nav still in English.
Revisit only if several posts end up translated.

The two are paired by a **`translationGroup`** param they both set to the same
value. `layouts/partials/hreflang.html` collects every page sharing the value
and emits one `rel="alternate"` per page, **including the current page** —
hreflang sets must be self-referencing or Google ignores them wholesale. The
language comes from `contentLang` and defaults to `"en"`, not to
`.Site.Language.Locale`: `hreflang="en-us"` would offer the English version to
US readers only. Untranslated posts set no `translationGroup` and emit nothing,
which is correct.

The name is `translationGroup` and **not `translationKey`** — that one is
Hugo's own multilingual field, and handing it two pages in the same language is
asking a feature we are not using to do something it does not mean.

**The 2019 URL `/posts/lets-talk-about-communication/` now serves the English
translation, not the Portuguese original**, and there is deliberately no alias
for it — the one exception to the rename rule above. Do not "fix" this by
adding `aliases = ["/posts/lets-talk-about-communication/"]` to the Portuguese
post. Measured on 0.164: Hugo does not detect the collision, does not warn, and
does not skip the alias. It writes the redirect stub **over** the English post,
so `/posts/lets-talk-about-communication/` becomes a meta-refresh to the
Portuguese one and the English translation disappears from the site. The build
still reports success; the only visible difference is the alias count going
1 → 2.

The cost of having no alias is real but small: a Portuguese reader following an
old link lands on English and has to take the `em português` link at the top.
Nothing 404s, and it is the same piece either way. Both posts carry that
cross-link in the body, right after `<!--more-->` so it stays out of listings
and summaries.

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
