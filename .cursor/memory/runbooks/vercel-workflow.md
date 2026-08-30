# Domain: Vercel — deploy and Git workflow

## Purpose

Give agents a short, repeatable picture of how **repo changes** become **Vercel deployments** and how to operate the **CLI** (and optionally **MCP**) from a workspace.

## Paths / artifacts

- Repo root: current project root (for Next.js, confirm `package.json` scripts such as `dev`, `build`, and `start` when present).
- Optional linkage: `.vercel/` after `vercel link` (confirm gitignore before committing).
- Optional long-form handover: use a project-specific handover file only if one exists.

## Procedure summary

### Git → Vercel (usual)

1. Connect GitHub/GitLab/Bitbucket repo to the Vercel Project (dashboard).  
2. `git push` to default branch → Production build; other branches/PRs → Preview.  
3. Fix build/env in repo or dashboard env vars; push again to redeploy.

### CLI from repo root

1. `vercel login` if needed.  
2. `vercel link` (once per clone).  
3. `vercel` (preview) or `vercel --prod` (production).  
4. `vercel env pull .env.local` when local dev needs production-like env **names** (user handles secrets).

### This environment

- Use **terminal** with `npx vercel ...` when global CLI absent.  
- **Vercel MCP:** authenticate `plugin-vercel-vercel` (`mcp_auth`); if unavailable, use CLI.

## Validation

- Deployment appears in Vercel dashboard with expected commit or CLI upload.  
- `npm run build` succeeds locally when debugging Vercel build failures.

## Related

- `/TOOLS.md`, `/skills/vercel-deploy-workflow/SKILL.md`, `/memory/MEMORY.md`

---
