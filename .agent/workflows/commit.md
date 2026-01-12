---
description: Git 提交規範，採用 Conventional Commits 格式
---

# Git 提交規範

本專案採用 [Conventional Commits](https://www.conventionalcommits.org/) 規範。

## 提交訊息格式

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### 基本格式範例

```
feat(update): 新增自動更新功能
fix(excel): 修復讀取合併儲存格的問題
docs(readme): 更新安裝說明
```

## 提交類型 (Type)

| 類型 | 說明 | 範例 |
|------|------|------|
| `feat` | 新功能 | `feat: 新增律師選擇對話框` |
| `fix` | 修復 bug | `fix: 修復金額計算錯誤` |
| `docs` | 文件更新 | `docs: 更新 README` |
| `style` | 程式碼風格（不影響邏輯） | `style: 格式化程式碼` |
| `refactor` | 重構（不新增功能或修復 bug） | `refactor: 重構服務層架構` |
| `perf` | 效能優化 | `perf: 優化 Excel 讀取速度` |
| `test` | 測試相關 | `test: 新增單元測試` |
| `build` | 建置系統或外部依賴 | `build: 更新 PyInstaller 配置` |
| `ci` | CI/CD 配置 | `ci: 新增 GitHub Actions` |
| `chore` | 其他維護工作 | `chore: 更新 .gitignore` |

## 範圍 (Scope) - 選填

常用範圍（依專案結構）：
- `ui` - 使用者介面
- `excel` - Excel 處理相關
- `update` - 自動更新功能
- `db` - 資料庫相關
- `service` - 服務層

## 提交訊息範例

### 好的範例 ✅

```
feat(ui): 新增明細分帳頁面的進度條

- 顯示處理進度百分比
- 支援取消操作
```

```
fix(excel): 修復讀取空白列時的錯誤

修復當 Excel 檔案包含空白列時會拋出 IndexError 的問題。
現在會自動跳過空白列繼續處理。

Fixes #42
```

### 不好的範例 ❌

```
update                     # 太模糊
fix bug                    # 沒有說明修復了什麼
WIP                        # 不應提交未完成的工作
修改 app.py               # 只描述了改動的檔案，沒有說明目的
```

## 何時應該提交

- ✅ 完成一個功能或功能的子部分
- ✅ 修復一個 bug
- ✅ 完成一段重構
- ✅ 更新文件
- ❌ 程式碼無法編譯
- ❌ 測試失敗
- ❌ 只完成一半的功能

## 使用命令

```powershell
# 基本提交
git commit -m "feat: 新增功能描述"

# 帶有詳細說明的提交
git commit -m "fix(excel): 修復問題標題" -m "詳細說明問題原因和解決方案"
```
