# Supabase RLS Security Patch

Drop-in SQL migration to lock down Supabase tables for a solo internal dashboard.

## What it does

- Enables RLS on all internal tables
- `anon` key (browser) → **SELECT only**
- `service_role` (server) → **bypasses RLS entirely**, full access
- Drops overly permissive write policies that accidentally grant anon write access

## Pattern

```
Browser  (anon key)      → SELECT ✅   INSERT / UPDATE / DELETE ❌
Server   (service_role)  → everything ✅  (RLS skipped)
```

## Usage

1. Copy `rls_security_patch.sql` and adapt table names to your project
2. Run via Supabase Management API or SQL editor:

```bash
curl -X POST "https://api.supabase.com/v1/projects/<project-id>/database/query" \
  -H "Authorization: Bearer <management-token>" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$(cat rls_security_patch.sql | tr '\n' ' ')\"}"
```

## Key concepts

| Key | Held by | RLS applies? |
|-----|---------|-------------|
| `anon key` | Browser (public) | ✅ Yes — policies enforced |
| `service_role` | Server only | ❌ No — bypasses RLS |

## Intentional exceptions (kept open by design)

- `visits` — anon INSERT allowed for analytics
- `blog_comments` — anon INSERT allowed for public commenting
- `webdrops` — anon INSERT + DELETE for public file drop sessions
- `shared_notes` — anon SELECT for anyone with a share link
