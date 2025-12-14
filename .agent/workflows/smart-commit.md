---
description: 智能Git提交 - 自动生成提交说明并推送到远端
---

# Smart Commit - 智能Git提交命令

自动分析当前更改，生成符合规范的提交信息，执行提交并推送到远程仓库。

## 支持的参数
- 无参数：自动分析所有更改并提交推送
- `--dry-run`：预览提交信息但不实际提交
- `--no-push`：只提交不推送
- `--message "custom message"`：使用自定义提交信息

## 执行步骤

### 1. 环境检查
首先检查Git配置和SSH认证状态：
```bash
git config --get user.name
git config --get user.email
git remote -v
```

### 2. 分析当前更改
分析工作区状态和具体更改内容：
```bash
git status
git diff --stat
git diff
```

### 3. 智能分析更改类型
根据以下规则识别提交类型：

**文件类型识别**：
- `.md` 文件 → `docs` 或 `content` 类型
- `.py, .js, .ts` 等源码 → `feat` 或 `fix` 类型
- `package.json, requirements.txt` → `chore` 类型
- 测试文件 → `test` 类型

**更改模式识别**：
- 新增文件较多 → `feat` 类型
- 主要是删除 → `refactor` 或 `chore` 类型
- 修改现有功能 → `fix` 或 `update` 类型
- 配置文件更改 → `chore` 类型

**提交类型说明**：
- `feat`: 新功能、新文件
- `fix`: 修复bug、错误修正
- `docs`: 文档更新、README修改
- `style`: 格式调整、代码风格
- `refactor`: 重构代码
- `test`: 测试相关
- `chore`: 配置、构建相关
- `update`: 更新内容、数据变更

### 4. 生成提交信息
按照以下格式生成提交信息：

```
<type>(<scope>): <description>

<body>

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

其中：
- `<type>`：提交类型（见上述分类）
- `<scope>`：影响范围（如模块名、组件名）
- `<description>`：简短描述（中英文均可）
- `<body>`：详细说明（可选，重要更改时添加）

### 5. 执行提交
添加所有更改到暂存区并提交：
```bash
git add -A
git commit -m "<生成的提交信息>"
```

### 6. 推送到远程仓库
除非指定 `--no-push`，否则推送到远程：
```bash
git push
```

如果是首次推送或上游分支未设置：
```bash
git push --set-upstream origin <当前分支名>
```

## 安全检查

在执行提交前，自动检查以下内容：

1. **敏感文件过滤**：确保以下文件不被提交
   - `.env*` 文件
   - `*.key`, `*.pem` 密钥文件
   - 其他敏感配置

2. **确认文件列表**：显示将要提交的文件供确认

3. **远程仓库验证**：确认推送目标仓库地址

## SSH认证处理

如果推送时遇到认证问题：

1. 检查SSH密钥是否存在：
```bash
ls ~/.ssh/id_rsa.pub
```

2. 如果不存在，提示用户生成SSH密钥：
```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

3. 提示用户将公钥添加到GitHub/GitLab等平台

## 错误处理

- **合并冲突**：暂停并提示用户手动解决冲突
- **推送失败**：
  - 检查是否需要先 pull
  - 验证远程仓库权限
  - 提供具体的解决建议
- **无更改**：提示没有需要提交的内容

## 自定义配置

可以在项目根目录创建 `.claude-commit-config.json` 进行个性化配置：

```json
{
  "defaultBranch": "main",
  "commitPrefix": "",
  "pushByDefault": true,
  "excludePatterns": [".env*", "*.key", "*.pem"],
  "customRules": {
    "系统配置": "chore",
    "文档更新": "docs",
    "功能实现": "feat"
  }
}
```

## 使用示例

基本使用（自动分析并提交推送）：
```
/smart-commit
```

预览模式（查看将生成的提交信息）：
```
/smart-commit --dry-run
```

只提交不推送：
```
/smart-commit --no-push
```

使用自定义提交消息：
```
/smart-commit --message "feat(ai): 新增智能提交命令功能"
```
