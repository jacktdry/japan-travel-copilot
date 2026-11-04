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
