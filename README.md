# Japan Travel Copilot

A public, vendor-neutral Agent Skill for Japan travel: progressive first-trip
setup, pre-trip, on-trip, translation, disruption help, and optional portable
file memory. Replies default to Traditional Chinese, put one safe next step
first, and distinguish user reports, verified facts and inference.

## Install and compatibility

Copy this complete folder into a host's supported Agent Skills location,
keeping `SKILL.md`, `references/` and `scripts/` together. Consult that host's
instructions for discovery and activation; this repository does not install
itself. No particular vendor, model, account, private runtime or built-in
memory is required. Host support for Agent Skills and individual tools varies.

The core skill needs no runtime, API keys, or network service. Browsing, image
reading, filesystem access and external actions depend on the host's actual
capabilities and policies. Without live evidence, verify dynamic travel facts
with official boards, apps or staff. No invented platforms, routes, schedules,
elevator status, availability or exchange rates. Bookings, cancellations,
purchases and messages require explicit approval and a capable tool.

## First use and continuity

A fictional walkthrough:

> Traveler: Help me plan a Japan trip.
>
> Assistant: We can work in this conversation; there is no persistent memory
> unless you explicitly enable it. Which cities, dates or approximate range,
> and how many travelers? Partial answers, undecided or skip are fine.
>
> Traveler: Sendai and Morioka, two people, dates undecided.
>
> Assistant: Noted. Any accommodation area or luggage/accessibility needs?
> You can skip these too.
>
> Traveler: Near stations; skip luggage for now.
>
> Assistant: Two travelers, Sendai and Morioka, undated, accommodation near
> stations; luggage unknown. Please correct this summary. We can continue in
> this conversation or I can provide sanitized JSON for you to copy.

Reuse supplied answers, itineraries and uploads. Ask optional origins,
arrival/departure, interests, budget, transport and confirmed/tentative booking
status in short relevant batches. Do not request exact addresses or booking
codes. Already traveling? Help with the immediate next step first. Translation
requests are translated immediately. Urgency or disruption never waits for
onboarding. Later turns update confirmed deltas without repeating intake.

## Optional MEMORY

Conversation-only is the default. This feature is an explicit JSON file, not
agent built-in memory. Before any persistence, confirm the sanitized profile
and corrections, obtain storage consent, and select an external file outside
this repository/installed Skill. Reads also need opt-in. No default path,
auto-discovery, automatic invocation read/write, cloud sync or secret storage.
If memory/storage is disabled by host policy, do not bypass it: use the
conversation and optional manual JSON copy. Restoring in another session needs
the same explicitly shared accessible file and permission in that host.

The optional stdlib CLI requires Python 3.9+ and secure POSIX filesystem
facilities. Below is a **template**, with fictional data. Replace
`<EXPLICIT_EXTERNAL_DIRECTORY>` with a user-selected, existing, private,
physical absolute directory outside any Skill/Git repository. The placeholder
is deliberately not a usable path. Run only after real consent/confirmation;
the booleans do not grant filesystem permission or prove authorization.

```sh
python3 scripts/run.py <<'JSON'
{
  "skill_action": "save",
  "state_path": "<EXPLICIT_EXTERNAL_DIRECTORY>/example.travel-state.json",
  "consent": true,
  "confirmed": true,
  "expected_revision": null,
  "state": {
    "schema_version": "0.2",
    "revision": 0,
    "mode": "pre_trip",
    "profile": {
      "destinations": {"value": ["Example City"], "source": "user"},
      "dates": {"value": "undecided", "source": "user"},
      "travelers": {"value": 2, "source": "user"}
    },
    "raw_snapshot": {
      "destinations": {"value": ["Example City"], "source": "user"}
    }
  }
}
JSON
```

Success: `{"ok":true,"skill_action":"save","revision":1}` (formatting may
vary). For read-only status, use the same explicitly selected path:

```json
{"skill_action":"status","state_path":"<EXPLICIT_EXTERNAL_DIRECTORY>/example.travel-state.json","consent":true}
```

`load`/`export` return `state` on stdout only. `import` takes that object as
`state` and requires consent, confirmation and `expected_revision` for the new
explicit target. `delete`/`forget` requires those same controls. For replacement
or deletion use the current revision; `null` only creates an absent target.
Atomic owner-only writes and revision checks protect cooperating callers;
this is neither encryption nor a sandbox against hostile concurrent writers.
Sensitive free text still needs human/host review. See the full
[CLI and limitations](references/memory.md) and [schema](references/travel-state.md).

## Development and license

```sh
python3 -m unittest discover -s tests -v
```

Tests use only stdlib, synthetic data, temporary external files and no network.
CI discovers all tests. Static onboarding checks are contract checks, not proof
of every host's conversational behavior. See [CONTRIBUTING.md](CONTRIBUTING.md),
[SKILL.md](SKILL.md), and [scenarios](references/scenarios.md).
Apache-2.0; see [LICENSE](LICENSE).

---

# 日本旅遊 Copilot

公開、可攜且不綁定供應商的 Agent Skill，提供首次旅程引導、行前、旅途中、翻譯、
行程受阻協助，以及選用的檔案記憶。預設繁體中文，先給一個安全可執行的下一步，
並區分使用者提供、已查證與推論資訊。

## 安裝與相容性

依宿主文件將完整資料夾放入支援的 Agent Skills 位置，保留 `SKILL.md`、
`references/` 與 `scripts/` 相對路徑。儲存庫不會自行安裝，不依賴特定供應商、
模型、帳號、私有執行階段或內建記憶。不同宿主的技能載入與工具能力可能不同。
核心技能不需要執行環境、API 金鑰或指定網路服務；查網頁、讀圖片、存取檔案及
外部操作均須宿主實際支援且允許。即時資訊查不到時，請旅客看官方看板、App
或詢問現場人員，不猜路線、月台、時刻、電梯、庫存或匯率。購買、訂房、取消及
傳送訊息須有明確核准與可執行工具。

## 首次使用範例與後續更新

以下是虛構對話：

> 旅客：想規劃日本旅行。
>
> 助理：先在這段對話協助你；除非你明確啟用，沒有持久記憶。想去哪些城市、
> 日期或大約期間、幾位旅客？可以先回答一部分，也可以說未定或跳過。
>
> 旅客：仙台、盛岡，兩人，日期未定。
>
> 助理：收到。住宿地區、行李或無障礙需求有想法嗎？可以跳過。
>
> 旅客：住車站附近，行李先跳過。
>
> 助理：摘要是兩人去仙台、盛岡，日期未定，住宿偏好車站附近，行李未知。
> 請確認或更正；可以繼續在對話規劃，也能提供去除敏感資料的 JSON 自行複製。

已提供的資料、行程表或上傳檔案應直接沿用，不重問。其他出發地、抵離、興趣、
預算、交通偏好與訂單已確認／暫定狀態，分小批依需要選問；不索取完整地址或
訂位代碼。已在旅行就先處理眼前下一步；單純翻譯直接翻譯，緊急或受阻處理不等
引導完成。後續只更新已確認的變動，不重新跑問卷。

## 選用 MEMORY 與同意

預設僅限對話。記憶是明確指定的 JSON 檔案，不是代理程式內建記憶。寫入前先
確認摘要與更正、取得儲存同意，並由使用者／宿主指定儲存庫與已安裝 Skill 之外
的檔案；讀取也要同意。沒有預設路徑、自動尋找、啟用時自動讀寫、雲端同步或
秘密保管功能。宿主停用記憶／儲存時不可繞過；繼續用對話，選擇手動複製 JSON。
跨對話恢復必須再次明確提供同一個可存取檔案，並符合目前宿主權限。

選用 CLI 需要 Python 3.9+、標準函式庫及安全的 POSIX 檔案能力。上方 stdin JSON
範例使用虛構資料；請將 `<EXPLICIT_EXTERNAL_DIRECTORY>` 換成明確選定、已存在、
私有且位於 Skill／Git 儲存庫之外的實體絕對目錄。範例佔位符不能直接執行。
`consent`／`confirmed` 只表達真實同意與確認，不授予權限。每次明確提供路徑；
新建用 `expected_revision: null`，覆寫或刪除用目前版本號，衝突要重讀並重新確認。
`status` 唯讀；`load`／`export` 只向 stdout 回傳資料，`import` 讀取請求內的
`state`，`delete`／`forget` 只移除指定檔案，不抹除備份或宿主對話。

採原子寫入與僅擁有者可讀寫的檔案權限，但不是加密或對抗惡意並行寫入的沙箱；
自由文字仍須人工／宿主檢查敏感內容。完整同意契約、錯誤代碼與限制見
[記憶文件](references/memory.md)、[狀態格式](references/travel-state.md)；
引導規則見 [onboarding](references/onboarding.md)。

## 開發與授權

在根目錄執行 `python3 -m unittest discover -s tests -v`。測試只用標準函式庫、
虛構資料與外部暫存檔案，不連網；CI 探索全部測試。引導文字的靜態契約檢查不
等於所有宿主的對話行為驗收。貢獻規範見 [CONTRIBUTING.md](CONTRIBUTING.md)。
Apache-2.0，詳見 [LICENSE](LICENSE)。
