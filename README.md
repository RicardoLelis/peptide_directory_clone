# MyPeptideMatch Clone: Django + HTMX + Tailwind

A learning project that replicates the structure and design of a peptide-therapy
clinic directory (programmatic-SEO directory + lead generation + content layer)
using **Django templates, HTMX and Tailwind CSS**, managed with **uv**.

- **Database:** SQLite for development, PostgreSQL evaluated later (Phase 6 / 12)
- **Frontend:** server-rendered Django templates, HTMX for partial updates, Tailwind v4 compiled to a static file
- **Tooling:** uv (dependencies, virtualenv, tools), ruff (lint/format), pytest-django (tests)

> **Status:** Phase 1 complete (skeleton + design system). See [Roadmap](#roadmap).

---

## Table of contents

1. [Prerequisites](#prerequisites)
2. [Quick start](#quick-start)
3. [Project layout](#project-layout)
4. [Configuration](#configuration)
5. [Dependency management with uv](#dependency-management-with-uv)
6. [Frontend pipeline](#frontend-pipeline)
7. [Design tokens](#design-tokens)
8. [Templates](#templates)
9. [URLs](#urls)
10. [Code quality](#code-quality)
11. [Everyday commands](#everyday-commands)
12. [Troubleshooting](#troubleshooting)
13. [Conventions](#conventions)
14. [Roadmap](#roadmap)

---

## Prerequisites

- **uv**: install with `curl -LsSf https://astral.sh/uv/install.sh | sh`, or update with `uv self update`
- **Python 3.13**: uv can fetch it for you (`uv python install 3.13`)
- **make**: to run the shortcut commands in the `Makefile`
- A modern browser with dev tools (used for cache debugging, see [Troubleshooting](#troubleshooting))

No Node.js is required. Tailwind runs through a standalone binary wrapped by `pytailwindcss`.

---

## Quick start

```bash
# 1. Clone and enter the project
git clone <your-repo-url> peptide_directory
cd peptide_directory

# 2. Install Python + dependencies from the lockfile (creates .venv automatically)
uv sync

# 3. Create your environment file
cp .env.example .env        # or create .env by hand, see Configuration

# 4. Initialise the database
uv run manage.py migrate

# 5. Build the CSS once
make css-build

# 6. Run the two dev processes in separate terminals
make css     # terminal 1: Tailwind watch mode
make dev     # terminal 2: Django dev server
```

Open <http://127.0.0.1:8000/_design/> to see the design-system "kitchen sink" page.

---

## Project layout

```
peptide_directory/
├── manage.py
├── pyproject.toml            # dependencies, ruff and pytest config
├── uv.lock                   # exact dependency versions (commit this)
├── .python-version           # Python version pin
├── Makefile                  # shortcut commands
├── .env                      # local secrets/config (gitignored)
├── config/
│   ├── settings/
│   │   ├── base.py           # shared settings
│   │   ├── dev.py            # development overrides (used by manage.py)
│   │   └── prod.py           # production overrides (WhiteNoise, static root)
│   ├── urls.py               # root URL configuration
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── __init__.py
│   └── core/                 # site-wide pages (design system page for now)
│       ├── apps.py           # name = "apps.core"
│       ├── urls.py
│       └── views.py
├── assets/
│   └── tailwind.input.css    # Tailwind source: design tokens + scan paths
├── static/
│   ├── css/
│   │   ├── tailwind.min.css  # GENERATED, do not edit by hand
│   │   └── styles.css        # hand-written components (like globals.css)
│   ├── js/
│   │   └── htmx.min.js
│   ├── fonts/                # reserved for self-hosted fonts
│   └── img/
└── templates/
    ├── base.html
    ├── core/
    │   └── kitchen_sink.html
    └── partials/
        ├── navbar.html
        └── footer.html
```

---

## Configuration

### Settings package

Settings are split into a package. `manage.py` defaults to `config.settings.dev`:

```python
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
```

| File | Purpose |
|---|---|
| `base.py` | Everything shared: installed apps, middleware, templates, static config, `django-environ` setup |
| `dev.py` | `from .base import *` plus development-only settings |
| `prod.py` | `from .base import *` plus WhiteNoise, `STATIC_ROOT`, media and caching settings |

`BASE_DIR` in `base.py` must use **three** `.parent` calls, because the file sits inside a package:

```python
BASE_DIR = Path(__file__).resolve().parent.parent.parent
```

### Environment variables (`.env`)

Read with `django-environ` in `base.py`:

```python
import environ
env = environ.Env(DJANGO_DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG")
```

Minimal `.env`:

```
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True
```

`.env` is gitignored. Commit a `.env.example` with placeholder values instead.

### Installed apps and middleware (frontend-relevant)

```python
INSTALLED_APPS += ["django_htmx", "apps.core"]
MIDDLEWARE += ["django_htmx.middleware.HtmxMiddleware"]   # after CommonMiddleware
TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
```

`HtmxMiddleware` adds `request.htmx`, so views can tell HTMX requests from full page loads (used from Phase 5).

### Production settings (`prod.py`)

- WhiteNoise middleware must sit **directly after** Django's `SecurityMiddleware`, not at index 0:

  ```python
  _SECURITY = "django.middleware.security.SecurityMiddleware"
  _WHITENOISE = "whitenoise.middleware.WhiteNoiseMiddleware"

  if _WHITENOISE not in MIDDLEWARE:
      MIDDLEWARE.insert(MIDDLEWARE.index(_SECURITY) + 1, _WHITENOISE)
  ```

- Static files use hashed filenames, so browsers never serve stale CSS/JS after a deploy. On Django 4.2+, configure this through `STORAGES`:

  ```python
  STORAGES = {
      "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
      "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
  }
  STATIC_ROOT = BASE_DIR / "staticfiles"
  ```

- If a database cache backend is used, run `uv run manage.py createcachetable` once. Caching is revisited in Phase 11.

---

## Dependency management with uv

| Task | Command |
|---|---|
| Install everything from the lockfile | `uv sync` |
| Add a runtime dependency | `uv add <package>` |
| Add a dev-only dependency | `uv add --dev <package>` |
| Run a command in the project env | `uv run <command>` |
| One-off tool, no install | `uvx <tool>` (e.g. `uvx djlint templates/ --check`) |
| Global personal CLI tool | `uv tool install <tool>` |

**Runtime dependencies:** `django`, `django-htmx`, `django-environ`, `whitenoise`

**Dev dependencies:** `ruff`, `pytest`, `pytest-django`, `django-debug-toolbar`, `pytailwindcss`

Rule of thumb: anything the team or CI must run at a pinned version goes in the project (`uv add --dev`). Personal utilities go in `uv tool`. Always commit `pyproject.toml`, `uv.lock` and `.python-version`.

---

## Frontend pipeline

### How the two CSS files fit together

```
assets/tailwind.input.css  (tokens + scan paths)
        +
templates/**/*.html, apps/**/*.{html,py}  (class names Tailwind scans for)
        │
        ▼  uv run tailwindcss
static/css/tailwind.min.css      ← generated utilities + theme variables
static/css/styles.css            ← hand-written components, loaded AFTER Tailwind
```

- **`tailwind.min.css`** is generated. Tailwind only emits classes it finds in your templates, so the file must be rebuilt whenever you use a new class. Never edit it by hand.
- **`styles.css`** plays the role of `globals.css`: base typography and repeated components (`.btn`, `.card`, `.badge`, `.search-pill`, `.hero-bg`, `.eyebrow`). It reads tokens through CSS variables such as `var(--color-brand-600)`.

Rule of thumb: use Tailwind utilities for layout and one-offs directly in templates. When the same utility chain repeats around ten times, extract it into `styles.css`.

### Tailwind input (`assets/tailwind.input.css`)

```css
@import "tailwindcss";

/* Explicit globs: paths are relative to THIS file */
@source "../templates/**/*.html";
@source "../apps/**/*.{html,py}";

@theme static {
  /* design tokens, see the Design tokens section */
}
```

Two details that matter:

1. **Explicit `@source` globs** remove any doubt about what the scanner reads.
2. **`@theme static`** forces every token to be emitted as a CSS variable. Without `static`, Tailwind v4 drops variables that no utility class uses, which would break `styles.css` rules like `var(--color-brand-700)`.

### Cascade layers

`styles.css` wraps all its rules in `@layer components { ... }`. Tailwind v4 emits its utilities inside cascade layers, and **unlayered CSS always beats layered CSS**. Without the wrapper, a rule like `.btn { padding: ... }` would silently override a `px-10` utility on the same element. Load order matters too: `tailwind.min.css` first (it declares the layer order), then `styles.css`.

### Build commands

```bash
make css         # watch mode, rebuilds on template changes (development)
make css-build   # one-off minified build (before commit / deploy)
```

The wrapper downloads the Tailwind binary on first run. The installed version is Tailwind **v4.3.3**. If the wrapper ever lags behind a needed version, set `TAILWINDCSS_VERSION=v4.x.x`, or download the official standalone binary into `tools/` (gitignored).

### HTMX

`static/js/htmx.min.js` is served locally (no CDN). Record the pinned version in a comment at the top of the file or here in the README when you update it.

CSRF is handled once for every HTMX request by an attribute on `<body>` in `base.html`:

```html
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}' hx-boost="true">
```

### Fonts

Currently loaded from Google Fonts in `base.html`:

- **Saira Condensed** (weights 600, 700): headings (`font-display`)
- **Inter** (weights 400, 500, 600): body text (`font-sans`)

Both have fallback stacks. A later phase replaces this with self-hosted `woff2` files in `static/fonts/`.

---

## Design tokens

Colours were estimated from screenshots of the reference site, so treat them as a starting point.

| Token | Value | Utility examples | Used for |
|---|---|---|---|
| `--color-brand-50` … `700` | teal scale (`#effaf8` … `#0d5f59`) | `bg-brand-600`, `text-brand-600` | Buttons, links, accents |
| `--color-ink` | `#0b3b36` | `text-ink`, `bg-ink` | Headings, dark banner |
| `--color-nav` | `#0a0a0a` | `bg-nav` | Navbar and footer |
| `--color-surface` | `#f6f6f6` | `bg-surface` | Page background |
| `--color-tint-mint` / `peach` / `rose` / `lavender` / `sky` | pastels | `bg-tint-peach` | Category card backgrounds |
| `--color-status-fda-*` | green | `.badge-fda` | FDA Approved badge |
| `--color-status-compound-*` | blue | `.badge-compound` | Compounding badge |
| `--color-status-research-*` | grey | `.badge-research` | Research Use badge |
| `--font-display` | Saira Condensed | `font-display` | Headings |
| `--font-sans` | Inter | `font-sans` | Body |
| `--radius-card` | `1rem` | `rounded-card` | Cards |
| `--shadow-card` | soft two-layer shadow | `shadow-card` | Cards, search pill |

The three status badges map one-to-one to the peptide regulatory-status enum introduced in Phase 2.

### Component classes in `styles.css`

`.eyebrow`, `.btn`, `.btn-primary`, `.btn-ghost`, `.card`, `.badge`, `.badge-fda`, `.badge-compound`, `.badge-research`, `.hero-bg`, `.search-pill`

---

## Templates

- **`base.html`**: document shell. Loads fonts, `tailwind.min.css`, then `styles.css`; includes the navbar and footer partials; loads `htmx.min.js` with `defer`. Defines `{% block title %}`, `{% block head_extra %}` and `{% block content %}`.
- **`partials/navbar.html`, `partials/footer.html`**: shared page chrome (placeholders until Phase 4).
- **`core/kitchen_sink.html`**: the design-system page at `/_design/`. Every new component is added here first, so it doubles as a visual regression page.

Mental model: `base.html` is a base class, blocks are overridable methods, and partials are pure functions (context in, HTML out).

---

## URLs

| Path | Name | View |
|---|---|---|
| `/_design/` | `core:kitchen-sink` | `KitchenSinkView` (`TemplateView`) |
| `/admin/` | | Django admin |

Root config (`config/urls.py`):

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
]
```

---

## Code quality

Configured in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py313"
extend-exclude = ["**/migrations/*.py"]      # auto-generated files

[tool.ruff.lint]
select = ["E", "F", "I", "B", "DJ", "UP"]    # DJ = flake8-django rules

[tool.ruff.lint.per-file-ignores]
"config/settings/*.py" = ["F403", "F405"]    # star imports are intentional in settings

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.dev"
python_files = ["tests.py", "test_*.py"]
```

Notes:

- `# noqa` comments only work on the **same line** as the violation. A per-file ignore is the right tool for settings modules.
- Django's `startapp` generates unused imports; `ruff check --fix` removes them.

Verified state at the end of Phase 1:

```
uv run ruff check .            → All checks passed!
uv run ruff format --check .   → 18 files already formatted
uv run manage.py check         → System check identified no issues (0 silenced).
```

---

## Everyday commands

```bash
make dev                              # Django dev server
make css                              # Tailwind watch mode
make css-build                        # minified CSS build
make lint                             # ruff check + format check

uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py check
uv run pytest
uv run ruff check . --fix
uv run ruff format .
```

### Makefile

Recipe lines **must** start with a tab character, not spaces.

```makefile
css:            ## watch mode for development
	uv run tailwindcss -i assets/tailwind.input.css -o static/css/tailwind.min.css --watch

css-build:      ## minified, for commit/deploy
	uv run tailwindcss -i assets/tailwind.input.css -o static/css/tailwind.min.css --minify

dev:
	uv run manage.py runserver

lint:
	uv run ruff check . && uv run ruff format --check .
```

### `.gitignore` essentials

```
.venv/
.env
db.sqlite3
tools/tailwindcss
__pycache__/
staticfiles/
```

---

## Troubleshooting

Issues hit while building Phase 1, kept here for reference.

| Symptom | Cause | Fix |
|---|---|---|
| `404` at `/_design/` | App URLs not included | Check `config/urls.py` and `ROOT_URLCONF = "config.urls"` |
| `TemplateDoesNotExist` | `TEMPLATES[0]["DIRS"]` unset, or wrong folder | Templates live in `templates/` at the project root |
| `ModuleNotFoundError: apps.core` | Missing `apps/__init__.py` or wrong `AppConfig.name` | `name = "apps.core"` |
| Static path errors after splitting settings | `BASE_DIR` computed with two parents | Use three `.parent` calls |
| `NameError: INSTALLED_APPS` in `base.py` | `+=` used before the list exists | Define lists with `=` in `base.py`; use `+=` only in `dev.py`/`prod.py` |
| `make`: "missing separator" | Spaces instead of a tab in the Makefile | Use a real tab |
| Page has reset styles and components but no layout utilities (`flex`, `gap`, `max-w-*`) | Tailwind built with nothing to scan, or the build ran before the templates existed | Add explicit `@source` globs, rebuild with `make css-build` |
| Classes exist in `tailwind.min.css` (grep finds them) but the page is still unstyled | **Browser cached the old, near-empty CSS file** (the cause we hit) | Hard refresh (`Cmd+Shift+R`); keep dev tools open with **Disable cache** ticked |
| A `styles.css` component ignores a utility override | `styles.css` rules are outside `@layer` | Wrap them in `@layer components { ... }` |
| Custom variable like `var(--color-brand-700)` is undefined | Tailwind dropped an "unused" theme variable | Use `@theme static { ... }` |

### Debugging the CSS chain

Check each link in order:

```bash
# 1. file on disk
grep -o "\.bg-nav\|\.max-w-6xl\|\.flex{" static/css/tailwind.min.css | sort -u

# 2. file as Django serves it
curl -s http://127.0.0.1:8000/static/css/tailwind.min.css | grep -o "\.bg-nav" | sort -u

# 3. which file the static finder resolves
uv run manage.py findstatic css/tailwind.min.css -v2

# 4. duplicate copies
find . -name "tailwind.min.css" -not -path "./.venv/*"
```

Then check the Network tab in the browser (status `200`, response contains the classes) and the page source `<link>` order (Tailwind first, `styles.css` second).

In production, hashed filenames (`CompressedManifestStaticFilesStorage`) eliminate stale-cache problems, because a changed file gets a new URL.

---

## Conventions

- **One phase at a time.** Confirm each phase works before starting the next; reorganise only after functionality is complete.
- **Reusable UI comes first in the kitchen sink.** Add and check a component on `/_design/` before using it in real pages.
- **Utilities in templates, components in `styles.css`.** Extract at about ten repetitions.
- **Never edit `tailwind.min.css`.** Change tokens in `assets/tailwind.input.css` and rebuild.
- **Everything through `uv run`.** No manual virtualenv activation.
- **Lint before commit.** `make lint` must pass.

---

## Roadmap

| Phase | Topic | Status |
|---|---|---|
| 1 | Project skeleton and design system | Done |
| 2 | Data model: State, City, Clinic, Peptide, Treatment, Protocol, Review, Inquiry, Post; admin; seed data | Next |
| 3 | URLs, class-based views, template inheritance for entity pages | |
| 4 | Homepage assembled from partials with real queries | |
| 5 | HTMX: live search, filters, blog tabs, compare table, lead form | |
| 6 | Geo search; evaluate SQLite vs PostgreSQL | |
| 7 | SEO: sitemaps, canonical tags, breadcrumbs, JSON-LD | |
| 8 | Blog and dosing/titration calculators | |
| 9 | Auth and lead flow, rate limiting | |
| 10 | ETL: import, dedupe and refresh clinic data with pandas | |
| 11 | Testing, caching, query auditing | |
| 12 | Production: Docker Compose, PostgreSQL/PostGIS, WhiteNoise, gunicorn | |

### Planned app structure (Phase 2)

| App | Responsibility |
|---|---|
| `directory` | States, cities, clinics, reviews |
| `catalog` | Peptides, treatments, protocols |
| `content` | Blog posts and categories |
| `leads` | Inquiries and saved items |