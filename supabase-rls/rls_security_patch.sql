-- RLS Security Patch — Feb 25, 2026
-- Enables RLS on all internal tables and locks down write access.
-- anon key (browser) → SELECT only
-- service_role (server) → bypasses RLS entirely, full access

-- ── Enable RLS ────────────────────────────────────────────────────────────────
ALTER TABLE public.notes                      ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.claude_global_instructions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.claude_tabs                ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.claude_history             ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.claude_tokens              ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.claude_config              ENABLE ROW LEVEL SECURITY;

-- ── anon SELECT only (frontend reads + realtime subscriptions) ────────────────
CREATE POLICY "anon_select" ON public.notes                      FOR SELECT TO anon USING (true);
CREATE POLICY "anon_select" ON public.claude_global_instructions  FOR SELECT TO anon USING (true);
CREATE POLICY "anon_select" ON public.claude_tabs                 FOR SELECT TO anon USING (true);
CREATE POLICY "anon_select" ON public.claude_history              FOR SELECT TO anon USING (true);
CREATE POLICY "anon_select" ON public.claude_tokens               FOR SELECT TO anon USING (true);
CREATE POLICY "anon_select" ON public.claude_config               FOR SELECT TO anon USING (true);
-- No INSERT/UPDATE/DELETE policy for anon = hard blocked by RLS.
-- All writes go through Next.js API routes using service_role (bypasses RLS).

-- ── Drop overly permissive write policies (applied to all roles by mistake) ───
-- blog_posts and shared_notes API routes use service_role which bypasses RLS,
-- so these policies were redundant and dangerously open to anon.
DROP POLICY IF EXISTS "service write"  ON public.blog_posts;
DROP POLICY IF EXISTS "service delete" ON public.shared_notes;
DROP POLICY IF EXISTS "service insert" ON public.shared_notes;

-- ── Intentionally kept (by design) ───────────────────────────────────────────
-- visits: "Allow anonymous inserts" + "Allow authenticated inserts" → analytics
-- blog_comments: "public insert" → public commenting
-- webdrops: "public insert" + "public delete" → file drop sessions are public
-- shared_notes: "public read" → anyone with share link can read
