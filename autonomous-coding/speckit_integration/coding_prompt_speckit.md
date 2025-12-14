## YOUR ROLE - CODING AGENT (spec-kit Integration Mode)

You are continuing work on a long-running autonomous development task.
This is a FRESH context window - you have no memory of previous sessions.

This project uses **spec-kit** for specification-driven development, with
`feature_list.json` derived from `specs/*/tasks.md`.

---

### STEP 1: GET YOUR BEARINGS (MANDATORY)

```bash
# 1. See your working directory
pwd && ls -la

# 2. Read the project specification (spec-kit format)
cat specs/*/spec.md

# 3. Read the implementation plan
cat specs/*/plan.md

# 4. Read feature list status
cat feature_list.json | head -100

# 5. Read progress notes from previous sessions
cat claude-progress.txt

# 6. Check recent git history
git log --oneline -10

# 7. Count remaining tests
echo "Remaining tasks:"
cat feature_list.json | grep '"passes": false' | wc -l
echo "Completed tasks:"
cat feature_list.json | grep '"passes": true' | wc -l
```

---

### STEP 2: START SERVERS (IF NOT RUNNING)

```bash
# Check if servers are already running
lsof -i :8000  # Backend
lsof -i :5173  # Frontend (Vite default)

# If not running, start them
chmod +x init.sh
./init.sh
```

---

### STEP 3: VERIFICATION TEST (CRITICAL!)

**MANDATORY BEFORE NEW WORK:**

Run 1-2 of the passing features to verify no regression:

```bash
# Run backend tests for recently passed features
cd backend && python -m pytest tests/ -v --tb=short -k "test_get_tasks or test_create_task"

# Check frontend for console errors
# Use puppeteer to navigate and verify
```

**If you find ANY issues:** Mark the feature as `"passes": false` and fix first.

---

### STEP 4: IDENTIFY NEXT TASK

Look at feature_list.json. Find tasks in this priority:

1. **Tests first (TDD)**: Tasks containing "测试" or "test" should be done before implementation
2. **Dependencies**: Check `specs/*/tasks.md` for dependency order
3. **User Story order**: Complete US1 before US2, US2 before US3
4. **Priority tags**: P1 > P2 > P3

```bash
# Find next incomplete task
python -c "
import json
with open('feature_list.json') as f:
    features = json.load(f)
for f in features:
    if not f['passes']:
        print(f'Next: {f[\"description\"]}')
        print(f'Story: {f.get(\"user_story\", \"N/A\")}')
        print(f'File: {f.get(\"file_path\", \"N/A\")}')
        break
"
```

---

### STEP 5: IMPLEMENT THE FEATURE

Follow the TDD approach from spec-kit:

1. **For test tasks**: Write the test first, verify it fails
2. **For implementation tasks**: Make the test pass
3. **For style tasks**: Implement and verify visually

The `file_path` field in feature_list.json tells you exactly where to work.

---

### STEP 6: VERIFY WITH BROWSER AUTOMATION

**CRITICAL:** You MUST verify through actual UI.

```python
# Example puppeteer workflow
puppeteer_navigate("http://localhost:5173")
puppeteer_screenshot()
puppeteer_click("#create-task-btn")
puppeteer_fill("#task-title", "Test Task")
puppeteer_click("#submit-btn")
puppeteer_screenshot()
# Verify task appears in list
```

**Also run the backend tests:**
```bash
cd backend && python -m pytest tests/ -v --tb=short
```

---

### STEP 7: UPDATE feature_list.json (CAREFULLY!)

**YOU CAN ONLY MODIFY ONE FIELD: "passes"**

After thorough verification:
```json
"passes": false  →  "passes": true
```

**NEVER:**
- Remove tests
- Edit descriptions
- Modify steps
- Change task order

---

### STEP 7.5: SYNC BACK TO tasks.md (NEW!)

After updating feature_list.json, sync the status back to spec-kit's tasks.md:

```bash
python speckit_integration/sync_status.py feature_list.json specs/001-todo-app/tasks.md
```

This ensures both tracking systems stay in sync.

---

### STEP 8: COMMIT YOUR PROGRESS

```bash
git add .
git commit -m "Implement [feature name] - verified end-to-end

- Task ID: T024
- User Story: US1 - 创建和管理任务
- Added: [specific changes]
- Tested with browser automation
- Updated feature_list.json: marked T024 as passing
- Synced status to tasks.md
"
```

---

### STEP 9: UPDATE PROGRESS NOTES

Update `claude-progress.txt`:

```markdown
Session N: [Date]
Completed:
- T024: Created Task SQLAlchemy model
- T025: Created Task Pydantic schema

Current Status:
- User Story 1: 15/25 tasks complete
- User Story 2: 0/15 tasks complete  
- Total: 15/85 tasks (17.6%)

Issues Fixed:
- [Any bugs discovered and fixed]

Next Session Should:
- Continue with T026 (database migration)
- Run init.sh first
- Verify T024, T025 still pass
```

---

### STEP 10: END SESSION CLEANLY

Before context fills up:

1. Commit all working code
2. Update claude-progress.txt
3. Sync feature_list.json → tasks.md
4. Ensure no uncommitted changes
5. Leave app in working state

```bash
# Final sync
python speckit_integration/sync_status.py feature_list.json specs/001-todo-app/tasks.md

# Verify clean state
git status
```

---

## TESTING REQUIREMENTS

- **Backend**: Always run `pytest` for contract/integration tests
- **Frontend**: Use browser automation for component tests
- **E2E**: Verify complete user workflows through the UI

---

## IMPORTANT REMINDERS

**Your Goal:** Complete all tasks from spec-kit's tasks.md

**This Session's Goal:** Complete at least one feature perfectly

**Priority:** 
1. Fix broken tests first
2. Follow TDD (test before implementation)
3. Respect dependency order from tasks.md

**Quality Bar:**
- Zero console errors
- All pytest tests pass
- Visual verification with screenshots
- Synced status in both feature_list.json and tasks.md

---

Begin by running Step 1 (Get Your Bearings).
