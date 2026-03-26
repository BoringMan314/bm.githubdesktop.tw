# -*- coding: utf-8 -*-
"""產生要附加到 UserTemp.zh 的列（從 Orig 取精確字串）。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
t = (ROOT / "Orig" / "renderer.js").read_text(encoding="utf-8")
DELIM = ">*.*<"
CAT = "介面補齊"


def extract_quoted_before(needle: str) -> str:
    i = t.find(needle)
    if i < 0:
        raise SystemExit(f"missing: {needle[:40]}")
    q = t.rfind('"', 0, i)
    j = q + 1
    buf = []
    while j < len(t):
        c = t[j]
        if c == "\\":
            buf.append(t[j : j + 2])
            j += 2
            continue
        if c == '"':
            return "".join(buf)
        buf.append(c)
        j += 1
    raise SystemExit("unclosed string")


pairs: list[tuple[str, str]] = [
    ("Do not show this message again", "不要再顯示此訊息"),
    ("Sorry, I can't find that branch", "抱歉，找不到該分支"),
    (
        "The commits from the selected branch will be added to the current branch via a merge commit.",
        "所選分支的提交將透過合併提交加入目前分支。",
    ),
    (
        "The commits in the selected branch will be combined into one commit in the current branch.",
        "所選分支的所有提交將合併為單一提交後加入目前分支。",
    ),
    (
        "The commits from the selected branch will be rebased and added to the current branch.",
        "所選分支的提交將重新定基底（rebase）後加入目前分支。",
    ),
    (
        "Unable to start rebase. Check you have chosen a valid branch.",
        "無法開始重新定基底。請確認您已選擇有效的分支。",
    ),
    (
        "Unable to merge unrelated histories in this repository",
        "無法合併此儲存庫中不相關的歷史記錄",
    ),
    (
        "Unable to merge unrelated histories in this repository.",
        "無法合併此儲存庫中不相關的歷史記錄。",
    ),
    ("This action cannot be undone.", "此動作無法復原。"),
    ("Sign in to your GitHub Enterprise", "登入您的 GitHub Enterprise"),
    (
        "This operating system is no longer supported. Software updates have been disabled.",
        "不再支援此作業系統，已停用軟體更新。",
    ),
    (
        "Unable to read path on disk. Please check the path and try again.",
        "無法讀取磁碟路徑。請確認路徑是否正確後再試。",
    ),
    ("Could not determine the default branch.", "無法判斷預設分支。"),
    (
        "The currently checked out branch. Pick this if you need to build on work done on this branch.",
        "目前簽出的分支。若要延續此分支上的工作，請選擇此項。",
    ),
    ("Do you want to continue anyway?", "仍要繼續嗎？"),
    ("The current branch is unborn.", "目前分支尚無任何提交（空分支）。"),
    (
        "The current repository is in a detached HEAD state.",
        "此儲存庫目前處於分離 HEAD 狀態。",
    ),
    (
        "GitHub Desktop is a seamless way to contribute to projects on GitHub and GitHub Enterprise. Sign in below to get started with your existing projects.",
        "GitHub Desktop 讓您能順暢地為 GitHub 與 GitHub Enterprise 上的專案做出貢獻。請於下方登入，以存取您既有的專案。",
    ),
    (
        "If you are using GitHub Enterprise at work, sign in to it to get access to your repositories.",
        "若您在公司使用 GitHub Enterprise，請登入以存取您的儲存庫。",
    ),
    (
        "We couldn't find that repository. Check that you are logged in, the network is accessible, and the URL or repository alias are spelled correctly.",
        "找不到該儲存庫。請確認您已登入、網路可連線，且 URL 或儲存庫別名拼寫正確。",
    ),
    (
        "Your browser will redirect you back to GitHub Desktop once you've signed in. If your browser asks for your permission to launch GitHub Desktop, please allow it.",
        "登入完成後，瀏覽器會將您導回 GitHub Desktop。若瀏覽器詢問是否允許啟動 GitHub Desktop，請選擇允許。",
    ),
    (
        "Your browser will redirect you back to GitHub Desktop once you've signed in. If your browser asks for your permission to launch GitHub Desktop please allow it to.",
        "登入完成後，瀏覽器會將您導回 GitHub Desktop。若瀏覽器詢問是否允許啟動 GitHub Desktop，請允許該操作。",
    ),
    (
        "This diff contains bidirectional Unicode text that may be interpreted or compiled differently than what appears below. To review, open the file in an editor that reveals hidden Unicode characters.",
        "此差異含有雙向 Unicode 文字，解讀或編譯結果可能與畫面顯示不同。若要檢閱，請在可顯示隱藏 Unicode 字元的編輯器中開啟檔案。",
    ),
    (
        "Unable to switch branches as there are working directory changes which would be overwritten. Please commit or stash your changes.",
        "工作目錄有變更且可能被覆寫，無法切換分支。請先提交或暫存（stash）您的變更。",
    ),
    (
        "GitHub Desktop was not able to check for updates due to a timeout. Ensure you have internet connectivity and try again.",
        "檢查更新逾時，GitHub Desktop 無法完成更新檢查。請確認網路連線後再試。",
    ),
    (
        "The push operation includes a file which exceeds GitHub's file size restriction of 100MB. Please remove the file from history and try again.",
        "此次推送含有超過 GitHub 100MB 大小限制的檔案。請從歷史記錄中移除該檔案後再試。",
    ),
    (
        "This repository is currently only available on your local machine. By publishing it on GitHub you can share it, and collaborate with others.",
        "此儲存庫目前僅存在於您的電腦。發佈到 GitHub 後即可與他人分享並協作。",
    ),
    (
        "This branch is protected and any changes requires an approved review. Open a pull request with changes targeting this branch instead.",
        "此分支受保護，變更須經核准審查。請改為建立以本分支為目標的拉取要求。",
    ),
    (
        "The branch name cannot be a 40-character string of hexadecimal characters, as this is the format that Git uses for representing objects.",
        "分支名稱不可為 40 個字元的十六進位字串，因為 Git 用此格式表示物件。",
    ),
    (
        "Checking out a commit will create a detached HEAD, and you will no longer be on any branch. Are you sure you want to checkout this commit?",
        "簽出此提交會進入分離 HEAD 狀態，且不再位於任何分支上。確定要簽出此提交嗎？",
    ),
    (
        "You have changes in progress. Undoing the commit might result in some of these changes being lost. Do you want to continue anyway?",
        "您有尚未完成的變更。復原提交可能導致部分變更遺失。仍要繼續嗎？",
    ),
    (
        "You have changes in progress. Resetting to a previous commit might result in some of these changes being lost. Do you want to continue anyway?",
        "您有尚未完成的變更。重設到先前提交可能導致部分變更遺失。仍要繼續嗎？",
    ),
    (
        "Depending on your repository's hosting service, you might need to use a Personal Access Token (PAT) as your password. Learn more about creating a PAT in our",
        "視您的儲存庫託管服務而定，您可能需要將個人存取權杖（PAT）當作密碼。如需建立 PAT 的詳細說明，請參閱我們的",
    ),
    (
        "When enabled, GitHub Desktop will underline links in commit messages, comments, and other text fields. This can help make links easier to distinguish. ",
        "啟用後，GitHub Desktop 會在提交訊息、留言與其他文字欄位為連結加上底線，較容易辨識連結。",
    ),
    (
        "When enabled, check marks will be displayed along side the line numbers and groups of line numbers in the diff when committing. When disabled, the line number controls will be less prominent.",
        "啟用後，提交時在差異中會於行號旁顯示勾選標記與行號群組。關閉時行號控制項會較不醒目。",
    ),
    (
        "These icons indicate which repositories have local or remote changes, and require the periodic fetching of repositories that are not currently selected.",
        "這些圖示表示哪些儲存庫有本機或遠端變更，並需要定期擷取目前未選取之儲存庫。",
    ),
    (
        "Turning this off will not stop the periodic fetching of your currently selected repository, but may improve overall app performance for users with many repositories.",
        "關閉此選項不會停止擷取目前選取之儲存庫，但可能改善擁有大量儲存庫時的整體效能。",
    ),
    (
        "When enabled, GitHub Desktop will attempt to load environment variables from your shell when executing Git hooks. This is useful if your Git hooks depend on environment variables set in your shell configuration files, a common practive for version managers such as nvm, rbenv, asdf, etc.",
        "啟用後，執行 Git 掛鉤時，GitHub Desktop 會嘗試從您的 shell 載入環境變數。若掛鉤依賴於 shell 設定檔中的環境變數（例如 nvm、rbenv、asdf 等版本管理工具常見做法），此功能會很有用。",
    ),
    (
        "Cache hook environment variables to improve performance. Disable if your hooks rely on frequently changing environment variables.",
        "快取掛鉤環境變數以提升效能。若掛鉤依賴經常變動的環境變數，請關閉此選項。",
    ),
    (
        "Great commit summaries contain fewer than 50 characters. Place extra information in the description field.",
        "良好的提交摘要應少於 50 個字元，其餘說明請寫在描述欄位。",
    ),
    ("Place extra information in the description field.", "其餘說明請寫在描述欄位。"),
    ("Untracked files will be excluded", "未追蹤的檔案將被排除"),
    ("This binary file has changed.", "此二進位檔案已變更。"),
]

# 從 bundle 取精確字串（含特殊引號）
dynamic = [
    (
        "A pull request allows you to propose",
        "拉取要求可讓您提出程式碼變更。建立後即表示您希望他人審查並合併。由於這是示範儲存庫，此拉取要求將為私人。",
    ),
    (
        "Publishing will",
        "發佈會將您的提交「推送」（上傳）到此儲存庫在 GitHub 上的此分支。請使用頂端列第三個按鈕發佈。",
    ),
    (
        "A commit allows you to save",
        "提交可讓您儲存一組變更。在左下角的「summary」欄位撰寫簡短訊息，說明您做了哪些變更。完成後點藍色的「提交」按鈕即可。",
    ),
]

lines_out: list[str] = []
for en, zh in pairs:
    if t.count(en) == 0:
        raise SystemExit(f"MISSING in Orig: {en[:60]!r}")
    lines_out.append(f"{en}{DELIM}{zh}{DELIM}{CAT}{DELIM}renderer.js")

for prefix, zh in dynamic:
    en = extract_quoted_before(prefix)
    lines_out.append(f"{en}{DELIM}{zh}{DELIM}{CAT}{DELIM}renderer.js")

out = ROOT / "Temp" / "_renderer_additions.txt"
out.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
print(f"Wrote {out} ({len(lines_out)} lines)")
