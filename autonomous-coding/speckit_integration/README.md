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
| **工作流阶段** | 初始化 → 编码（双智能体） | constitution → specify → plan → tasks → implement |

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

### 2.3 互补优势分析

```
┌─────────────────────────────────────────────────────────────────┐
│                         spec-kit 优势                            │
├─────────────────────────────────────────────────────────────────┤
│  • 规格驱动方法论                                                 │
│  • 用户故事组织                                                   │
│  • 精确文件路径                                                   │
│  • 并行任务标记 [P]                                               │
│  • TDD 结构化                                                    │
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
│  /speckit.constitution → /speckit.specify → /speckit.plan       │
│                           → /speckit.tasks                       │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │      转换层（自动）     │
                    │  tasks.md → feature_  │
                    │    list.json 转换器   │
                    └───────────┬───────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   自主开发阶段（无人值守）                         │
├─────────────────────────────────────────────────────────────────┤
│  初始化智能体 → 编码智能体循环 → 浏览器验证 → 状态同步            │
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

### 4.3 转换后的 feature_list.json 结构

```json
{
  "category": "functional",
  "description": "[T024] 在 backend/app/models/task.py 中创建 Task SQLAlchemy 模型",
  "steps": [
    "Step 1: 验证模型文件语法正确",
    "Step 2: 运行数据库迁移",
    "Step 3: 验证表结构创建成功",
    "Step 4: 测试基本 CRUD 操作"
  ],
  "passes": true,
  "source_task_id": "T024",
  "user_story": "创建和管理任务",
  "file_path": "backend/app/models/task.py",
  "is_parallel": false
}
```

---

## 五、项目目录结构

```
project/
├── specs/
│   └── 001-todo-app/
│       ├── spec.md              # spec-kit: 功能规格
│       ├── plan.md              # spec-kit: 实现计划
│       ├── tasks.md             # spec-kit: 任务清单（主数据）
│       ├── research.md          # spec-kit: 技术调研
│       └── data-model.md        # spec-kit: 数据模型
├── speckit_integration/
│   ├── converter.py             # 转换器脚本
│   ├── sync_status.py           # 状态同步脚本
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

### 8.1 短期优化

1. **集成到 `agent.py`**：自动检测 specs/ 目录并使用 spec-kit 模式
2. **实时同步**：在每次 feature 完成后自动同步，无需手动运行

### 8.2 中期优化

1. **PR 生成**：每个用户故事完成后自动创建 Pull Request
2. **测试报告**：生成测试覆盖率和验证截图报告
3. **Web Dashboard**：可视化进度追踪界面

### 8.3 长期优化

1. **多 Agent 协作**：不同用户故事分配给不同 Agent 并行开发
2. **智能调度**：根据任务依赖自动调度最优执行顺序
3. **自愈机制**：自动检测和修复回归问题

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
*最后更新: 2025-12-15*
