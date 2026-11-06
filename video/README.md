# Final demo recording

Record the working local application, about ten minutes, using synthetic data. Name a size-reviewed recording `dayone_proof_demo.mp4` (H.264 preferred). Show the chosen provider/model but never API keys, .env, authorization headers, real personal data or private tabs.

GitHub rejects ordinary Git files over **100 MB** (documented limit: 100 MiB); browser repository upload limit is 25 MiB. Large recordings should use **Git LFS** or **Google Drive/YouTube**, with the accessible link placed in `video/VIDEO_LINK.md`. A GitHub Release asset is also suitable. Test playback/permissions from a judge's perspective. Keep text readable rather than overcompressing.

Videos are **not ignored**. A reviewed recording within ordinary Git limits can be staged normally with `git add video/dayone_proof_demo.mp4`; review the file size and recording for secrets first. For larger files use the approved LFS/link/Release option above; LFS is not already configured by this repository. Root README must link to VIDEO_LINK.md/the actual accessible asset. Naming: one final link record; keep unwanted drafts outside the repository rather than relying on ignore rules. No recording exists in the foundation.

For the architecture segment, describe the confirmed local SQLite setup and optional future managed PostgreSQL accurately; see [database decision](../docs/DATABASE_DECISION.md). Name the actual tested provider/model (for example Groq only once its adapter/live run exists), not a planned integration.
