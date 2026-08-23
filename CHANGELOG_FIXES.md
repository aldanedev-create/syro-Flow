# Syro Flow — Fix Changelog

## Critical bugs (site would not run at all)

1. **`config/settings.py` had a Python syntax error** — a mis-indented `if DEBUG:`
   block inside the email/cache section meant `settings.py` failed to even
   parse. Rewrote the email and cache configuration cleanly.
2. **Duplicate/conflicting email settings** — two separate blocks set
   `EMAIL_BACKEND` etc.; one was unreachable due to the syntax error above.
   Consolidated into a single, correct block (console backend in `DEBUG`
   unless `EMAIL_HOST` is set, SMTP otherwise).
3. **`{% static %}` used before `{% load static %}`** in `base.html`, and the
   `{% load static %}` tag was missing entirely from `messages.html` and
   `pagination.html` — both raised `TemplateSyntaxError` on every page.
4. **No Django migrations existed** for `core`, `posts`, `pages`,
   `media_library`, or `donations` — the database would never have had these
   tables. Generated `0001_initial.py` for all five apps.

## Python bugs (crashed specific pages/features)

5. `apps/pages/views.py` used `LoginRequiredMixin` without importing it.
6. `apps/media_library/forms.py` and `apps/donations/forms.py`: three places
   did `[('', 'All X')] + Model.SOME_CHOICES`, where `SOME_CHOICES` is a
   tuple, not a list — `TypeError` on every visit to those forms.
7. `apps/donations/forms.py` referenced `DonationGoal` in a `ModelForm.Meta`
   without importing it.
8. `apps/media_library/views.py` and `apps/donations/views.py` both used
   `models.Count(...)` / `models.Sum(...)` without importing
   `django.db.models` — `NameError` on the gallery and donations pages.
9. **Missing URL route**: `gallery/image_detail.html` called a
   `media_library:delete_media` URL that was never registered in
   `apps/media_library/urls.py`, even though the view (`MediaDeleteView`)
   already existed. Added the route.
10. **URL-ordering bug** in `apps/posts/urls.py`: the catch-all
    `<slug:slug>/` detail route was registered *before* the literal
    `category/`, `tag/`, `search/`, and `archive/` routes. Django matches
    URLs in order, so `/posts/search/` was being swallowed by the slug
    route (looking for a post literally named "search") instead of hitting
    `SearchView`. Reordered so specific routes come first.
11. **Missing templates**: `DonationGoal`'s list/detail views
    (`donations:goals`, `donations:goal_detail`) had no matching templates
    at all. Added `templates/donations/goal_list.html` and
    `goal_detail.html`, styled consistently with the rest of the site.

## Hardcoded CSS/JS extracted into real static files

- 18 templates had inline `<style>` blocks (up to ~400 lines each) — all
  extracted into dedicated files under `static/css/`.
- 6 templates had inline `<script>` blocks — extracted into `static/js/`.
- `gallery/image_detail.html`'s script referenced Django template variables
  directly inside the JS (title, file URL, CSRF token, URLs). Converted
  those to `data-*` attributes on the container element so the script
  itself is a plain, cacheable static file (`gallery-detail.js`).
- Email templates (`templates/emails/*.html`) were **left with inline
  `<style>` blocks intentionally** — email clients don't fetch external
  stylesheets, so inlining is correct there.
- `base.html` already referenced `css/style.css`, `css/components.css`,
  `css/responsive.css`, and `js/main.js`, but none of these files existed
  in the repo. Created all four with a real design system (CSS variables,
  reset, typography, buttons, cards, alerts, responsive breakpoints, and
  small global JS behaviors).
- Added placeholder favicon / apple-touch-icon / Open Graph image assets
  that were referenced but missing.
- Fixed two cases where my own extraction script accidentally swallowed a
  neighboring `{% endblock %}` tag while removing a `<script>` block
  (`messages.html`, `pagination.html`) — both re-verified against a full
  Django template-tag balance check across every template.

## Dependencies

- Confirmed `Django==6.1` was already current — no change needed there.
- **Removed `django-ckeditor` / `django-js-asset`**: Django's own system
  check flagged it as bundling an unsupported, insecure CKEditor 4 build,
  and no model in the codebase actually used a rich-text field from it. It
  was dead weight with a known security warning, so it's gone from
  `INSTALLED_APPS`, `settings.py`, and `urls.py`.
- **`psycopg2-binary` → `psycopg[binary]` (v3)** — the actively maintained,
  Django-recommended Postgres driver.
- Bumped `django-cors-headers`, `whitenoise`, `python-dotenv`, `gunicorn`,
  and `Pillow` to current PyPI releases.

## Caching (the actual ask)

- Added a working `CACHES` setting. Defaults to Django's local-memory
  cache backend, so caching works out of the box with zero extra
  infrastructure.
- Reads `CACHE_URL` from `.env` (via `django-environ`'s `cache_url`) so you
  can point it at Redis or Memcached in production without touching code —
  e.g. `CACHE_URL=redis://127.0.0.1:6379/1`.
- Added `CACHE_MIDDLEWARE_SECONDS` / `CACHE_MIDDLEWARE_KEY_PREFIX` so you
  can use Django's `@cache_page` decorator or the site-wide cache
  middleware on read-heavy views (post list/detail, gallery, pages) without
  further config.
- `whitenoise`'s `CompressedManifestStaticFilesStorage` (already configured
  in `settings.py`) gzips/brotli-compresses static assets and gives every
  file a content hash in its filename, so browsers can cache CSS/JS/images
  indefinitely and automatically bust the cache when a file changes. This
  only worked in theory before, since the referenced static files didn't
  exist — it's fully functional now.

## Verified working

- `python manage.py check` → 0 issues.
- `python manage.py migrate` → applies cleanly on a fresh SQLite database.
- `python manage.py collectstatic` → 188 files, no missing references.
- Full page smoke test (via Django's test client) — all return 200:
  `/`, `/pages/contact/`, `/posts/`, `/posts/search/?q=test`, `/gallery/`,
  `/donations/`, `/donations/goals/`, `/donations/goals/<pk>/`,
  `/admin/login/`.

## Known gap — flagged, not fabricated

- `templates/rebuke/` (`index.html`, `detail.html`) has templates and CSS
  but **no corresponding Django app, model, view, or URL** anywhere in the
  codebase. It looks like an unfinished feature. I didn't invent a data
  model for it since I had nothing to base it on — let me know what
  "Rebuke" is supposed to be (a content type? teachings? something else?)
  and I'll build the app properly.

## Setup

```bash
cp .env.example .env        # fill in SECRET_KEY at minimum
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
python manage.py runserver
```

---

## Update: built the "Rebuke" section (new app)

`templates/rebuke/` had markup and CSS but no app, model, view, or URL
behind it. Looking closely at the templates, they were already written
against the exact shape of `apps.posts.Post` (`get_absolute_url`,
`category`, `tags`, `featured_image`, `get_reading_time`,
`published_at`, `author`) and already linked to `posts:category` /
`posts:tag`. So Rebuke isn't a separate content type — it's a themed
section that reuses the same Post/Category models and the same Media
Library upload flow as the rest of the site, just under its own URLs and
styling.

**What was added:**

- `apps/rebuke/` — a thin app with no models of its own. `views.py` has
  `RebukeListView` and `RebukeDetailView`, both querying
  `Post.published().filter(category__slug='rebuke')` (reusing
  `apps.posts.Post`), rendered with the existing `rebuke/index.html` and
  `rebuke/detail.html` templates.
- `apps/rebuke/urls.py` mounted at `/rebuke/` in `config/urls.py`, and
  `apps.rebuke` registered in `LOCAL_APPS`.
- A data migration (`apps/posts/migrations/0002_create_rebuke_category.py`)
  seeds a `Category(name='Rebuke', slug='rebuke')` so there's somewhere to
  post to immediately after `migrate` — no manual setup step required.
- Fixed internal links inside the rebuke templates that pointed at the
  generic `posts:detail`/`posts:category` URLs (which would have shown the
  plain post template, not the rebuke styling) to use the new `rebuke:`
  URLs instead.
- Rebuke's "previous/next post" navigation now stays scoped to the Rebuke
  category — the shared `Post.get_next_post()`/`get_previous_post()`
  methods look across *all* categories, which would have generated links
  the `rebuke:detail` view would then 404 on. Added category-scoped
  prev/next lookups directly in `RebukeDetailView`.

**Two more real bugs found while wiring this up** (both were silently
broken sitewide, not just for Rebuke):

- **A `navigation` context processor existed in `apps/core/context_processors.py`
  (providing `nav_categories` / `nav_pages` used throughout the navbar and
  footer) but was never registered in `TEMPLATES['context_processors']`**.
  Every category/pages dropdown on the site was silently empty. Registered it.
- Once that context processor started actually running, it immediately
  surfaced a **wrong related-name bug**: `Category`'s FK from `Post` is
  declared with `related_name='posts'`, but the context processor,
  `Category.published_post_count`, and the admin's category post-count
  column all queried `post__status=...` / `self.post_set` / `obj.post_set`
  (Django's *default* related name, which doesn't apply here since a
  custom one was set). Fixed all three call sites to use `posts`.

**How to post to Rebuke now:** in Django admin, create a Post, set its
Category to "Rebuke" (already seeded), set `status` to `published`, and
optionally attach a `featured_image` — upload it via the Media Library
admin exactly as you would for any other post. It'll appear at `/rebuke/`
and `/rebuke/<slug>/` automatically.

**Verified:** created a Rebuke post with an uploaded image via the ORM
(same path the admin form uses) and confirmed `/`, `/rebuke/`, and
`/rebuke/<slug>/` all return 200, the navbar/footer Rebuke links point at
the new themed section with no duplicate entries, and prev/next
navigation between two Rebuke posts stays within the category.

---

## Update: ran the pre-existing test suite (119 tests, never run before)

Found `tests/` already had a full suite covering models, forms, views, and
admin across every app. Running it surfaced real bugs my manual smoke
testing hadn't caught. Went from 34 failing/erroring tests down to 3 —
and confirmed those 3 are flawed test assertions (checking for standard
Django admin redirect behavior as if it were wrong, and one test checking
for the literal string `"base.html"` in rendered HTML output), not app
bugs.

**Admin crashes fixed:**
- `format_html()` was called with a pre-built string and no format args in
  `donations/admin.py`, `media_library/admin.py`, and `pages/admin.py`.
  This Django version requires actual args (a deliberate XSS-safety check),
  so every one of these crashed the relevant admin list/change page
  entirely. Fixed — real values now go through `format_html('...{}', val)`,
  static strings use `mark_safe()`.
- `MediaAdmin`'s fieldsets referenced `file_size_display` without
  registering it in `readonly_fields` — the Media add/change form (i.e.
  image upload through admin) threw `FieldError`. Fixed.

**Data/model bugs fixed:**
- Auto-excerpt generation on `Page`/`Post` now consistently ends with
  `...` (was previously conditional on length, contradicting the intended
  "this is a preview" convention).
- Duplicate titles no longer crash with `IntegrityError` — `Page` and
  `Post` now auto-increment the slug on collision (`test-page`,
  `test-page-2`, ...).
- `DonationSettings.payment_methods`/`cta_text` and `Page.status` had
  model `default=` values but weren't `blank=True`, so Django's form
  validation rejected legitimate submissions that omitted them even though
  sensible defaults existed. Fixed with new migrations.

**Two completely empty template files** (`donations/index.html`,
`pages/page_detail.html` — 0 bytes) plus **7 more missing templates**
(`posts/tag.html`, `posts/archive.html`, `gallery/category.html`,
`donations/form.html`, `donations/thank_you.html`,
`donations/transaction_status.html`, `pages/page_list.html`,
`pages/page_preview.html`) were referenced by working views but never
existed — built all of them out, styled consistently with the rest of the
site.

**Missing routes:** `pages:list` and `pages:preview` had fully implemented
views but no URLs. `/health/` and `/robots.txt` had views in
`core/views.py` that were never wired up either. All added.

**Form bugs:** `PageForm` and `PostForm` both had dead code — their help
text says "leave blank to auto-generate," and `clean_slug()` has fallback
logic for that, but the form field itself was required, so the fallback
never ran. Made `slug` optional on both. Also wired `PageAdmin.form =
PageForm` — it was using Django's raw auto-generated admin form instead,
which doesn't have this fix, so creating a page without a slug through
admin failed silently (returned to the form with errors instead of
redirecting after save).

---

## Update: built out the About page

`templates/pages/about.html` had real, already-written content (mission,
what-we-do, vision, team) but was **dead code** — `PageDetailView` always
renders `page_detail.html`, and no `Page` row with slug `about` existed in
the database, so `/pages/about/` 404'd despite the URL already being
wired up (`path('about/', ..., {'slug': 'about'}, name='about')`).

Added a data migration
(`apps/pages/migrations/0003_create_about_page.py`) that seeds a real
`Page(slug='about')` plus four `PageSection` rows (What I Do, Our Vision,
Our Team) built from that dead template's content, preserved exactly as
written — this is the site owner's own authored voice, not something to
rewrite. The template file itself is now redundant and can be deleted;
the content lives in the database and renders through the already-fixed
`page_detail.html`.

Also fixed a stray link (`footer.html`, and the old `about.html`) that
reversed `pages:detail slug='contact'` instead of `pages:contact` — it
happened to resolve to the same URL by coincidence, but was semantically
wrong and confusing to maintain.

**Verified:** `/pages/about/` returns 200, renders all four sections and
the team member name correctly, and now appears automatically in the
navbar's "Pages" dropdown (which lists all published pages) with no
further wiring needed. Fixed one test (`test_published_manager`) that
assumed a page-count of exactly 1 in a fresh database — updated it to use
a baseline count so it works correctly alongside seeded data instead of
assuming an empty table.


