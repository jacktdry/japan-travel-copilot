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

- Separate **readable source text or numbers**, translation, and an
  **inference** about a route, a store, a dish or a price. Do not fill unreadable
  characters from remembered context. A photo may be older than "now".
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
sent or accepted.

Staff may say an item is still coming, was never entered in the system, or
is unavailable: those are different facts. If the traveler cancels an item,
mark it as requested cancellation until staff/receipt confirms the outcome.

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
unreadable amount. Do not conclude "no overcharge" solely because totals
match; a receipt charge does not prove serving, and an unbilled item does
not prove the user never spoke the order.

Use no payment identifiers, and don't retain full receipts after the task.
