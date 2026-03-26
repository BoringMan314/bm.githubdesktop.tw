# `scripts` 使用說明

所有指令皆在**專案根目錄**執行（本專案資料夾名稱為 **`bm-githubdesktop-tw`**），並請已安裝 **Python 3**。

---

## GitHub Desktop 版本更新時：從哪裡開始？

請**依序**做下面步驟；**第一步永遠是換 `Orig`**，否則對照表與實際 bundle 版號不一致，會出現漏譯、警告列、甚至白屏。

| 順序 | 動作 | 說明 |
|:----:|------|------|
| **1** | **更新 `Orig/`** | 從本機**已安裝且未改過**的 GitHub Desktop 複製 `main.js`、`renderer.js`，覆蓋專案內 `Orig/main.js`、`Orig/renderer.js`。路徑形如：`%LOCALAPPDATA%\GitHubDesktop\app-<版號>\resources\app\`。版號必須與你接下來要給使用者的安裝版**一致**。 |
| **2** | 跑檢查 | `python scripts/validate_orig.py`。十項通過後再套用較安全。 |
| **3** | 修對照表 | 依 `validate` 與 `apply` 的警告，編輯 `Temp/UserTemp.zh`：官方若改寫英文，左欄「英文原文」須改成與**新** `Orig` 完全相同的一段字串。 |
| **4** | 產出繁體 bundle | `python scripts/apply_zh_patch.py`。寫入 `Windows/main.js`、`Windows/renderer.js`。若有 `[warn] source string(s) not found`，回到步驟 3。 |
| **5** | （選）掃漏譯 | `python scripts/scan_remaining_en.py`，列出套用後仍像介面英文的片段，再補進 `Temp/UserTemp.zh` 並重複步驟 2–4。 |
| **6** | 安裝測試 | **完全關閉** GitHub Desktop 後，只覆蓋安裝目錄 `resources\app\` 內之 **`main.js`、`renderer.js`**（勿整包取代 `app` 資料夾）。 |

**濃縮記法**：版更 → **先 Orig** → **validate** → **改 `Temp/UserTemp.zh`** → **apply** → **覆蓋安裝目錄測試**。

---

## 各檔案做什麼

| 腳本 | 用途 |
|------|------|
| `validate_orig.py` | 檢查 `Orig`、`Temp/UserTemp.zh` 是否存在與合理；對照表來源字串是否在 `Orig` 內；模擬套用後 `createElement` 數量等是否異常。**建議每次換版或改對照後都跑**。 |
| `apply_zh_patch.py` | 依 `Temp/UserTemp.zh` 將 `Orig` 全文取代後寫入 `Windows/main.js`、`Windows/renderer.js`。選項：`--main-only`、`--renderer-only`（白屏時隔離是 main 還是 renderer 出問題）。 |
| `scan_remaining_en.py` | 在記憶體中模擬套用 renderer 對照後，列出仍像 UI 的英文雙引號字串，方便補條目。 |
| `gen_renderer_additions.py` | 依腳本內建英→中對照，從 `Orig/renderer.js` 擷取精確字串，輸出可貼進 `Temp/UserTemp.zh` 的列（需視新版調整腳本內 `pairs`）。 |
| `analyze_renderer_sources.py` | 列出 renderer 對照各列在 `Orig` 的出現次數，標出過短、易誤換的來源字串。需在根目錄執行：`python scripts/analyze_renderer_sources.py`。 |
| `diagnose_patch.py` | 比對 `Orig` 與 `Windows` 的 `main.js`／`renderer.js` 在幾種結構片段上的計數與長度差，輔助粗查套用是否「傷到骨架」。 |
| `copy_to_github_desktop.ps1` | 將 `Windows\main.js`、`renderer.js` 複製到本機**最新**的 `%LOCALAPPDATA%\GitHubDesktop\app-*\resources\app\`。若 PowerShell 解析失敗，可改手動複製。 |
| `verify_installed_bundle.ps1` | 比對專案 `Windows\` 產物與上述安裝路徑內檔案之雜湊／大小是否一致（不會寫入檔案）。 |

---

## 白屏時可做的簡化流程

1. 還原安裝目錄為官方原版，確認白屏消失。  
2. `python scripts/apply_zh_patch.py --main-only`，覆蓋測試。  
3. 再 `python scripts/apply_zh_patch.py --renderer-only`，覆蓋測試。  
4. 搭配 `diagnose_patch.py` 或開發者工具 Console 錯誤縮小範圍。

更細的說明見專案根目錄 `README.md` 〈視窗全白／卡住時請先確認〉一節。

---

## 對照表格式（提醒）

`Temp/UserTemp.zh` 每列：

```text
英文原文>*.*<譯文>*.*<分類>*.*<main.js 或 renderer.js>
```

替換為**全文取代**；來源字串須與 `Orig` 內文**逐字相同**（含引號、空格）。
