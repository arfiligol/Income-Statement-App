# NiceGUI 應用程式架構 (MVVM + Clean + DTO 規範)

這份文件定義了本 NiceGUI 應用程式不可妥協的架構原則。

## 目標

建立一個可維護的 NiceGUI 應用程式（Web + 可選的 Native Desktop），並達成以下目標：

- 使用 Material Icons + TailwindCSS 進行現代化 UI 設計。
- 利用 Python 進行強大的資料分析 (pandas/numpy 等)。
- 支援系統原生功能（如檔案選擇器）並處理 Excel 檔案。
- 即使在 NiceGUI 的事件驅動生命週期中，也要避免 Callback Spaghetti（回呼地獄）。

## 核心原則 (不可妥協)

1. **UI Callbacks 不得包含業務邏輯**：僅負責觸發 ViewModels。
2. **跨層資料交換必須僅使用 DTOs**：禁止直接傳遞 ORM 物件或 DataFrame。
3. **Web 與 Native 的差異必須隔離在 Infrastructure Gateways 中**。

## 建議的高層架構

結合以下模式：

- 類整潔架構層次：`domain / application / infrastructure`
- NiceGUI 的 MVVM 模式：`ui/pages/components + ui/viewmodels + ViewState/Intent/Effect`
- 可選的 `api/`（僅在需要外部 HTTP 端點時）。

## 分層職責

### domain/ (領域層)

- 純粹的規則與結構：DTOs、Entities、Validators、Transformations、Enums。
- 禁止 I/O、禁止 pandas、禁止 NiceGUI、禁止檔案系統呼叫。

### application/ (應用層)

- 負責工作流程編排的使用案例 (Use Cases)（例如：「匯入 Excel -> 驗證 -> 映射 -> 計算 -> 匯出」）。
- 僅依賴 `domain` 與 `application/ports` (介面)。
- 禁止匯入 NiceGUI；避免直接操作 pandas/openpyxl（應委派給 infra 層）。

### infrastructure/ (基礎設施層)

- 外部世界：Excel I/O (pandas/openpyxl)、檔案系統、資料庫、Web/Native Gateways。
- 實作 `application/ports` 中定義的介面。
- 將外部格式轉換為 Domain DTOs 並回傳 DTOs。

### ui/ (表現層)

- Pages/Components/Layout + Routing + ViewModels。
- 負責渲染、事件綁定、狀態綁定與 Effects。
- 禁止繁重的邏輯、禁止 I/O、禁止 pandas。

## NiceGUI 的 MVVM 生命週期模式

### 關鍵構造

- **ViewState (單一真理來源)**：每個頁面/功能一個狀態物件。
- **Intent/Command**：所有的 UI 事件都轉化為有限的 Intent 集合。
- **Effect Channel**：一次性的副作用（如通知、跳轉）不應儲存在 ViewState 中。

### 生命週期流程

1. **View** 發出 Intent（或呼叫 VM 方法）。
2. **ViewModel** 處理 Intent：
   - 更新 Loading 狀態。
   - 呼叫 UseCase(s)。
   - 成功時：更新 State (填入 DTO 結果)。
   - 失敗時：設定 Error State + 發出 Effect。
3. **View** 嚴格根據 ViewState 重新渲染；副作用透過 Effects 執行。

## 路由與模組化

- `ui/routers/*`：負責路由註冊。
- `ui/pages/*`：負責頁面組裝。
- `ui/components/*`：可重用的 UI 元素。

## Web + Native 檔案處理策略

定義統一的 `FileSource` DTO：

- `LocalPathSource(path)`：用於原生檔案對話框。
- `UploadedTempSource(temp_path_or_id)`：用於 Web 上傳。
- (可選) `BytesSource(bytes, filename)`：若有需要處理純位元組。

UI 總是操作 `FileSource`，由 Infrastructure 解析為可讀取的輸入。

### 實作筆記 (NiceGUI + Native)

- 檔案選擇器 UI 位於 `app/ui/components/widgets/file_source_picker.py`。
- Web 模式使用 `ui.upload` 並在建立 `FileSource` 前將檔案存至暫存區。
- Native 模式使用 `app.native.main_window.create_file_dialog` 並回傳包含路徑的 `FileSource`。
- 在 Native 模式下應使用 `webview.FileDialog.OPEN` 以避免 pickling 錯誤。
- 若 `on_file_selected` 是非同步的，請使用 `asyncio.create_task` 排程，避免未等待的 Coroutine 警告。

## 背景任務策略

Excel 匯入與繁重計算必須在 UI 執行緒之外執行。

- 提供中心化的 `TaskRunner` (Thread/Process Pool + Async Wrapper)。
- ViewModel 應立即設定 Loading 狀態，等待任務完成，然後更新 State/Effects。

## 樣式策略 (Tailwind + Material Icons)

- 使用 **Tailwind** 處理佈局 (Spacing/Grid/Typography/Responsive)。
- 保持元件視覺與 NiceGUI/Quasar 預設一致；最小化覆寫。
- 集中管理 Icon 名稱/映射，避免字串散落在 UI 各處。
- 將最小化的覆寫放在 `app/ui/styles/` 並應用 Token-First 主題 (詳見樣式指南)。

## 建議目錄結構

```text
your_app/
  main.py  # Composition Root: DI wiring, router registration, ui.run()

  app/
    config/
      settings.py
      logging.py

    common/
      errors.py
      types.py
      utils/

    domain/
      dto/
      entities/
      rules/
      enums.py

    application/
      use_cases/
      services/
      ports/
        repositories.py
        gateways.py

    infrastructure/
      repositories/
        excel_pandas_repo.py
      gateways/
        file_picker_web.py
        file_picker_native.py
        notifications.py
      runtime/
        task_runner.py
        paths.py

    ui/
      routers/
      pages/
      components/
        layout/
        widgets/
      viewmodels/
        base.py
      state/
        app_store.py
        session_store.py
      styles/
      static/

  tests/
    domain/
    application/
    infrastructure/
    ui_smoke/
```

## 審查清單 (Review Checklist)

- [ ] UI Callbacks 僅發出 Intent / 呼叫 VM 方法 (無工作流程邏輯)。
- [ ] 沒有 DataFrame/openpyxl/ORM 物件洩漏到 Infrastructure 之上。
- [ ] UseCases 僅依賴 Ports/Interfaces，不依賴 Infra 的實作。
- [ ] Web/Native 的差異僅存在於 Infrastructure Gateways 中。
- [ ] 每個頁面只有一個 ViewState 作為單一真理來源；沒有隱藏的 UI 狀態。
- [ ] 副作用走 Effects 通道，不存於持久化狀態中。
