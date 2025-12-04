# PowerShell Allow List Terminal Commands

這個文件定義了可以在 PowerShell 中自動執行的安全命令列表。

## PowerShell 匹配規則

允許列表條目的 tokens 可以匹配命令 tokens 的**任何連續子序列**。

---

## 文件系統查看命令 (唯讀)

```powershell
Get-ChildItem
Get-Content
Get-Location
Test-Path
Resolve-Path
```

## 版本和幫助資訊

```powershell
python --version
python -V
node --version
npm --version
uv --version
git --version
pip --version
poetry --version
dotnet --version
--help
-h
Get-Help
Get-Command
```

## 套件管理器 - 唯讀操作

```powershell
pip list
pip show
pip freeze
npm list
npm ls
uv pip list
uv pip show
poetry show
poetry env info
dotnet list package
```

## 套件管理器 - 安裝和同步 (專案範圍)

```powershell
uv sync
uv pip install
npm install
npm ci
pip install
poetry install
dotnet restore
```

## 專案運行和測試

```powershell
uv run
npm run
npm run dev
npm run start
npm run build
npm test
pytest
pytest -v
python -m pytest
poetry run
dotnet run
dotnet test
dotnet build
```

## Git 唯讀操作

```powershell
git status
git log
git log -n
git diff
git show
git branch
git branch -a
git remote -v
git ls-files
git ls-tree
git config --list
git config --get
```

## 搜尋和尋找

```powershell
Select-String
Where-Object
Find-Object
fd
rg
```

## Python 運行

```powershell
python -m
python -c
uv run python
poetry run python
```

## 環境變數查看

```powershell
Get-ChildItem Env:
$env:PATH
$env:PYTHON_VERSION
```

## 其他安全命令

```powershell
Write-Host
Write-Output
Get-Date
Get-Host
hostname
whoami
$PSVersionTable
Test-Connection -Count
```

---

## ⚠️ 排除的危險命令

以下命令**不應該**加入允許列表：

### 文件/目錄刪除和修改
- `Remove-Item`
- `Remove-Item -Recurse`
- `Remove-Item -Force`
- `Clear-Content`
- `Set-Content`
- `Out-File`

### 強制參數
- 任何包含 `-Force` 的命令
- 任何包含 `-Confirm:$false` 的命令

### 系統配置
- `Set-ExecutionPolicy`
- `Set-ItemProperty`
- `New-ItemProperty`
- `reg add`
- `reg delete`
- `netsh`

### 全域安裝
- `npm install -g`
- `pip install --user`
- `choco install`

### 行程管理
- `Stop-Process`
- `Kill`
- `taskkill`
- `Start-Process -Verb RunAs`

### 網路寫入操作
- `Invoke-WebRequest -Method POST`
- `Invoke-RestMethod -Method POST`
- `curl -X POST`
- `wget`

### 重新導向和寫入
- `>` (重新導向覆蓋)
- `>>` (重新導向追加)
- `Out-File`
- `Set-Content`
- `Add-Content`

---

## 實際使用範例

基於 PowerShell 的子序列匹配規則：

| 允許列表條目 | 匹配的命令範例 | 說明 |
|------------|--------------|------|
| `npm run` | `npm run dev`<br>`npm run test` | ✅ 匹配連續子序列 |
| `--help` | `python --help`<br>`git --help` | ✅ 匹配任何位置的幫助標誌 |
| `uv sync` | `uv sync`<br>`uv sync --dev` | ✅ 前綴匹配 |
| `Get-ChildItem` | `Get-ChildItem -Path .` | ✅ PowerShell cmdlet |
| `pytest -v` | `pytest -v tests/` | ✅ 帶參數的命令 |

---

## 配置建議

1. **專案範圍的套件安裝**是安全的（只影響虛擬環境）
2. **唯讀操作**永遠安全
3. **開發伺服器和測試**通常安全
4. 避免**系統級修改**和**文件刪除**操作
5. 如果需要手動確認，不要加入允許列表
