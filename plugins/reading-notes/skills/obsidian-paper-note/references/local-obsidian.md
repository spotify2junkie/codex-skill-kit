# Local Obsidian conventions

Use this reference only when the task writes to the user's Obsidian vault.

## Destination on this computer

This portable package has no personal vault path. Use the vault and destination explicitly supplied in the current task or in that workspace's AGENTS.md. If neither is available, ask for them before writing. Do not search personal folders for a likely vault, create a replacement vault, or migrate existing notes during skill installation.

Keep writing conventions in the destination workspace. Master-note examples are optional style references; only append to a note the user names. If the user changes the storage backend, preserve the source evidence and note structure and adapt the write/attachment layer to that backend after the user chooses it.

## Standalone mode

- Name the note `<paper short title> 精读.md` unless the user supplies a name.
- Put assets in `附件/<paper short title>/`.
- Keep one PDF and one provenance-marked figure per source unless the user asks for a text-only note.
- If the destination filename already exists, compare DOI, URL, and title. Do not overwrite it without an explicit update request.

## Append mode

- Keep every article inside the named master Markdown file.
- Continue the existing two-digit numbering and preserve its table of contents.
- Reuse the attachment folder already established by that master note. If none exists, create `附件/<master note stem>/`.
- Insert exactly one top-level article heading. Demote imported headings so they do not become accidental sibling articles.
- Do not leave nested YAML front matter inside an appended section.

## Safe edits and moves

- Inspect the destination and referenced assets before writing.
- Preserve unrelated user edits. Back up a materially replaced file to the current task's `work/` directory.
- Prefer recoverable moves for obsolete drafts. Report the archive location.
- After any move, parse every `![[...]]` PDF and image embed and verify that it resolves from the note directory or vault root.
- Keep attachment directories that are still referenced, even when cleaning duplicate notes.
