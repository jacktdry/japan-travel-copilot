# v0.3.0 版本說明 / Release Notes

**狀態：v0.3.0 發布前驗證完成。PR #2 已合併；`main` 的 CI、公開來源和 Skills CLI 的隔離安裝／更新均已通過。正式版本標籤與下載請以 GitHub Releases 為準。**
這個專案是日本旅遊的 **AI 助理指引（Agent Skill）**，不是具備
即時車站定位、保證無障礙路線或代替官方平台的旅遊 App。

## 這一版要交付什麼

- **規劃與延續：** 簡短開始行程、沿用已提供的城市／日期／人數／偏好；
  確認過的事項與暫定想法分開。
- **旅途中協助：** 交通與景點選擇、照片或站牌解讀、遇到行程異動時整理下一步。
- **日文與帳單：** 翻譯、向店員詢問、點餐異動與收據核對。
- **預設不用額外設定：** 不需 API 金鑰、私人行程檔案或特定模型；
  可選用的檔案記憶必須另行取得同意。

主要用法是安裝後直接對 Agent 說：

> 使用 japan-travel-copilot 幫我規劃日本旅行：仙台、盛岡，兩人，
> 日期未定；先從最重要的資訊開始，不要一次問很多問題。

若已在旅行，直接提供現場問題、文字或照片，不必先完成問卷。

## 最小發布標準

這次改採 **日常使用是否順暢**，而不是對每個模型與車站都做安全認證。

- [x] **可安裝：** 核心 `SKILL.md` 和 `references/` 能以手動 ZIP
      複製進隔離的 Skills 目錄，並可被讀取；公開 CLI 安裝指令與
      作用範圍在 README 說明清楚。
- [x] **核心流程可用：** 至少在一個相容的 Agent 宿主完成簡單的
      首次規劃、上下文延續、翻譯／旅途下一步對話測試。
- [x] **基本回歸通過：** Python 3.9.6、3.15.2 各 95/95 項測試通過，
      安裝說明和相對連結有效；合併後 `main` 的 GitHub CI 也已通過。
- [x] **沒有當前可重現的核心阻斷問題：** 不任意捏造即時資料、
      不在未確認時宣稱付款／訂單已執行，也不擅自儲存私人資料。
      如果基本使用測試出現這類問題，先修復再發布。

以上是 **一般旅遊 Skill 的基本發布標準**，不等於所有宿主、交通資料、
無障礙路線、圖片理解或隱私隔離都經過全面認證。

## 本次基本驗收紀錄（2026-11-11，虛構資料）

**隔離安裝資源檢查：通過。** 用本機工作樹的 `SKILL.md`、
`references/`、`scripts/`、README 與本文件製成 ZIP，解壓至
臨時的 `host-skills/japan-travel-copilot/` 路徑。
15 個實際檔案皆可讀取，`SKILL.md` 內 19 個相對參照均指向存在的檔案；
沒有安裝到全域 Skills 目錄、沒有啟動記憶。後來又從**已合併的公開 `main`**
以 Skills CLI 成功辨識 Skill、在獨立暫存專案執行實際安裝，並確認
`skills update japan-travel-copilot --project` 回報已是最新；安裝後
`SKILL.md` 的 SHA-256 與公開主分支一致。沒有修改個人全域安裝。

**單一宿主基本對話：通過。** 在該隔離副本建立一個新 ACP 會話，
以虛構「仙台、盛岡、兩人、日期未定」開始，模型只追問一個關鍵資訊；
第二回合加入四天、近車站住宿和雙人房每晚 10,000–14,000 日圓後，
回答保留旅客條件並給出粗略行程與價格變動提醒，未捏造精確班次或飯店
即時空房；第三回合直接翻譯
「すみません、エレベーターはどこですか？」並提供向站務員詢問方向的
簡短日文，不重新啟動旅程問卷。

記錄的是**一個已完成的簡單宿主對話樣本**，不是跨模型或真實站點
測試。公開 CLI 安裝與更新已在隔離專案驗證，但不代表每個聊天宿主
都會自動載入 Skill。沒有稽核整個宿主檔案系統，也未獨立確證底層
模型或 Sandbox 狀態；這些不作為一般旅遊輔助版本的額外發布門檻。

## 不再阻擋一般版本發布的項目

完整的跨模型圖片測試、Codex ACP 額度、原生模型／Sandbox 狀態
投影一致性、宿主零暫存檔稽核，以及真實車站每段電梯動線查證，
都列為**後續改善／有需要才做的專項驗證**。歷史 P0 現場安全
**NO-GO** 紀錄和原始失敗樣本仍完整保留，不能改寫成已通過；
它們不是一般旅遊輔助版本的通用發行門檻。

相應的務實使用界線仍要遵守：時刻、費用、電梯運作及座位是否
可用屬動態資訊，必須依宿主實際工具及當前可靠來源查證；
遇到不確定的路線或照片清楚說明限制並建議現場核實；
任何預約、取消、付款或對外發訊須另外授權；
未啟用可選記憶前不主動寫入旅客檔案。

## 已完成的發布流程與後續維護

1. 已完成隔離 ZIP 資源檢查及三回合 Agent 旅遊對話煙霧測試。
2. 已通過 Python 3.9／3.15 單元測試、PR CI 與合併後 `main` 的 CI。
3. PR #2 已合併；公開 `main` 的 Skill 可被 CLI 找到，並已完成隔離的
   專案範圍安裝與更新測試。正式版標籤、版本紀錄與下載以
   [GitHub Releases](https://github.com/jacktdry/japan-travel-copilot/releases) 為準。
4. 延後的高嚴格度項目放在 [evaluations/README.md](evaluations/README.md)
   與相關報告；是否繼續投入依真實使用回饋決定。

## English summary

v0.3.0 is a practical Japan-travel Agent Skill release: plan trips,
retain confirmed conversational context, translate signs and menus, assist with
on-trip choices and disruptions, and optionally use explicitly approved file
memory. Minimum release readiness is one compatible-host basic workflow smoke
test, a reversible isolated installation-file check, and passing offline
Python/CI checks. Extensive cross-model, host sandbox and live station safety
research remains **optional follow-up**, not a universal release gate.
The Skill does not claim current transit accuracy, guaranteed step-free routes
or host-wide zero-file privacy. PR #2 was merged; the publicly hosted main-branch
Skill was discovered, installed and updated in an isolated CLI project.
The official release tag and notes are listed in GitHub Releases.
