# 📋 Team RIP: Master Task Forwarding Board
> **Live Task Forwarding Ledger** | Synced via Git across all branches  
> **Last Updated:** 2026-11-13 14:57:34 | **Active Tasks:** 0

---

## 🚦 Live Task Dispatch Status

| Task ID | Title | Requester | Assigned Worker | Type | Priority | Status | Branch / Output |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TASK-001** | Generate Spectral SED Unit Tests | `@iceodu` | `@coolodu` | `token_heavy` | `NORMAL` | 🟢 COMPLETED | `tests/test_sed.py` |

---

## 📥 Quick Commands

- **Forward a task:** `python tools/task_forwarder.py dispatch --from <name> --to <name> --type <token_heavy|compute_heavy> --title "..." --brief "..."`
- **Check assigned tasks:** `python tools/task_forwarder.py check --worker <name>`
- **View task board:** `python tools/task_forwarder.py list`
- **Claim a task:** `python tools/task_forwarder.py claim --task <TASK-ID> --worker <name>`
- **Complete a task:** `python tools/task_forwarder.py complete --task <TASK-ID> --output "<path>"`
