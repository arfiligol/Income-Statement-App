---
description: Git 開發工作流程總覽，說明在開發過程中如何使用 git 進行版本控制
---

# Git 開發工作流程

本文件說明在開發過程中使用 Git 的標準流程。

## 開發前：狀態檢查

在開始任何開發工作之前，先確認 git 狀態：

```powershell
# 1. 確認當前分支
git branch

# 2. 檢查是否有未提交的變更
git status

# 3. 確認與遠端同步狀態
git fetch origin
git log --oneline -5
```

### 如果有未提交的變更

決定如何處理：
- **繼續開發**：直接開始工作
- **儲存起來**：`git stash` 暫存變更
- **提交它**：使用 [commit workflow](/commit) 提交

## 開發中：增量提交

遵循「小步快跑」原則，頻繁提交：

1. **完成一個邏輯單元**（一個功能、一個修復）
2. **檢查變更**：`git diff`
3. **暫存變更**：`git add <files>` 或 `git add -p`
4. **提交**：遵循 [commit 規範](/commit)

### 建議的提交時機

- ✅ 新增一個完整功能
- ✅ 修復一個 bug
- ✅ 重構一段程式碼（不改變行為）
- ✅ 更新文件
- ❌ 程式碼處於不可編譯狀態
- ❌ 測試失敗

## 功能完成後：整理與推送

```powershell
# 1. 確認所有變更已提交
git status

# 2. 檢查提交歷史
git log --oneline -10

# 3. 推送到遠端
git push origin <branch-name>
```

## 常用命令速查

| 情境 | 命令 |
|------|------|
| 查看狀態 | `git status` |
| 查看差異 | `git diff` |
| 暫存檔案 | `git add <file>` |
| 暫存所有 | `git add .` |
| 提交 | `git commit -m "type: message"` |
| 查看歷史 | `git log --oneline -n 10` |
| 暫存變更 | `git stash` |
| 恢復暫存 | `git stash pop` |
| 同步遠端 | `git pull --rebase` |
| 推送 | `git push origin <branch>` |

## 注意事項

> [!WARNING]
> **禁止直接 force push 到 main 分支**
> 如果需要重寫歷史，請先與團隊討論

> [!TIP]
> 使用 `git add -p` 可以互動式選擇要暫存的變更區塊，避免將不相關的變更混入同一個提交
