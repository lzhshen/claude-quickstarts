# autonomous-coding × spec-kit 集成方案

本文档详细描述如何将 **autonomous-coding**（自主编程框架）与 **spec-kit**（规格驱动开发工具）进行有机结合，实现更高质量的 AI 自主开发流程。

---

## 目录

- [一、背景与目标](#一背景与目标)
- [二、两个框架核心对比](#二两个框架核心对比)
- [三、集成策略分析](#三集成策略分析)
- [四、推荐方案：串联模式详细设计](#四推荐方案串联模式详细设计)
- [五、项目目录结构](#五项目目录结构)
- [六、使用指南](#六使用指南)
- [七、工具参考](#七工具参考)
- [八、后续优化建议](#八后续优化建议)

---

## 一、背景与目标

### 1.1 项目定位

- **autonomous-coding**：基于 Claude Agent SDK 的自主编程框架，能够多会话无人值守开发
- **spec-kit**：GitHub 开源的规格驱动开发工具包，强调 "What before How"

### 1.2 集成目标

1. **保留 autonomous-coding 的自主运行能力**：多会话无人值守开发
2. **利用 spec-kit 的规格驱动方法论**：提升任务定义质量
3. **结合两者的验证机制**：TDD + E2E 浏览器验证
4. **统一进度追踪**：双向同步任务状态

---

## 二、两个框架核心对比

### 2.1 核心机制对比

| 维度 | autonomous-coding | spec-kit |
|-----|-------------------|----------|
| **任务定义** | `feature_list.json`（20-200 个测试用例） | `tasks.md`（按用户故事组织，85+ 任务） |
| **任务粒度** | 以 E2E 测试为中心，每个功能有详细步骤 | 以文件/组件为中心，精确到具体路径 |
| **进度追踪** | `"passes": true/false` 单字段 | `[X]`/`[ ]` checkbox 标记 |
| **运行模式** | 多会话自主循环，无人值守 | 交互式 slash 命令，人工触发 |
| **验证方式** | Puppeteer 浏览器自动化 + 截图 | 依赖 TDD，测试先行 |
| **安全机制** | 沙箱 + 文件限制 + 命令白名单 | 无内置安全隔离 |
| **工作流阶段** | 初始化 → 编码（双智能体） | constitution → specify → clarify → plan → tasks → analyze → checklist → implement |

### 2.2 tasks.md 与 feature_list.json 结构差异

**spec-kit 的 tasks.md 示例**：
```markdown
## 第3阶段: 用户故事 1 - 创建和管理任务 (优先级: P1)
- [X] T024 [US1] 在 backend/app/models/task.py 中创建 Task SQLAlchemy 模型
- [X] T025 [US1] 在 backend/app/schemas/task.py 中创建 Task Pydantic 模式
- [ ] T028 [P] [US1] 在 backend/app/api/endpoints/tasks.py 中实现 GET /tasks 端点
```

**autonomous-coding 的 feature_list.json 示例**：
```json
{
  "category": "functional",
  "description": "用户可以创建新任务",
  "steps": [
    "Step 1: 导航到任务列表页面",
    "Step 2: 点击'新建任务'按钮",
    "Step 3: 输入任务标题和描述",
    "Step 4: 点击保存按钮",
    "Step 5: 验证任务出现在列表中"
  ],
  "passes": false
}
```

### 2.3 spec-kit 完整工作流阶段说明

> **重要**：spec-kit 包含 9 个命令，构成完整的规格驱动开发工作流。

| 阶段 | 命令 | 功能说明 | 是否必需 |
|-----|------|---------|--------|
| 1 | `/speckit.constitution` | 定义项目原则和非可协商规则 | ✅ 推荐 |
| 2 | `/speckit.specify` | 创建功能规格 + 自动创建 Git 分支 | ✅ 必需 |
| 3 | `/speckit.clarify` | 消除规格模糊点（最多 5 个问题） | 可选 |
| 4 | `/speckit.plan` | 制定技术计划、数据模型、API 契约 | ✅ 必需 |
| 5 | `/speckit.tasks` | 任务分解（按用户故事组织） | ✅ 必需 |
| 6 | `/speckit.analyze` | 跨工件一致性检查（非破坏性） | ✅ 推荐 |
| 7 | `/speckit.checklist` | 生成"需求质量检查清单" | 可选 |
| 8 | `/speckit.implement` | 执行实现（检查 checklist 后执行） | ✅ 必需 |
| 9 | `/speckit.taskstoissues` | 将任务转换为 GitHub Issues | 可选 |

### 2.4 spec-kit 核心理念："Unit Tests for English"

spec-kit 的 checklist 不是传统的验证测试，而是**需求质量的单元测试**：

```markdown
❌ WRONG（测试实现）：
- "Verify landing page displays 3 cards"
- "Test hover states work correctly"

✅ CORRECT（测试需求质量）：
- "Are the exact number and layout of cards specified?" [Completeness]
- "Is 'prominent display' quantified with sizing/positioning?" [Clarity]
- "Are hover state requirements consistent across elements?" [Consistency]
```

**核心思想**：如果规格是用英语写的"代码"，checklist 就是它的单元测试套件。

### 2.5 Constitution 权威性机制

Constitution 在 spec-kit 中具有**非可协商**的权威性：

- `speckit.analyze` 会严格验证 constitution 合规性
- `speckit.plan` 中有 "Constitution Check" 环节
- 违反 MUST 原则的问题自动标记为 **CRITICAL**
- Constitution 规则应注入到 autonomous-coding 的智能体提示词中

### 2.6 互补优势分析

```
┌─────────────────────────────────────────────────────────────────┐
│                         spec-kit 优势                            │
├─────────────────────────────────────────────────────────────────┤
│  • 规格驱动方法论                                                 │
│  • 用户故事组织                                                   │
│  • 精确文件路径                                                   │
│  • 并行任务标记 [P]                                               │
│  • TDD 结构化                                                    │
│  • Constitution 权威规则                                          │
│  • "Unit Tests for English" 需求质量检查                         │
│  • 跨工件一致性分析                                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   集成方案     │
                    └───────────────┘
                            ▲
                            │
┌───────────────────────────┴─────────────────────────────────────┐
│                    autonomous-coding 优势                        │
├─────────────────────────────────────────────────────────────────┤
│  • 多会话自主运行                                                 │
│  • 状态持久化                                                     │
│  • 沙箱安全机制                                                   │
│  • 浏览器自动化验证                                               │
│  • 进度可量化追踪                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、集成策略分析

### 3.1 三种策略对比

| 维度 | 策略A: 串联模式 | 策略B: 并行模式 | 策略C: 增强替换 |
|-----|---------------|---------------|---------------|
| **实现复杂度** | 中（需转换器） | 高（双向同步） | 低（改配置） |
| **信息保留度** | 高 ✅ | 高 | **低** ❌ |
| **灵活性** | 高 | 中 | 低 |
| **维护成本** | 低 | 高 | 低 |

### 3.2 策略A：串联模式（推荐）✅

```
┌─────────────────────────────────────────────────────────────────┐
│                     规格定义阶段（人工）                          │
├─────────────────────────────────────────────────────────────────┤
│  1. /speckit.constitution → (项目原则)                           │
│  2. /speckit.specify → (功能规格 + 自动创建 Git 分支)             │
│  3. /speckit.clarify → (消除模糊点，可选但推荐)                   │
│  4. /speckit.plan → (技术计划、数据模型、API 契约)                │
│  5. /speckit.tasks → (任务分解)                                  │
│  6. /speckit.analyze → (一致性检查，推荐)                        │
│  7. /speckit.checklist → (需求质量检查，可选)                    │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │      转换层（自动）     │
                    │  • pre_convert_       │
                    │    validator.py       │
                    │  • converter.py       │
                    │  • constitution_      │
                    │    injector.py        │
                    └───────────┬───────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   自主开发阶段（无人值守）                         │
├─────────────────────────────────────────────────────────────────┤
│  初始化智能体(含 Constitution) → 编码智能体循环(含 Checklist 参考)│
│  → 浏览器验证 → Constitution 合规检查 → 状态同步                 │
└─────────────────────────────────────────────────────────────────┘
```

**适用场景**：需要高质量规格定义 + 长时间自主开发

### 3.3 策略B：并行模式

两个系统同时运行，双向实时同步状态。

**问题**：
- 同步复杂度高，容易状态不一致
- 需要持续监控和修复同步问题

### 3.4 策略C：增强替换模式

用 spec-kit 的 `spec.md`/`plan.md` 替换 `app_spec.txt`，让 autonomous-coding 重新生成 `feature_list.json`。

**问题**：
- **信息损失**：tasks.md 的结构化信息（文件路径、并行标记、用户故事）会丢失
- **重复劳动**：spec-kit 已经做了任务分解，再让 AI 做一遍
- **可能不一致**：两次分解出的任务可能不同

### 3.5 推荐策略A的理由

1. **信息保留**：通过转换器，tasks.md 的结构信息可以嵌入 feature_list.json
2. **分工明确**：spec-kit 负责"规格驱动"，autonomous-coding 负责"自主执行"
3. **可追溯**：每个 feature 都有 `source_task_id` 回溯到原始任务

---

## 四、推荐方案：串联模式详细设计

### 4.1 整体架构

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   人工阶段       │     │    转换层        │     │   自主运行阶段   │
│                 │     │                 │     │                 │
│ 1. constitution │     │ 读取 tasks.md   │     │ 初始化智能体     │
│ 2. specify      │ ──▶ │ 解析任务结构     │ ──▶ │ 读取 feature_   │
│ 3. plan         │     │ 生成测试步骤     │     │   list.json    │
│ 4. tasks        │     │ 输出 JSON       │     │ 实现 → 验证      │
│                 │     │                 │     │ 更新 → 同步      │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │   同步层         │
                                               │ 回写 tasks.md   │
                                               └─────────────────┘
```

### 4.2 转换规则

| tasks.md 元素 | feature_list.json 映射 |
|--------------|----------------------|
| 用户故事标题 | `description` 的上下文 |
| `[US1]` 标签 | `user_story` 字段 |
| 任务描述 | 转换为多个验证步骤 |
| `[X]` 完成标记 | `"passes": true` |
| `[ ]` 未完成标记 | `"passes": false` |
| `[P]` 并行标记 | `is_parallel` 字段 |
| 文件路径 | `file_path` 字段 |

### 4.3 转换后的 feature_list.json 结构（增强版）

```json
{
  "category": "functional",
  "description": "[T024] [US1] 在 backend/app/models/task.py 中创建 Task SQLAlchemy 模型",
  "steps": [
    "Step 1: 验证模型文件语法正确",
    "Step 2: 运行数据库迁移",
    "Step 3: 验证表结构创建成功",
    "Step 4: 测试基本 CRUD 操作"
  ],
  "passes": false,
  
  // 基础元数据
  "source_task_id": "T024",
  "user_story": "创建和管理任务",
  "file_path": "backend/app/models/task.py",
  "is_parallel": false,
  
  // 新增：Phase 信息
  "phase": "User Story 1",
  "phase_number": 3,
  "priority": "P1",
  
  // 新增：MVP 和独立测试信息
  "is_mvp": true,
  "independent_test": "验证任务表已创建且可 CRUD",
  
  // 新增：Constitution 规则引用
  "constitution_rules": ["TDD mandatory", "Integration testing required"],
  
  // 新增：Checklist 引用
  "checklist_refs": ["CHK012", "CHK015"]
}
```

> **注意**：增强版结构保留了更多 speckit 的元数据，便于追溯和质量管控。

---

## 五、项目目录结构

```
project/
├── .specify/
│   ├── memory/
│   │   └── constitution.md      # 项目原则（非可协商）
│   ├── scripts/bash/            # speckit 依赖的脚本
│   │   ├── create-new-feature.sh
│   │   ├── check-prerequisites.sh
│   │   ├── setup-plan.sh
│   │   └── update-agent-context.sh
│   └── templates/               # 模板文件
├── specs/
│   └── 001-todo-app/
│       ├── spec.md              # spec-kit: 功能规格
│       ├── plan.md              # spec-kit: 实现计划
│       ├── tasks.md             # spec-kit: 任务清单（主数据）
│       ├── research.md          # spec-kit: 技术调研
│       ├── data-model.md        # spec-kit: 数据模型
│       ├── contracts/           # spec-kit: API 契约
│       └── checklists/          # spec-kit: 需求质量检查清单
│           ├── ux.md
│           ├── api.md
│           └── security.md
├── speckit_integration/
│   ├── converter.py             # 转换器脚本
│   ├── sync_status.py           # 状态同步脚本
│   ├── pre_convert_validator.py # 预转换验证器（新增）
│   ├── constitution_injector.py # 原则注入器（新增）
│   ├── initializer_prompt_speckit.md  # 初始化智能体提示词
│   └── coding_prompt_speckit.md       # 编码智能体提示词
├── feature_list.json            # autonomous-coding: 派生的测试清单
├── claude-progress.txt          # autonomous-coding: 进度笔记
├── init.sh                      # 环境初始化脚本
├── backend/
│   └── ...
└── frontend/
    └── ...
```

---

## 六、使用指南

### 6.1 前置条件

- Python 3.10+
- 已安装 spec-kit CLI (`uv tool install specify-cli`)
- 已配置 ANTHROPIC_API_KEY

### 6.2 步骤 1：用 spec-kit 生成规格

在 Claude Code 中运行：

```bash
# 建立项目原则
/speckit.constitution Create principles focused on code quality...

# 定义功能规格
/speckit.specify Build a todo app that allows users to create, edit, delete tasks...

# 制定技术计划
/speckit.plan Use FastAPI backend, React frontend, SQLite database...

# 分解任务清单
/speckit.tasks
```

产出：`specs/001-todo-app/tasks.md`

### 6.3 步骤 2：运行转换器

```bash
# 将 tasks.md 转换为 feature_list.json
python speckit_integration/converter.py \
    specs/001-todo-app/tasks.md \
    feature_list.json

# 验证输出
python -c "
import json
with open('feature_list.json') as f:
    features = json.load(f)
print(f'Total features: {len(features)}')
print(f'Passing: {sum(1 for f in features if f[\"passes\"])}')
print(f'Remaining: {sum(1 for f in features if not f[\"passes\"])}')
"
```

### 6.4 步骤 3：运行自主开发

```bash
# 设置 API 密钥
export ANTHROPIC_API_KEY='your-key'

# 启动自主开发循环
python autonomous_agent_demo.py \
    --project-dir ./project \
    --initializer-prompt speckit_integration/initializer_prompt_speckit.md \
    --coding-prompt speckit_integration/coding_prompt_speckit.md
```

### 6.5 步骤 4：状态同步

自主开发完成后，同步状态回 tasks.md：

```bash
python speckit_integration/sync_status.py \
    feature_list.json \
    specs/001-todo-app/tasks.md
```

---

## 七、工具参考

### 7.1 converter.py

**功能**：将 spec-kit 的 tasks.md 转换为 autonomous-coding 的 feature_list.json

**用法**：
```bash
python converter.py <tasks_md_path> [output_json_path]
```

**特性**：
- 解析任务结构（ID、完成状态、并行标记、用户故事标签）
- 提取文件路径
- 根据任务类型生成 E2E 测试步骤
- 分类任务（functional/style）
- 保留元信息用于追溯和同步

### 7.2 sync_status.py

**功能**：将 feature_list.json 的完成状态回写到 tasks.md

**用法**：
```bash
python sync_status.py <feature_list_json> <tasks_md_path>
```

**特性**：
- 读取 feature_list.json 中的 `passes` 和 `source_task_id`
- 更新 tasks.md 中对应任务的 `[X]`/`[ ]` 标记
- 添加更新时间戳

### 7.3 initializer_prompt_speckit.md

初始化智能体提示词，指导智能体：
1. 读取 spec-kit 生成的规格文件
2. 运行转换器
3. 创建项目结构和 init.sh
4. 初始化 Git

### 7.4 coding_prompt_speckit.md

编码智能体提示词，指导智能体：
1. 读取项目状态
2. 运行验证测试
3. 按 TDD 方式实现功能
4. 用浏览器验证
5. 更新 feature_list.json
6. 同步状态到 tasks.md
7. 提交代码

---

## 八、后续优化建议

### 8.1 P0：立即实施（文档优化）

1. ✅ **补充完整工作流阶段**：已在本文档中更新
2. ✅ **说明 Constitution 权威性**：已添加相关章节
3. ✅ **增强 feature_list.json 结构**：已添加新字段说明

### 8.2 P1：优先实施（转换器增强）

1. **增强 converter.py**：
   - 保留 Phase/MVP/独立测试等元数据
   - 关联 checklist 引用
   - 提取 constitution 规则

2. **新增 constitution_injector.py**：
   - 读取 `.specify/memory/constitution.md`
   - 提取 MUST/SHOULD 规则
   - 注入到智能体提示词

3. **更新智能体提示词**：
   - 添加 Constitution 合规检查环节
   - 添加 Checklist 参考机制

### 8.3 P2：中期实施（质量门控）

1. **新增 pre_convert_validator.py**：
   - 转换前检查 analyze 报告
   - 如有 CRITICAL 问题则阻止转换
   - 检查 checklist 完成状态

2. **Checklist 机制复用**：
   - 为每个 feature 关联 checklist 项
   - 作为额外质量门控

3. **PR 生成**：每个用户故事完成后自动创建 Pull Request
4. **测试报告**：生成测试覆盖率和验证截图报告

### 8.4 P3：长期实施（高级功能）

1. **多 Agent 协作**：不同用户故事分配给不同 Agent 并行开发
2. **智能调度**：根据任务依赖自动调度最优执行顺序
3. **自愈机制**：自动检测和修复回归问题
4. **Web Dashboard**：可视化进度追踪界面
5. **脚本集成**：考虑移植 speckit bash 脚本功能到 Python

---

## 附录：测试结果

使用 `specs/001-todo-app/tasks.md` 测试转换器：

```
✅ 转换完成!
   输入: specs/001-todo-app/tasks.md
   输出: feature_list.json
   总任务数: 97
   已完成: 70
   待完成: 27
```

---

*本方案由 autonomous-coding × spec-kit 集成分析生成*
*最后更新: 2025-12-16*
*基于 speckit 完整工作流（9 个命令）深度分析后优化*
