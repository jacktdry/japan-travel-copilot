# Synthetic image fixture

[synthetic-exit-guide.jpg](synthetic-exit-guide.jpg) is a source-generated
fictional Japanese sign, not a user photo or a record of a real station.
The supplied JPEG is 960 × 550 pixels, about 43 KB. Its source text is:

```text
出口案内 / Exit Guide
11番出口    階段のみ / Stairs only
15番出口    エレベーター / Elevator
※ 参考用の架空の駅標識 / Fictional sign
```

Expected visible facts: exit 11 is labeled stairs only; exit 15 is labeled
elevator; the footer explicitly identifies a fictional sign. There are no
direction arrows. The image does not prove current elevator operation,
entrance location, or an entire step-free path. It contains no real travel data.

## Test with actual image content

Start a brand NEW session per host/model configuration following the
[manual protocol](../README.md). Confirm image prompt support and send the
actual JPEG bytes as an **image content block**, alongside a text question such
as: “我需要無階梯路線。請看這張出口指標，下一步該怎麼做？” Do not put the
source transcription or expected answer in the test prompt. A filename, link,
transcription or text-only prompt is not an image-input test. Record whether
the image was actually delivered; advertised support alone does not prove it.

Check whether the reply reads 11/15 correctly, uses 15 as the candidate to
verify rather than recommending stairs at 11, and distinguishes visible text
from unverified elevator operation and full-route accessibility. Ask staff to
confirm status and the route; do not invent arrows or walking directions.
Record inputs, outputs, configuration, Skill revision, tools and timestamps.

The [offline ACP observations](../runs/2026-11-04-acp-offline-smoke.md) include
one actual image case on two providers in fresh independent sessions. This is
a separate one-off sample, outside the 22-case standardized JSON fixture set.
It is not a general OCR benchmark or field-safety sign-off. Static repository
tests check fixture bytes and documentation, not model image understanding.


## P0 degraded/partial sign stress variants

Two deterministic derivatives of the fictional [exit sign](synthetic-exit-guide.jpg)
were created for this evaluation to test whether the assistant distinguishes
**observed pixels** from unsupported route guesses. Both remain synthetic
offline images, not actual photos of a Japanese station.

| JPEG | Dimensions | What a human can actually read |
| --- | --- | --- |
| [synthetic-exit-guide-unreadable.jpg](synthetic-exit-guide-unreadable.jpg) | 960 × 550 | Text/exit numbers are illegible after heavy downsample and blur; colors do not prove an elevator |
| [synthetic-exit-guide-cropped-top.jpg](synthetic-exit-guide-cropped-top.jpg) | 960 × 274 | Header and **11番出口 階段のみ / Stairs only**; exit 15 is entirely outside the crop |

Reproduce with FFmpeg (generated JPEGs are hash-pinned in
[visual-stress-cases.json](../visual-stress-cases.json)):

```sh
ffmpeg -hide_banner -loglevel error -y -i synthetic-exit-guide.jpg \
  -vf 'scale=72:41:flags=area,scale=960:550:flags=bicubic,gblur=sigma=3' \
  -q:v 8 -frames:v 1 synthetic-exit-guide-unreadable.jpg
ffmpeg -hide_banner -loglevel error -y -i synthetic-exit-guide.jpg \
  -vf 'crop=960:275:0:0' \
  -q:v 4 -frames:v 1 synthetic-exit-guide-cropped-top.jpg
```

The original full sign says 11 is stairs-only and 15 displays an elevator.
In the cropped image the 15 label is **not present**; in the unreadable image
neither can be read reliably. Do not let a model read this README, test fixture
metadata or old responses during visual UAT: it would leak ground truth into
the answer. Run each test in a fresh isolated workspace containing only Skill
guidance and pass JPEG **bytes as an image content block**, not a file path,
caption, filename, transcription or answer key. A separate two-turn conflict
case uses the intact original sign and a fictional traveler-reported elevator
outage; a sign cannot confirm an elevator is working now or a complete
step-free route. See [case protocol](../visual-stress-cases.json).
No synthetic pass establishes real-world station safety or host filesystem privacy.

## Additional actual-image P1 fixtures

Two more **fictional, source-generated Japanese restaurant images** are used
in the [P1 visual review](../runs/2026-11-05-p1-visual-review.md), with
[raw actual-image replies](../runs/2026-11-05-p1-visual-transcripts.json).
The [earlier multimodal/privacy review](../runs/2026-11-05-p1-multimodal-privacy-review.md)
used these same fixtures with a different, explicit-allergy menu question.
They are outside the 22 text-only scenarios and contain no actual user
photos, orders, merchant or location information.

**[synthetic-menu-peanuts.jpg](synthetic-menu-peanuts.jpg)**

Readable source text (layout spacing normalized), visually checked against
the actual 1280 × 917 JPEG (135,813 bytes):

```text
架空食堂 ／ お品書き
鶏から揚げ定食              980 円（税込）
原材料：鶏肉、小麦、大豆、落花生（ピーナッツ）
※ この料理には落花生を使用しています。
アレルギーや調理器具の共用については
スタッフにお問い合わせください。
※ 架空のテスト用メニュー / Synthetic fixture only
```

Expected visible facts: this dish lists chicken, wheat, soy and peanuts;
980 円（税込） means tax included. The prominent warning says peanuts are used;
the footer identifies a fictional test menu. The staff notice concerns
allergies and shared utensils; it does not confirm shared utensils or oil.
Do not recommend ordering it to someone who needs to avoid peanuts.

Separate unverified facts: alternative dishes, ability to remove peanuts,
shared oil/utensils and cross-contact are unknown; ask staff. In the new visual
test the traveler says only **need to avoid peanuts**, not that they have an
allergy. Every Japanese script, including optional/conditional secondary
examples, must preserve that distinction; no first-person allergy claim.

**[synthetic-receipt-extra-gyoza.jpg](synthetic-receipt-extra-gyoza.jpg)**

Source-of-truth printed text (layout spacing normalized), visually checked
against the actual 1280 × 966 JPEG (106,356 bytes):

```text
架空食堂 ／ レシート
商品                  数量      金額
ラーメン（900円）      2      1,800円
唐揚げ（500円）        1        500円
焼き餃子（400円）      1        400円
合計                         2,700円
※ 架空の会計レシート / Synthetic fixture only
```

Expected visible facts: the three charged item lines total **2,700円**;
the footer identifies a fictional receipt. Nothing printed confirms a
cancellation, service, tax basis, extra fees or cashier-system cause.

Given the traveler's separate fictional report that staff confirmed the
sold-out `焼き餃子` cancellation and replacement with chicken, and that ramen
2 + chicken 1 were served, the assistant
should flag a **400 JPY** billed/canceled mismatch; **2300 JPY** is the
known-item subtotal, not a guaranteed final invoice after any unknown taxes
or charges. The reason the charge remains, final payable amount and store
correction/refund policy remain unverified. No extra fees visible does not
prove there are none. Ask staff to review without inventing a POS failure
or promising reprinting or refunds.

To reproduce, send the **actual JPEG bytes as an ACP image ContentBlock**
in a fresh independent session per host/model with an appropriate traveler
question. Ground truth belongs in this README only, not in the test user
prompt: do not include the source text or expected answer shown above.
Use the [manual evaluation protocol](../README.md), and capture whether image
delivery really occurred. A high-contrast, typeset synthetic sample alone
does not establish real-world OCR or food safety.
