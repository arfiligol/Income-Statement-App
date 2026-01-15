# 統一設計系統 (Unified Styling System)

本文件定義 NiceGUI + Tailwind + Material Icons 的強制性樣式系統。

## 目標

建立一個單一的樣式系統，並且：

- 在深色/淺色模式 (Dark/Light Mode) 切換時運作可靠。
- 避免硬編碼顏色分散在元件中。
- 允許使用 Tailwind 佈局工具，同時保持主題一致性。
- 一致地支援 Material Icons。
- 具備可維護性與擴展性。

## 不可妥協的規則

1. **元件中禁止硬編碼顏色** (No hard-coded colors)。
2. **深淺模式切換必須由單一根開關驅動**。
3. **所有自定義樣式必須透過中心化的 Design Token 層**。
4. **每個可重用元件必須宣告其使用的語意化 Token**。

## Token-First 主題 + Tailwind 佈局

使用 CSS 變數作為 Design Tokens，並將 Tailwind 顏色工具映射到這些 Token。

- **Tailwind 主要用於佈局與間距**：
  - `flex`, `grid`, `gap-*`, `p-*`, `m-*`, `w-*`, `h-*`, `rounded-*`, `shadow-*`, `text-*` (僅尺寸), `font-*`
- **顏色與表面 (Surface) 來自 Tokens**：
  - `bg-surface`, `text-fg`, `border-border`, `bg-elevated`, `text-muted`

## 主題 Tokens (語意化調色盤)

定義一組最小化的語意 Token (需要時再擴充)：

- `--bg` (應用程式背景)
- `--surface` (卡片/面板)
- `--elevated` (模態框/彈出視窗)
- `--fg` (主要文字)
- `--muted` (次要文字)
- `--border` (邊框)
- `--primary` (品牌色)
- `--primary-fg` (品牌色上的文字)
- `--danger`, `--warning`, `--success` (可選狀態色)
- `--ring` (聚焦外框)

### 淺色/深色定義 (Light/Dark Definition)

實作方式：

- `:root { ...淺色 tokens... }`
- `.dark { ...深色 tokens... }`

在根節點切換 `.dark` 類別即可切換整個應用程式的主題。

## Tailwind 整合策略

### Tailwind 設定

Tailwind 顏色配置必須引用 CSS 變數：

- `bg-surface` -> `background-color: rgb(var(--surface) / <alpha-value>)`
- `text-fg` -> `color: rgb(var(--fg) / <alpha-value>)`
- `border-border` -> `border-color: rgb(var(--border) / <alpha-value>)`

### 允許的 Tailwind 用法

- 佈局：`flex`, `grid`, `gap`, `p`, `m`, `w`, `h`, `rounded`, `shadow`, `text-*` (僅尺寸), `font-*`
- 基於 Token 的顏色類別：`bg-surface`, `text-fg`, `border-border`, `ring-ring` 等。

### 禁止的 Tailwind 用法

- 字面顏色工具：`text-red-500`, `bg-slate-900`, `bg-[#...]` 等。
- 內聯 Hex/RGB 值與臨時 CSS 變數。

## NiceGUI + Quasar 互操作規則

- 將 Quasar 預設視為尺寸/行為的基準。
- 對於顏色，使用基於 Token 的容器類別包裝 UI：
  - 頁面根容器：`bg-bg text-fg`
  - 卡片/面板：`bg-surface border-border`
- 避免設定 Quasar 的顏色 Props，除非它們映射到 Token。

## 動畫與轉場 (Animations & Transitions)

### Tab Panels
- **預設行為**: Quasar 預設為 `slide-right`/`slide-left`。
- **政策**: 強制覆寫為 **Fade**，以避免動態暈眩並提供更乾淨的轉場。
- **實作**: 對 `ui.tab_panels` 應用 `.props("animated transition-prev=fade transition-next=fade")`。

## 元件包裝慣例 (Component Wrapper Convention)

每個頁面都使用共享的 Shell Wrapper：

- `app/ui/components/layout/shell.py` 應用 `bg-bg text-fg min-h-screen`。
- 所有頁面皆在 Shell 內渲染，確保背景/文字一致。

## 自適應佈局規則 (Adaptive Layout Rules)

- 卡片應設為 `w-full`，並依賴父容器的 Padding 來定義頁面邊緣。
- 使用父容器 Padding (例如 `px-6 py-8`) 進行水平留白；避免在卡片本身設定 Margin。
- 垂直間距請使用容器的 `gap-*` 或適度使用 `mb-*`。

## 深/淺切換契約 (Dark/Light Toggle Contract)

### 單一真理來源 (Single Source of Truth)
- 將 `theme_mode` 保持在全域 Store 中 (例如 `app/ui/state/app_store.py`)。
- 切換時：
  - 持久化使用者偏好。
  - 更新根節點 `.dark` 類別一次。
  - 不要對個別元件進行變更。

## 共享樣式資產 (Shared Style Assets)

新增專用主題資料夾並強制使用：

```text
app/ui/styles/
  theme.css          # tokens: :root and .dark
  tailwind.css       # generated or minimal Tailwind entry
  components.css     # shared component classes (btn, card, input wrappers)
```

### components.css (共享類別)

為重複的 UI 模式定義規範類別：

- `.app-card` -> `bg-surface border border-border rounded-2xl p-4 shadow`
- `.app-section-title` -> `text-lg font-semibold text-fg`
- `.app-muted` -> `text-muted`
- `.app-btn-primary` -> `bg-primary text-primary-fg ...`

## 強制執行檢查清單 (Enforcement Checklist)

- [ ] 元件中無原始顏色 (Inline, Hex, Tailwind Literal Palettes)。
- [ ] 僅使用語意化 Token 類別進行 Color/Surface/Border/Ring 設定。
- [ ] 所有頁面皆在 Shell Wrapper 內渲染。
- [ ] 深/淺切換僅翻轉根節點 `.dark`。
- [ ] 一致使用共享元件類別。
- [ ] 任何新的 Token 更新需同時包含 Light + Dark 定義。
