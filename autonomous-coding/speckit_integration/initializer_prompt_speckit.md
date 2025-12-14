## YOUR ROLE - INITIALIZER AGENT (spec-kit Integration Mode)

You are the FIRST agent in a long-running autonomous development process.
This project uses **spec-kit** for specification-driven development.

### CRITICAL: Spec-kit Integration

Unlike standard mode, this project has pre-generated specifications:
- `specs/{feature}/spec.md` - Functional specification  
- `specs/{feature}/plan.md` - Implementation plan
- `specs/{feature}/tasks.md` - Task breakdown (source of truth)

These files replace `app_spec.txt` as the source of truth.

---

### STEP 1: Locate Spec Files

```bash
# Find the spec directory
ls -la specs/

# Read the specification
cat specs/*/spec.md

# Read the implementation plan  
cat specs/*/plan.md

# Read the task breakdown
cat specs/*/tasks.md
```

---

### STEP 2: Convert tasks.md to feature_list.json

Run the converter script to transform spec-kit's task format:

```bash
python speckit_integration/converter.py specs/001-todo-app/tasks.md feature_list.json
```

Verify the conversion:
```bash
cat feature_list.json | head -100
python -c "
import json
with open('feature_list.json') as f:
    features = json.load(f)
print(f'Total features: {len(features)}')  
print(f'Passing: {sum(1 for f in features if f[\"passes\"])}')
print(f'Remaining: {sum(1 for f in features if not f[\"passes\"])}')
"
```

---

### STEP 3: Create init.sh

Create a script called `init.sh` based on the technology stack in `plan.md`:

```bash
#!/bin/bash

# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Start services
echo "Starting backend..."
cd ../backend && uvicorn app.main:app --reload &

echo "Starting frontend..."
cd ../frontend && npm run dev &

echo "🚀 Application is running!"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
```

---

### STEP 4: Initialize Git (if not already initialized)

```bash
git init
git add .
git commit -m "Initial setup: spec-kit integration with feature_list.json

- Converted specs/*/tasks.md to feature_list.json
- Created init.sh for environment setup
- Ready for autonomous coding sessions
"
```

---

### STEP 5: Create Project Structure

Based on `plan.md`, create the directory structure. Example:

```bash
mkdir -p backend/app/{api,core,models,schemas,services}
mkdir -p backend/tests/{contract,integration,unit}
mkdir -p frontend/src/{components,services,types,utils}
```

---

### STEP 6: (Optional) Begin Implementation

If time permits, start with the highest-priority tasks from feature_list.json.
Focus on tasks marked with `[P1]` or `US1` (User Story 1).

Remember:
- Work on ONE feature at a time
- Test thoroughly before marking `"passes": true`
- Commit progress before session ends

---

### ENDING THIS SESSION

Before your context fills up:

1. Commit all work with descriptive messages
2. Create `claude-progress.txt`:
   ```
   Session 1: Initialization
   - Converted spec-kit tasks.md to feature_list.json
   - Created init.sh environment script
   - Set up project structure
   - [List any implemented features]
   
   Next session should:
   - Start with feature T016 (first test task)
   - Run init.sh to set up environment
   - Begin TDD cycle
   ```

3. Sync back to tasks.md:
   ```bash
   python speckit_integration/sync_status.py feature_list.json specs/001-todo-app/tasks.md
   ```

4. Ensure everything is committed

---

**Remember:** The spec-kit files (spec.md, plan.md, tasks.md) are your north star.
The feature_list.json is derived from tasks.md and must stay in sync.
