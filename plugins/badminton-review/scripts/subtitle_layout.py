"""Pure layout rules for fixed-size badminton review subtitles."""

from __future__ import annotations

from dataclasses import dataclass
import math


MAX_LINE_CODEPOINTS = 18
MAX_LINES_PER_PAGE = 2


@dataclass(frozen=True)
class FrameSize:
    width_px: int
    height_px: int


@dataclass(frozen=True)
class CaptionPage:
    lines: tuple[str, ...]
    start_s: float
    end_s: float


@dataclass(frozen=True)
class CaptionStyle:
    font_size_px: int
    outline_px: int
    box_padding_px: int
    box_alpha: float
    center_x_fraction: float
    center_y_fraction: float


@dataclass(frozen=True)
class CaptionPlan:
    pages: tuple[CaptionPage, ...]
    style: CaptionStyle


def _style_for_frame(frame: FrameSize) -> CaptionStyle:
    if frame.width_px <= 0 or frame.height_px <= 0:
        raise ValueError("frame dimensions must be positive")

    font_size = math.ceil(frame.height_px * 0.07)
    outline = max(3, math.ceil(frame.height_px * 0.003))
    padding = math.ceil(frame.height_px * 0.0125)
    center_y = 0.84

    line_height = font_size * 1.25
    max_block_height = (
        line_height * MAX_LINES_PER_PAGE + 2 * padding + 2 * outline
    )
    bottom_margin = frame.height_px * (1 - center_y) - max_block_height / 2
    if bottom_margin < frame.height_px * 0.05:
        raise ValueError(
            "fixed caption size cannot meet the 5% bottom margin"
        )

    max_line_width = MAX_LINE_CODEPOINTS * font_size
    if max_line_width > frame.width_px * 0.92:
        raise ValueError("18 caption characters do not fit the frame width")

    return CaptionStyle(
        font_size_px=font_size,
        outline_px=outline,
        box_padding_px=padding,
        box_alpha=0.58,
        center_x_fraction=0.5,
        center_y_fraction=center_y,
    )


def _partition_text(text: str) -> tuple[tuple[str, ...], ...]:
    if not text:
        raise ValueError("caption text must not be empty")

    page_size = MAX_LINE_CODEPOINTS * MAX_LINES_PER_PAGE
    page_count = math.ceil(len(text) / page_size)
    page_length, remainder = divmod(len(text), page_count)
    pages: list[tuple[str, ...]] = []
    offset = 0
    for page_index in range(page_count):
        length = page_length + (1 if page_index < remainder else 0)
        page_text = text[offset:offset + length]
        offset += length
        lines = tuple(
            page_text[line_start:line_start + MAX_LINE_CODEPOINTS]
            for line_start in range(0, len(page_text), MAX_LINE_CODEPOINTS)
        )
        if not 1 <= len(lines) <= MAX_LINES_PER_PAGE:
            raise ValueError("caption page has an invalid line count")
        if any(len(line) > MAX_LINE_CODEPOINTS for line in lines):
            raise ValueError("caption line exceeds 18 code points")
        pages.append(lines)
    return tuple(pages)


def plan_caption(
    text: str,
    *,
    duration_s: float,
    frame: FrameSize,
) -> CaptionPlan:
    """Split a caption into fixed-size pages and local, gap-free intervals."""
    if not math.isfinite(duration_s) or duration_s <= 0:
        raise ValueError("caption duration must be finite and positive")

    line_groups = _partition_text(text)
    page_duration = duration_s / len(line_groups)
    pages = tuple(
        CaptionPage(
            lines=lines,
            start_s=page_duration * index,
            end_s=(
                duration_s
                if index == len(line_groups) - 1
                else page_duration * (index + 1)
            ),
        )
        for index, lines in enumerate(line_groups)
    )
    return CaptionPlan(pages=pages, style=_style_for_frame(frame))
