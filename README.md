### 本專案對應 GitHub Desktop 版本：3.5.6

此工具為 **GitHub Desktop** 的正體中文化。

![截圖](screenshot.png)

### 參考資料
GitHub Desktop 官網：https://desktop.github.com  
GithubDesktopZhTool：https://github.com/robotze/GithubDesktopZhTool  
GithubDesktopTW：https://github.com/NeKoOuO/GithubDesktopTW

### Windows

將本專案 `Windows` 資料夾內的 `main.js` 和 `renderer.js` 複製，覆蓋本機 GitHub Desktop 安裝路徑內對應檔案（見下路徑）。
`%LOCALAPPDATA%\GitHubDesktop\app-*\resources\app\`

### 自行編譯 main.js／renderer.js

1. 從本機 **GitHub Desktop 安裝目錄**複製**未修改**的 `main.js`、`renderer.js`，覆蓋本專案的 `Orig/main.js`、`Orig/renderer.js`（版本須與你實際安裝一致）。
2. 編輯對照表 `Temp/UserTemp.zh`：每列格式為 `英文原文>*.*<譯文>*.*<分類>*.*<main.js 或 renderer.js>`，程式會依「英文原文」做全文取代。
3. 確認 Orig 與對照表一致、套用後不會誤傷程式碼：`python scripts/validate_orig.py`
4. 在專案根目錄執行：  
   `python scripts/apply_zh_patch.py`  
   預設會寫入 `Windows/main.js` 與 `Windows/renderer.js`。
5. 將這兩個檔複製到安裝路徑的 `resources\app\` 覆蓋原版（路徑形如 `%LOCALAPPDATA%\GitHubDesktop\app-*\resources\app\`）。

若升級 GitHub Desktop 後某句英文改寫，對照表內對應的「英文原文」也要一併更新，否則該句不會被替換。

### 視窗全白／卡住時請先確認

1. **只覆蓋兩個檔**：務必只替換 `resources\app\main.js` 與 `resources\app\renderer.js`，**不要**整包刪掉或覆蓋整個 `app` 資料夾（缺少 `index.html`、`package.json` 等會直接白屏）。
2. **版本一致**：`Orig` 必須從**同一版**安裝目錄複製；本專案產物與 `app-3.5.x` 需對應。
3. **完全結束程式後再覆蓋**：工作管理員結束所有 GitHub Desktop 相關處理序後再複製。
4. **可改用腳本複製**（以系統管理員權限執行 PowerShell 若遇權限問題）：  
   `powershell -ExecutionPolicy Bypass -File scripts\copy_to_github_desktop.ps1`
5. 本專案已用 `validate_orig.py` 驗證：套用後 **`createElement` 等骨架與原版數量相同**，代表產出的 JS 未缺括號／未誤刪函式結構；若仍白屏，請在 GitHub Desktop 視窗按 **Ctrl+Shift+I** 查看 **Console** 第一則紅色錯誤並回報。
6. **隔離測試**（判斷白屏來自 main 還是 renderer）：  
   - 只繁體化選單／主程式：`python scripts/apply_zh_patch.py --main-only`  
   - 只繁體化介面內容：`python scripts/apply_zh_patch.py --renderer-only`  
   每次產生後再覆蓋到 `resources\app\` 重開，看哪一種會白屏。
7. **還原英文對照**：若把安裝目錄裡的 `main.js`、`renderer.js` 換回**原版**（從官方重裝或備份）後白屏消失，即可確定與繁體檔案有關；再搭配第 6 點縮小範圍。
