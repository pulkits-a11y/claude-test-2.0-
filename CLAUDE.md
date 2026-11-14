# HyperFrames videos

This repo holds [HyperFrames](https://hyperframes.heygen.com) video projects (HTML rendered to video).

- Projects: `my-video/` (each project has its own `CLAUDE.md` with commands and rules — read it before editing).
- `remotion-video/`: a [Remotion](https://www.remotion.dev) project (React rendered to video), scaffolded with `npx create-video@latest --hello-world --skills`. Its 13 Remotion agent skills are in `remotion-video/.agents/skills` (linked from `.claude/skills`); start at `/remotion-best-practices`. Run `npm install` there first in a fresh session.
- Skills: `.claude/skills/` holds all 9 HyperFrames skills. Start at `/hyperframes` for any video work.
- New project: `npx hyperframes init <name> --skip-skills --skill=hyperframes --non-interactive`
- Run `npx hyperframes ...` commands from inside the project folder.
- Cloud sessions: set `NODE_USE_ENV_PROXY=1` so the CLI's model downloads (whisper, Parakeet) go through the HTTPS proxy.
