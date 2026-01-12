---
description: Git 分支管理策略與命名規範
---

# Git 分支管理

本文件說明專案的分支管理策略和命名規範。

## 主要分支

| 分支 | 用途 | 保護規則 |
|------|------|----------|
| `main` | 正式發布版本 | 禁止直接推送 |
| `develop` | 開發整合分支（如有使用） | - |

## 分支命名規範

### 格式

```
<type>/<short-description>
```

### 類型對照

| 類型 | 用途 | 範例 |
|------|------|------|
| `feature/` | 新功能開發 | `feature/auto-update` |
| `fix/` | Bug 修復 | `fix/excel-merge-cell` |
| `hotfix/` | 緊急修復（直接修正 main） | `hotfix/critical-crash` |
| `refactor/` | 重構工作 | `refactor/service-layer` |
| `docs/` | 文件更新 | `docs/readme-update` |
| `release/` | 發布準備 | `release/v0.2.0` |

### 命名規則

- ✅ 使用小寫字母
- ✅ 使用連字號 `-` 分隔單字
- ✅ 簡短但具描述性
- ❌ 不要使用空格或底線
- ❌ 不要使用中文

## 工作流程

### 開發新功能

```powershell
# 1. 從 main 建立功能分支
git checkout main
git pull origin main
git checkout -b feature/my-feature

# 2. 開發並提交
git add .
git commit -m "feat: 實作功能"

# 3. 推送到遠端
git push origin feature/my-feature

# 4. 建立 Pull Request 合併到 main
```

### 修復 Bug

```powershell
# 1. 從 main 建立修復分支
git checkout main
git pull origin main
git checkout -b fix/bug-description

# 2. 修復並提交
git add .
git commit -m "fix: 修復問題描述"

# 3. 推送並建立 PR
git push origin fix/bug-description
```

## 分支合併策略

| 情境 | 建議策略 |
|------|----------|
| 功能分支 → main | Squash and merge（合併為單一提交） |
| 修復分支 → main | Squash and merge |
| Release 分支 → main | Merge commit（保留完整歷史） |

## 分支清理

定期清理已合併的本地分支：

```powershell
# 刪除已合併的本地分支
git branch --merged main | Select-String -NotMatch "main" | ForEach-Object { git branch -d $_.Line.Trim() }

# 清理已刪除的遠端分支追蹤
git fetch --prune
```

## 注意事項

> [!CAUTION]
> 永遠不要使用 `git push --force` 到 `main` 分支

> [!TIP]
> 保持分支生命週期短暫，儘快合併回主分支以減少合併衝突
