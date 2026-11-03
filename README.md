# Japan Travel Copilot

A portable, tool-agnostic Agent Skill for practical Japan trip planning and
in-trip help. It prioritizes one safe next step, concise mobile replies, and
clear separation between user reports, verified facts, and inference.

## Install

Copy the complete `japan-travel-copilot/` folder into a compatible agent's
skills directory. Keep `SKILL.md` at the root of that folder and preserve the
relative `references/` links. Consult the host agent's documentation for its
skills directory and discovery behavior.

For AgentDock, use its local-directory skill import if that capability is
available in your installed version. This repository does not provide or claim
an AgentDock runtime contract. ChatGPT does not automatically install a skill
from this repository; use only a host that supports the Agent Skills format.

The skill has no API keys, external runtime dependencies, or required network
service. Dynamic travel facts still require an available, suitable live source;
without one the skill asks the traveler to verify with official boards, apps, or
staff.

## What it covers

- Pre-trip, on-trip, translation, and disruption modes.
- Conversation-only travel state updates, without implied persistence.
- Evidence-based station, platform, exit, elevator, and service guidance.
- Faithful Chinese-Japanese translation and cautious reading of travel photos
  and menus.
- Flight/accommodation disruption recovery, shopping, and currency estimates.
- Privacy, emergency, and explicit approval boundaries for external actions.

Start at [SKILL.md](SKILL.md). Supporting contracts and synthetic examples are
in [references/](references/).

## Development

Requires Python 3 and its standard library only. Run the repository checks
from the root:

```sh
python3 -m unittest discover -s tests -v
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for scope and validation expectations.

## License

Apache-2.0; see [LICENSE](LICENSE).

---

# 日本旅遊 Copilot

這是一個可攜、與工具無關的 Agent Skill，協助日本行前規劃與旅途中處理實際
問題。優先提供一個安全、可執行的下一步，回覆適合手機閱讀，並清楚區分使用者
提供、已查證與推論的資訊。

## 安裝

將完整的 `japan-travel-copilot/` 資料夾複製到相容代理程式的 skills 目錄。
請讓 `SKILL.md` 留在該資料夾根目錄，並保留 `references/` 相對路徑。skills
目錄位置與自動探索方式請依照所用代理程式的文件設定。

若使用 AgentDock，請在目前安裝版本確實支援時，使用本機目錄匯入功能。本專案
不提供也不宣稱任何 AgentDock 執行階段契約。本儲存庫不會讓 ChatGPT 自動安裝
技能；請使用支援 Agent Skills 格式的宿主。

本技能不需要 API 金鑰、外部執行階段依賴或指定網路服務。即時旅遊資訊仍須由
可用且適當的即時來源查證；沒有這類來源時，應請旅客查看官方看板、App 或詢問
現場人員。

## 功能

- 行前、旅途中、翻譯與行程受阻模式。
- 僅在對話中更新旅遊狀態，不暗示持久儲存。
- 依據證據提供車站、月台、出口、電梯與營運資訊。
- 忠實中日翻譯，謹慎讀取旅遊照片與菜單。
- 航班或住宿受阻處理、購物與匯率估算。
- 隱私、緊急情況與外部操作明確核准界線。

請先閱讀 [SKILL.md](SKILL.md)。支援文件與虛構情境範例位於
[references/](references/)。

## 開發

只需要 Python 3 與標準函式庫。在儲存庫根目錄執行：

```sh
python3 -m unittest discover -s tests -v
```

請參閱 [CONTRIBUTING.md](CONTRIBUTING.md) 的範圍與驗證要求。

## 授權

Apache-2.0，詳見 [LICENSE](LICENSE)。
