"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document

_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def _make_chunk(text: str, source: str, index: int) -> Chunk:
    return Chunk(
        text=text,
        source=source,
        index=index,
        produced_by="chunker.py::split_documents",
    )


def _split_by_words(text: str, source: str, index: int, chunks: list[Chunk]) -> int:
    """Last-resort fallback: fixed-size character windows with overlap."""
    start = 0
    while start < len(text):
        piece = text[start : start + config.CHUNK_SIZE].strip()
        if piece:
            chunks.append(_make_chunk(piece, source, index))
            index += 1
        start += config.CHUNK_SIZE - config.CHUNK_OVERLAP
    return index


def _split_oversized_paragraph(
    paragraph: str, source: str, index: int, chunks: list[Chunk]
) -> int:
    """
    A paragraph longer than CHUNK_SIZE. Pack whole sentences into a chunk
    until the next sentence would push it over the limit, so cuts land on
    sentence boundaries instead of mid-word. A single sentence longer than
    CHUNK_SIZE on its own still needs the raw character-window fallback.
    """
    sentences = _SENTENCE_BOUNDARY.split(paragraph)
    current = ""

    for sentence in sentences:
        candidate = f"{current} {sentence}".strip() if current else sentence

        if len(candidate) <= config.CHUNK_SIZE:
            current = candidate
            continue

        if current:
            chunks.append(_make_chunk(current, source, index))
            index += 1

        if len(sentence) <= config.CHUNK_SIZE:
            current = sentence
        else:
            index = _split_by_words(sentence, source, index, chunks)
            current = ""

    if current:
        chunks.append(_make_chunk(current, source, index))
        index += 1

    return index


MIN_CHUNK_SIZE = 40


def _merge_short_paragraphs(paragraphs: list[str], floor: int) -> list[str]:
    """A paragraph under `floor` characters merges into the previous one."""
    merged: list[str] = []
    for paragraph in paragraphs:
        if merged and len(paragraph) < floor:
            merged[-1] = f"{merged[-1]} {paragraph}"
        else:
            merged.append(paragraph)
    return merged


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Paragraph-aware chunker for campus_life.

    Each document is "Title\\n\\nParagraph\\n\\nParagraph...". Splitting on
    blank lines keeps each paragraph's single thought intact instead of
    cutting it at a fixed character count. The title is merged into the first
    body paragraph so it doesn't become its own near-empty chunk, and any
    paragraph under MIN_CHUNK_SIZE merges into the previous one so it doesn't
    stand alone either.

    A paragraph over CHUNK_SIZE (rare in this corpus: 2 out of 183) falls
    back to packing whole sentences up to the limit, and only drops to a raw
    character window if a single sentence alone exceeds CHUNK_SIZE.
    """
    chunks: list[Chunk] = []

    for doc in documents:
        paragraphs = [p.strip() for p in doc.text.split("\n\n") if p.strip()]

        if len(paragraphs) > 1:
            paragraphs = [f"{paragraphs[0]}. {paragraphs[1]}"] + paragraphs[2:]

        paragraphs = _merge_short_paragraphs(paragraphs, MIN_CHUNK_SIZE)

        index = 0
        for paragraph in paragraphs:
            if len(paragraph) <= config.CHUNK_SIZE:
                chunks.append(_make_chunk(paragraph, doc.source, index))
                index += 1
            else:
                index = _split_oversized_paragraph(
                    paragraph, doc.source, index, chunks
                )

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
