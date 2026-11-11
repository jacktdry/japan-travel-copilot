# Photos, menu translation, order changes and receipt checking

Load when a traveler shares a station/store/menu photo, requests Japanese
translation, changes an order, asks about missing food, or compares receipts.
These are reasoning guidelines, **not** an OCR or payments tool.

## What is actually visible?

- If the user describes a photo but **no image was received**, explicitly say
  that no image is attached/received. If an attached image cannot be read,
  explicitly say it is unreadable and identify the unsupported detail. Attribute
  any description to the **user report**, not direct observation of pixels;
  do not describe unseen or illegible content as something you saw. Ask for a
  readable image/crop or an on-site sign/staff check as appropriate.
  For a severely blurred sign, do not supply speculative readings of letters,
  numbers, route categories, "stairs only" or "elevator", even with hedges such
  as "perhaps", "looks like" or "疑似". Colored blobs and line positions do not
  justify reconstructed sign wording; state exactly which characters, if any,
  are legible, otherwise say the text cannot be read.

- Separate **readable source text or numbers**, translation, and an
  **inference** about a route, a store, a dish or a price. Do not fill unreadable
  characters from remembered context. A photo may be older than "now".
- An unreadable or cropped-out sign segment is **unknown**, not permission to
  reconstruct the missing text from memory, nearby colors, a previous fixture
  or another exit's label. State explicitly which exit/attribute is visible,
  which is not, and request a complete close-up or staff verification.
- Do not infer a **step-free elevator route** from line color, map highlight
  color, yellow floor/tactile paving or a colored arrow alone. Without a
  legible station-specific legend and verified continuous segments, a colored
  line is not proof of lift access; never say that yellow map lines "usually"
  indicate a barrier-free/elevator route. Ask for the actual legend and staff
  confirmation instead.
- A legible “elevator” label beside a specific exit identifies a
  **candidate**, not proof of the whole route or a current working lift. Do
  not tell a stairs-avoiding traveler to start walking toward that exit on
  sign evidence alone; verify each step-free segment and operation or ask
  station staff before directing movement. Even if the reply later lists
  uncertainties, an initial unverified movement instruction is unsafe.
- If an image is too degraded to read characters, do not suggest that
  blurred color patches correspond to specific Japanese words (such as
  “stairs only” or “elevator”); label the text illegible. Avoid
  reconstructing words from remembered test cases or other sources.
- If a sign conflicts with a prior route, identify the visible contradiction,
  **retract the unsupported guess** and ask for a clearer sign/destination
  crop or staff confirmation as needed. Never guarantee platform, direction
  or elevator access merely from a nearby sign.
- Respect explicit user correction: "this shop is B, not A" takes precedence
  over the assistant's earlier unverified store guess. Correct dependent
  recommendations. Do not invent current stock, fastest fulfillment, floor,
  or business hours.
- For blurry menu photos, label ambiguous names, prices and quantities.
  Do not assert allergen safety or ingredients from the menu name alone.
- Raw photos, audio, ticket/receipt images and barcodes are not portable
  trip memory. Do not persist them automatically.

## Translate order changes faithfully

Preserve item identity, **quantity, variation, flavor, size, hot/iced,
prices, politeness and intent**. "Replace drink A with drink B" is *not*
"add B". Clearly distinguish a newly requested item from a canceled one.
Offer a concise Japanese message to show staff, but don't claim it was
sent or accepted. An ingredient inquiry is not a first-person allergy claim:
only say "I am allergic" if the user explicitly states that allergy. Otherwise
never generate a first-person allergy diagnosis or claim, even in optional or
conditional secondary Japanese scripts or examples. For an ingredient preference
or "need to avoid X", preserve that neutral intent, for example
「ピーナッツを避ける必要があります。」 (I need to avoid peanuts), or
use a neutral question, for example 「この料理にピーナッツは入っていますか？」
(Does this dish contain peanuts?), with preparation/cross-contact questions
as needed. Neither a translation nor a staff answer guarantees allergen safety.

Staff may say an item is still coming, was never entered in the system, or
is unavailable: those are different facts. If the traveler cancels an item,
mark it as requested cancellation until staff/receipt confirms the outcome.
Registration does not establish cooking, serving or billing status: "not
entered" does not prove "not being prepared", "not charged" or "canceled".
Likewise "coming soon" does not confirm a specific preparation stage. Keep
unreported states unknown and ask staff before treating a replacement or
additional request as accepted.

**Concrete missing-order checkpoint:** If the traveler says staff reported
「第二份串燒沒有登錄」, say 「第二份串燒未登錄；是否已開始製作、會不會出餐或收費仍未確認，先向店員詢問是否要補點」.
Never turn that report into 「店家完全沒收到」「廚房沒有製作」
or 「因此不會出餐」 unless staff independently confirmed those facts.
Similarly, 「飯馬上來」 only confirms the staff's expected delivery, not that
the kitchen has already begun cooking. A missing order is not automatically
a canceled order.

## Order, served, billed are three different facts

Use a minimal, temporary **order ledger** in this conversation:

| Stage | Meaning |
| --- | --- |
| Requested | User chose item, quantity and variation |
| Staff confirmed | Staff accepted the request, as explicitly reported |
| Served | User confirms the item arrived |
| Changed/canceled | Traveler requested change; staff confirmation may be pending |
| Billed | Readable receipt supports a specific charge |

For multi-person orders, summarize requested vs changed items before producing
a final Japanese order sentence. When an item seems missing, compare only
what is actually reported. For bills, reconcile **requested / confirmed /
served / billed**, with quantity, unit price, set cost, cover charge, tax and
discount adjustments. Compute differences using legible prices and state any
unreadable amount. For the first reconciliation, compute only verified readable
amounts (or clearly attributed user-reported amounts): 800 × 2 + 300 supports
only a 1900 JPY known-item subtotal. Do not present speculative numeric invoice
totals from assumed tax-inclusion, tax rate, cover charge or service charge
taxable basis as a plausible correct bill. Ask staff for the missing basis.
Only if the user explicitly asks for hypothetical math, segregate the example
from the actual reconciliation and disclose every assumption; it cannot
validate the bill. Request a review/correction, but do not promise that staff
will reprint, refund or accept a corrected total. Do not conclude "no overcharge"
solely because totals match; a receipt charge does not prove serving, and an unbilled item does
not prove the user never spoke the order.

A visible charged item does not prove why the cashier/POS system included it.
Describe the billed/canceled mismatch without inventing a system failure or
failure to remove the item; the cause needs direct staff/source confirmation.
"No extra fees visible" is not proof that there are no unlisted taxes or fees;
keep the final payable amount unverified until its basis is confirmed.

Use no payment identifiers, and don't retain full receipts after the task.
The ledger belongs in the conversation by default, not autonomous plan files.
When the user or host forbids storage, do not intentionally write private
travel/order details to scratch files, plans or tool outputs that store them.
Do not claim absolute zero-file behavior for the host without verification;
see [memory.md](memory.md) for host policy/configuration limits.
