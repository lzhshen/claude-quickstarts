#!/usr/bin/env python3
"""
状态同步脚本：feature_list.json → tasks.md 回写

当 autonomous-coding 完成任务后，同步更新 spec-kit 的 tasks.md 文件

用法:
    python sync_status.py <feature_list_json> <tasks_md_path>

示例:
    python sync_status.py feature_list.json specs/001-todo-app/tasks.md
"""

import re
import json
import sys
from pathlib import Path
from datetime import datetime


def load_feature_list(json_path: Path) -> dict[str, bool]:
    """加载 feature_list.json，返回 task_id -> passes 映射"""
    with open(json_path, 'r', encoding='utf-8') as f:
        features = json.load(f)
    
    return {
        f['source_task_id']: f['passes']
        for f in features
        if 'source_task_id' in f
    }


def sync_to_tasks_md(tasks_md_path: Path, status_map: dict[str, bool]) -> tuple[int, list[str]]:
    """
    将状态更新同步到 tasks.md
    
    返回: (更新数量, 更新的任务ID列表)
    """
    content = tasks_md_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    updated_tasks = []
    
    for i, line in enumerate(lines):
        # 匹配任务行: - [X] T001 或 - [ ] T001
        match = re.match(r'^(-\s*\[)([ Xx])(\]\s*)(T\d+)(.*)$', line)
        if not match:
            continue
        
        prefix = match.group(1)      # "- ["
        current_status = match.group(2)  # " " 或 "X"
        bracket = match.group(3)     # "] "
        task_id = match.group(4)     # "T001"
        rest = match.group(5)        # 剩余部分
        
        if task_id not in status_map:
            continue
        
        new_passes = status_map[task_id]
        new_status = 'X' if new_passes else ' '
        
        # 只有状态变化时才更新
        if current_status.upper() != new_status:
            lines[i] = f"{prefix}{new_status}{bracket}{task_id}{rest}"
            updated_tasks.append(task_id)
    
    if updated_tasks:
        # 添加更新时间戳（如果文件头有状态更新行）
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        for i, line in enumerate(lines):
            if line.startswith('**状态更新**:'):
                lines[i] = f"**状态更新**: {timestamp} - 同步自 feature_list.json"
                break
        
        # 写回文件
        tasks_md_path.write_text('\n'.join(lines), encoding='utf-8')
    
    return len(updated_tasks), updated_tasks


def main():
    """命令行入口"""
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    feature_list_path = Path(sys.argv[1])
    tasks_md_path = Path(sys.argv[2])
    
    if not feature_list_path.exists():
        print(f"错误: 找不到文件 {feature_list_path}")
        sys.exit(1)
    
    if not tasks_md_path.exists():
        print(f"错误: 找不到文件 {tasks_md_path}")
        sys.exit(1)
    
    status_map = load_feature_list(feature_list_path)
    count, updated_ids = sync_to_tasks_md(tasks_md_path, status_map)
    
    if count > 0:
        print(f"✅ 同步完成! 更新了 {count} 个任务:")
        for task_id in updated_ids:
            print(f"   - {task_id}")
    else:
        print("ℹ️ 没有需要同步的更新")


if __name__ == '__main__':
    main()
