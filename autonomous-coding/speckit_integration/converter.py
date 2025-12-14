#!/usr/bin/env python3
"""
spec-kit tasks.md → autonomous-coding feature_list.json 转换器

用法:
    python converter.py <tasks_md_path> [output_json_path]

示例:
    python converter.py specs/001-todo-app/tasks.md feature_list.json
"""

import re
import json
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Feature:
    """feature_list.json 中的单个功能项"""
    category: str
    description: str
    steps: list[str]
    passes: bool
    # 扩展字段（用于追溯和同步）
    source_task_id: str
    user_story: str
    file_path: Optional[str] = None
    is_parallel: bool = False


def parse_tasks_md(content: str) -> list[Feature]:
    """解析 spec-kit 的 tasks.md 文件内容"""
    features = []
    current_story = ""
    current_phase = ""
    
    lines = content.split('\n')
    
    for line in lines:
        # 解析阶段标题
        phase_match = re.match(r'^## 第\d+阶段[:：]\s*(.+)', line)
        if phase_match:
            current_phase = phase_match.group(1).strip()
            # 提取用户故事（如果有）
            story_match = re.search(r'用户故事\s*\d+\s*[-–]\s*(.+?)(?:\s*\(|$)', current_phase)
            if story_match:
                current_story = story_match.group(1).strip()
            else:
                current_story = current_phase
            continue
        
        # 解析任务行
        # 格式: - [X] T001 [P] [US1] 任务描述
        task_match = re.match(
            r'^-\s*\[([ Xx/])\]\s*(T\d+)\s*'       # 完成状态和任务ID
            r'(?:\[P\]\s*)?'                       # 可选的并行标记
            r'(?:\[(US\d+)\]\s*)?'                 # 可选的用户故事标签
            r'(.+)$',                              # 任务描述
            line
        )
        
        if task_match:
            status = task_match.group(1).upper()
            task_id = task_match.group(2)
            us_tag = task_match.group(3) or ''
            description = task_match.group(4).strip()
            
            # 检查是否有并行标记
            is_parallel = '[P]' in line
            
            # 提取文件路径（如果有）
            file_path = extract_file_path(description)
            
            # 生成测试步骤
            steps = generate_test_steps(description, current_story, file_path)
            
            # 分类任务
            category = categorize_task(description)
            
            features.append(Feature(
                category=category,
                description=f"[{task_id}] {description}",
                steps=steps,
                passes=(status == 'X'),
                source_task_id=task_id,
                user_story=current_story if us_tag else current_phase,
                file_path=file_path,
                is_parallel=is_parallel
            ))
    
    return features


def extract_file_path(description: str) -> Optional[str]:
    """从任务描述中提取文件路径"""
    # 匹配 "在 xxx/yyy.py 中" 或 "xxx/yyy.py"
    patterns = [
        r'在\s+([a-zA-Z0-9_/.-]+\.[a-zA-Z]+)\s+中',
        r'([a-zA-Z0-9_/.-]+\.[a-zA-Z]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, description)
        if match:
            return match.group(1)
    
    return None


def generate_test_steps(description: str, story_context: str, file_path: Optional[str]) -> list[str]:
    """根据任务描述生成 E2E 测试步骤"""
    desc_lower = description.lower()
    steps = []
    
    # 测试类任务
    if '测试' in description or 'test' in desc_lower:
        if 'contract' in desc_lower or '契约' in description:
            steps = [
                "Step 1: 确保后端服务已启动",
                "Step 2: 运行契约测试命令",
                "Step 3: 验证所有测试用例通过",
                "Step 4: 检查测试覆盖率报告"
            ]
        elif 'integration' in desc_lower or '集成' in description:
            steps = [
                "Step 1: 准备测试数据库环境",
                "Step 2: 运行集成测试",
                "Step 3: 验证端到端流程正确",
                "Step 4: 清理测试数据"
            ]
        elif 'react' in desc_lower or '组件' in description:
            steps = [
                "Step 1: 运行前端组件测试",
                "Step 2: 验证组件渲染正确",
                "Step 3: 验证交互行为符合预期",
                "Step 4: 检查无控制台错误"
            ]
        else:
            steps = [
                "Step 1: 运行相关测试命令",
                "Step 2: 验证测试通过",
                "Step 3: 检查测试输出日志"
            ]
    
    # 后端 API 任务
    elif 'backend' in desc_lower or 'endpoint' in desc_lower or '端点' in description:
        if 'GET' in description:
            steps = [
                "Step 1: 启动后端开发服务器",
                "Step 2: 发送 GET 请求到端点",
                "Step 3: 验证响应状态码为 200",
                "Step 4: 验证响应数据结构正确",
                "Step 5: 在浏览器中验证 API 可用"
            ]
        elif 'POST' in description:
            steps = [
                "Step 1: 启动后端开发服务器",
                "Step 2: 准备有效的请求体",
                "Step 3: 发送 POST 请求",
                "Step 4: 验证响应状态码为 201",
                "Step 5: 验证资源已正确创建"
            ]
        elif 'PUT' in description or 'PATCH' in description:
            steps = [
                "Step 1: 确保目标资源存在",
                "Step 2: 发送更新请求",
                "Step 3: 验证响应包含更新后的数据",
                "Step 4: 验证数据库中数据已更新"
            ]
        elif 'DELETE' in description:
            steps = [
                "Step 1: 确保目标资源存在",
                "Step 2: 发送删除请求",
                "Step 3: 验证响应状态码为 200 或 204",
                "Step 4: 验证资源已从数据库删除"
            ]
        else:
            steps = [
                "Step 1: 启动后端服务器",
                "Step 2: 验证 API 端点可访问",
                "Step 3: 测试正常请求场景",
                "Step 4: 测试错误处理场景"
            ]
    
    # 前端 UI 任务
    elif 'frontend' in desc_lower or 'component' in desc_lower or '组件' in description:
        component_name = extract_component_name(description)
        steps = [
            "Step 1: 启动前端开发服务器",
            "Step 2: 导航到包含该组件的页面",
            f"Step 3: 验证 {component_name} 组件渲染正确",
            "Step 4: 截图验证 UI 外观",
            "Step 5: 验证无控制台错误"
        ]
        
        if 'form' in desc_lower or '表单' in description:
            steps.extend([
                "Step 6: 填写表单字段",
                "Step 7: 提交表单并验证反馈",
                "Step 8: 验证表单验证规则生效"
            ])
        
        if 'list' in desc_lower or '列表' in description:
            steps.extend([
                "Step 6: 验证列表正确显示数据",
                "Step 7: 测试列表项的交互功能"
            ])
    
    # 样式任务
    elif 'tailwind' in desc_lower or 'css' in desc_lower or '样式' in description:
        steps = [
            "Step 1: 启动前端开发服务器",
            "Step 2: 导航到目标页面",
            "Step 3: 截图验证样式效果",
            "Step 4: 验证响应式布局",
            "Step 5: 验证颜色和间距符合设计"
        ]
    
    # 数据库/模型任务
    elif 'model' in desc_lower or '模型' in description or 'schema' in desc_lower:
        steps = [
            "Step 1: 验证模型文件语法正确",
            "Step 2: 运行数据库迁移",
            "Step 3: 验证表结构创建成功",
            "Step 4: 测试基本 CRUD 操作"
        ]
    
    # 配置/初始化任务
    elif '配置' in description or 'config' in desc_lower or '初始化' in description:
        steps = [
            "Step 1: 验证配置文件存在且语法正确",
            "Step 2: 启动相关服务验证配置生效",
            "Step 3: 验证环境变量正确加载"
        ]
    
    # 默认步骤
    else:
        steps = [
            f"Step 1: 验证代码文件 {file_path or '相关文件'} 存在",
            "Step 2: 运行相关测试",
            "Step 3: 验证功能正常工作"
        ]
    
    return steps


def extract_component_name(description: str) -> str:
    """从描述中提取组件名称"""
    # 匹配 "TaskForm 组件" 或 "TaskForm component"
    match = re.search(r'(\w+)\s*(?:组件|component)', description, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # 匹配文件名中的组件名
    match = re.search(r'/(\w+)/\1\.tsx', description)
    if match:
        return match.group(1)
    
    return "该"


def categorize_task(description: str) -> str:
    """分类任务为 functional 或 style"""
    style_keywords = [
        '样式', 'style', 'CSS', 'Tailwind', '颜色', '布局',
        '暖色', '视觉', 'UI', '主题', 'theme', '动画', 'animation'
    ]
    
    for keyword in style_keywords:
        if keyword.lower() in description.lower():
            return "style"
    
    return "functional"


def features_to_json(features: list[Feature]) -> str:
    """将 Feature 列表转换为 JSON 字符串"""
    # 转换为字典列表，保留扩展字段
    data = [asdict(f) for f in features]
    return json.dumps(data, indent=2, ensure_ascii=False)


def convert_tasks_to_features(tasks_md_path: Path, output_path: Path) -> tuple[int, int]:
    """
    主转换函数
    
    返回: (总任务数, 已完成任务数)
    """
    content = tasks_md_path.read_text(encoding='utf-8')
    features = parse_tasks_md(content)
    
    # 按用户故事排序，优先级高的在前
    features.sort(key=lambda f: (
        '1' if 'P1' in f.user_story else (
            '2' if 'P2' in f.user_story else (
                '3' if 'P3' in f.user_story else '9'
            )
        ),
        f.source_task_id
    ))
    
    # 写入 JSON
    json_content = features_to_json(features)
    output_path.write_text(json_content, encoding='utf-8')
    
    total = len(features)
    passed = sum(1 for f in features if f.passes)
    
    return total, passed


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    tasks_md_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('feature_list.json')
    
    if not tasks_md_path.exists():
        print(f"错误: 找不到文件 {tasks_md_path}")
        sys.exit(1)
    
    total, passed = convert_tasks_to_features(tasks_md_path, output_path)
    
    print(f"✅ 转换完成!")
    print(f"   输入: {tasks_md_path}")
    print(f"   输出: {output_path}")
    print(f"   总任务数: {total}")
    print(f"   已完成: {passed}")
    print(f"   待完成: {total - passed}")


if __name__ == '__main__':
    main()
