# NiceGUI 開發規範 (Guardrails)

本文件定義了本應用程式使用 NiceGUI 的最低遵循規範。
所有 AI Agent 在提出或實作變更前，必須詳細閱讀此文件。

## 官方參考資料

- Page Layout: https://nicegui.io/documentation/section_page_layout
- Controls: https://nicegui.io/documentation/section_controls
- Binding Properties: https://nicegui.io/documentation/section_binding_properties
- Styling & Appearance: https://nicegui.io/documentation/section_styling_appearance
- Action & Events: https://nicegui.io/documentation/section_action_events
- Pages & Routing: https://nicegui.io/documentation/section_pages_routing

## 開發規範 (Guardrails)

### 頁面佈局 (Page Layout)

- 使用 `with` context 進行 UI 樹的組合；不要顯式傳遞 parent。
- 優先使用 `ui.row`, `ui.column`, `ui.card`, `ui.grid` 以及佈局元素 (header/drawer/footer) 進行結構化。
- 不要在單一函數中混合不相關的佈局；應隔離為元件。
- 本 NiceGUI 版本不支援 `ui.page_container`；請使用 `ui.element('div').classes('q-page-container')`
  與 `ui.element('div').classes('q-page')` 來保留 Quasar 的佈局語義。

### 控制元件 (Controls)

- 使用 NiceGUI 控制元件 (`ui.button`, `ui.input`, `ui.select`, `ui.upload` 等) 並搭配明確的 Handler。
- Event Handler 僅負責發送 Intent 或呼叫 ViewModel 方法 (UI 不得包含工作流程)。
- 網頁上傳使用 `ui.upload`，桌面端則透過 Gateways 使用原生對話框。

### 綁定屬性 (Binding Properties)

- 僅對簡單、局部的 UI 同步使用 `bind_value`, `bind_text_from`, 或 `bind_visibility`。
- 避免對大型或複雜物件進行重度綁定 (主動連結刷新迴圈可能很昂貴)。
- 若需綁定自定義模型，請優先使用可綁定屬性或 Bindable Dataclasses。

### 樣式與外觀 (Styling & Appearance)

- 使用 `classes` 與 `props` 進行樣式設定；除非必要，避免使用 inline `style`。
- 佈局使用 Tailwind classes；顏色必須來自語意化 Token。
- 深色模式使用單一根開關 (`ui.dark_mode` + root `.dark` class)。
- 覆寫 Quasar 時，請依照文件使用 Tailwind layers 或 `ui.add_css`。

### 動作與事件 (Action & Events)

- 對於 I/O 密集與 CPU 密集的工作，使用 Async Handler 或背景任務。
- 避免阻塞 Event Handler；優先使用 Task Runner 或 Async Workflows。
- 僅使用 `ui.notify`, `ui.dialog`, 與 `ui.run_javascript` 處理效果 (Effects)。

### 頁面與路由 (Pages & Routing)

- `@ui.page` 僅用於獨立函數或靜態方法。
- 使用 `ui.navigate.to` 進行導航 (`ui.open` 已被移除)。
- 路由註冊發生在啟動時 (Composition Root)。

## 應用程式特定強制規範

- UI Callbacks 僅發送 Intents 並呼叫 ViewModels。
- DTOs 是唯一的跨層資料結構。
- Web/Native 差異隔離於 Infrastructure Gateways。
- 每個頁面只有一個 ViewState；效果不儲存於 State。

### 跨平台相容性 (Cross-Platform Compatibility)

- **路徑處理**: 必須使用 `pathlib.Path`；禁止字串連接路徑。
- **Windows 路徑**: 涉及反斜線 `\` 的字串 (如正則表達式或 Windows 腳本)，必須使用 Raw Strings (`r"..."`)。
- **非同步執行**: CPU/IO 密集任務必須移出主要事件迴圈。
  - 使用 `nicegui.run.io_bound` (注意: `ui.run` 是 `nicegui` 的 alias，但有時會造成 getattr 錯誤，建議 `from nicegui import run`)。

