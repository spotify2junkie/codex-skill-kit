# ELI5 PDF

The ELI5 PDF lets a beginner follow the paper once before returning to the source-level engineering details.

## Sub-features

- `eli5-main-flow` checks the conclusion, main flow, fixed roles, and legend on page 1.
- `eli5-cards` checks ten dependency cards with `烦恼` and `办法` panels.
- `eli5-takeaways` checks exactly two takeaway labels per card.
- `eli5-route` checks the final migration experiment and learning route.

## How to get to it (user POV)

- Open the article note in Obsidian.
- Expand `ELI5 精读 PDF`.
- Read the PDF from page 1 through page 10.
- Follow the two cards on each of pages 2 through 6.

## Driving it with ONV CLI

Preconditions:

- The PDF embed resolves from the note.
- Poppler and ImageMagick pass doctor.

- **Verify the card rhythm.** Run ONV verify. `pdf.eli5_cards` reports ten matched sets and `pdf.two_cards_per_page` passes for pages 2 through 6.
- **Verify the page roles.** Page 7 contains the framework, page 8 the training ledger, page 9 evidence boundaries, and page 10 migration plus the learning route.
- **Inspect visuals.** Open `evidence/contact-sheet.png`. Check that comics carry the explanation, text is short, fixed roles remain recognizable, and no page has become a dense report card.
- **Attest.** Run `onv.py attest` only after inspecting every page. Then require `onv.py status` to print `ONV_PASS`.

## Gotchas

- Repeated words in hidden metadata can inflate counts. Use the rendered pages to confirm the ten visible cards.
- Text extraction cannot detect overlap, tiny type, missing glyphs, or unreadable figures.
- A pleasant cartoon is still a failure if it changes paper facts or omits a consequential limitation.
- Teaching numbers must say `示意值`; unlabeled examples can be mistaken for paper data.
