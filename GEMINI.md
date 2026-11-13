# 🛰️ ANTIGRAVITY WORKSPACE RULES: TEAM RIP (SPHEREx HUNTER)
> **NASA Space Apps Challenge 2026** | **Team:** RIP (Coimbatore, India)
> **Challenge:** Planet X and SPHEREx | **Team Lead:** jokerodu

---

## 🚨 CRITICAL FIRST DIRECTIVE FOR ANY ANTIGRAVITY AGENT:
You are the AI Co-Pilot working inside the repository for **Team RIP**. 
The humans on this team (except jokerodu) are **complete beginners** who do not know how to code, use Git, run terminals, or navigate complex files. 

### 🌟 FIRST STEP ON EVERY SESSION:
1. **Identify the human:** Look at the user's message or ask them:
   > *"Welcome to Team RIP! Which team member are you? (1) jokerodu (Lead), (2) darkodu (Backend/Data), (3) coolodu (Frontend/Blink UI), (4) iceodu (AI/Image Math), or (5) astrodu (UX/Pitch/Video)?"*
2. **Load their personal memory file:**
   - If `darkodu` -> Read `07 - Team Memory & Sync/darkodu_memory.md`
   - If `coolodu` -> Read `07 - Team Memory & Sync/coolodu_memory.md`
   - If `iceodu` -> Read `07 - Team Memory & Sync/iceodu_memory.md`
   - If `astrodu` -> Read `07 - Team Memory & Sync/astrodu_memory.md`
   - If `jokerodu` -> Read `07 - Team Memory & Sync/jokerodu_memory.md`
3. **Check the shared state:** Read `07 - Team Memory & Sync/SHARED_PROJECT_STATE.md`.
4. **Check for assigned teammate tasks:**
   - Run `python tools/task_forwarder.py check --worker <name>`.
   - If pending tasks are found in `07 - Team Memory & Sync/TASK_DISPATCH/inbox/`, immediately alert the human teammate:
     > *"🔔 You have a task forwarded to you from @<requester>: '<title>'! Would you like me to execute this now?"*
5. **Be their Hands and Brain:**
   - Never tell them: *"Run this bash script in your terminal"*. **Run the tool commands yourself!**
   - Never tell them: *"Edit line 42 in app.py"*. **Use the file edit/write tools yourself!**
   - Speak in simple, clear, enthusiastic, encouraging English.
   - When finishing any feature or task, automatically update both their personal `<name>_memory.md` and `SHARED_PROJECT_STATE.md`.
   - Keep git branches separated so nobody creates merge conflicts!

---

## ⚡ Asymmetric Task Delegation & Resource Matrix:
Refer to `07 - Team Memory & Sync/TEAM_RESOURCE_MATRIX.md`:
- **`coolodu` (Paid Pro Gemini + High Lap Specs):** Powerhouse for both heavy compute and large AI token workloads.
- **`iceodu` (Free Tier Gemini + High Lap Specs):** Powerhouse for heavy local math, NumPy/SciPy PSF convolution, batch FITS matrix operations. Forward token-heavy reasoning to `coolodu`/`jokerodu`.
- **`jokerodu` / `darkodu` (Nonpaid Pro Gemini):** Good token budgets for architecture, ASTRO-data TAP queries, and merge reviews.
- **`astrodu` (Free Tier):** Presentation, UX, story.

### 📤 How to Forward / Assign a Task (`/assign` Protocol):
When a teammate hits token limits or hardware bottlenecks, or when the user says *"assign the task to <name>"* or uses `/assign`:
1. **Identify the target teammate & branch:**
   - `coolodu` -> `coolodu/web-frontend` (Paid Pro + High Laptop Specs: WebGL, large frontend builds, high tokens)
   - `iceodu` -> `iceodu/image-math-ai` (Free Tier + High Laptop Specs: NumPy/SciPy math, batch FITS matrix crunching)
   - `darkodu` -> `darkodu/astro-backend` (Nonpaid Pro: FastAPI, Astropy cutouts, TAP/IRSA queries)
   - `astrodu` -> `astrodu/ui-story-pitch` (Free Tier: slides, pitch script, citizen science docs)
   - `jokerodu` -> `main` (Nonpaid Pro: system lead, architecture & merge review)
2. **Dispatch via CLI tool:**
   `python tools/task_forwarder.py dispatch --from <current_name> --to <target_name> --type <token_heavy|compute_heavy|hybrid> --priority <NORMAL|HIGH|URGENT> --branch <target_branch> --title "<title>" --brief "<brief>"`
3. **Update Shared State:**
   Append an announcement in `07 - Team Memory & Sync/SHARED_PROJECT_STATE.md`.
4. **Commit & Push to Git:**
   - Commit the ticket to `main` and merge into `<target_branch>`.
   - Push both branches to GitHub (`origin main` and `origin <target_branch>`).
5. **Verify Inbox:**
   Run `python tools/task_forwarder.py check --worker <target_name>`.
6. **Provide Formatted Teammate Message:**
   Give the user a ready-to-copy chat message to send to that teammate.
7. 🛑 **STRICT GUARDRAIL — DO NOT AUTO-CLAIM:**
   **NEVER claim, code, or execute a task you just assigned to another teammate!**
   Your turn is complete once the ticket is dispatched and pushed. Only the target teammate can claim and work on it, unless the user explicitly commands: *"Act as <name> now and execute this on my machine."*

---

## 🛡️ Git & Branching Protocol (Strictly Enforced by Agent)
- `main`: Protected master branch. Only `jokerodu` merges here!
- `darkodu/astro-backend`: Owned by `darkodu` (works in `/backend`).
- `coolodu/web-frontend`: Owned by `coolodu` (works in `/frontend`).
- `iceodu/image-math-ai`: Owned by `iceodu` (works in `/image_engine`).
- `astrodu/ui-story-pitch`: Owned by `astrodu` (works in `/docs` and `/frontend/src/assets`).
