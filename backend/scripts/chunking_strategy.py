"""
Semantic chunking strategy for textbook content.

Splits content into optimal chunks for embedding with metadata preservation.
"""

from typing import List, Dict, Any
import tiktoken


class ChunkingStrategy:
    """Implements semantic chunking based on sections with token-based sizing."""

    def __init__(self, target_tokens: int = 200, overlap_tokens: int = 50):
        """
        Initialize chunking strategy.

        Args:
            target_tokens: Target tokens per chunk (200 for better retrieval granularity).
            overlap_tokens: Number of overlapping tokens between chunks (50 for context).
        """
        self.target_tokens = target_tokens
        self.overlap_tokens = overlap_tokens
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using GPT tokenizer.

        Args:
            text: Text to count tokens for.

        Returns:
            Token count.
        """
        return len(self.tokenizer.encode(text))

    def chunk_section(
        self,
        section: Dict[str, Any],
        chapter_number: int,
    ) -> List[Dict[str, Any]]:
        """
        Chunk a single section into token-sized pieces.

        Args:
            section: Section data with content.
            chapter_number: Chapter number for metadata.

        Returns:
            List of chunks with metadata.
        """
        chunks = []
        content = section["content"]
        section_id = section["section_id"]
        section_title = section["title"]

        # Split by paragraphs first
        paragraphs = content.split("\n\n")

        current_chunk = ""
        current_tokens = 0
        chunk_counter = 0

        for paragraph in paragraphs:
            para_tokens = self.count_tokens(paragraph)

            # If adding paragraph exceeds target, save current chunk
            if current_tokens + para_tokens > self.target_tokens and current_chunk:
                chunk_counter += 1
                chunks.append({
                    "chunk_id": f"{section_id}_chunk{chunk_counter}",
                    "chapter_number": chapter_number,
                    "section_id": section_id,
                    "section_title": section_title,
                    "content": current_chunk.strip(),
                    "token_count": current_tokens,
                    "order": chunk_counter,
                })

                # Start new chunk with overlap
                # Keep last sentence for context
                sentences = current_chunk.split(". ")
                if len(sentences) > 1:
                    overlap_content = ". ".join(sentences[-1:])
                    current_chunk = overlap_content + " " + paragraph
                    current_tokens = self.count_tokens(current_chunk)
                else:
                    current_chunk = paragraph
                    current_tokens = para_tokens
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
                current_tokens += para_tokens

        # Save final chunk
        if current_chunk:
            chunk_counter += 1
            chunks.append({
                "chunk_id": f"{section_id}_chunk{chunk_counter}",
                "chapter_number": chapter_number,
                "section_id": section_id,
                "section_title": section_title,
                "content": current_chunk.strip(),
                "token_count": current_tokens,
                "order": chunk_counter,
            })

        return chunks

    def chunk_chapters(self, chapters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Chunk all chapters into semantic chunks.

        Args:
            chapters: List of parsed chapters.

        Returns:
            List of chunks ready for embedding.
        """
        all_chunks = []

        for chapter in chapters:
            chapter_number = chapter["chapter_number"]
            for section in chapter["sections"]:
                section_chunks = self.chunk_section(section, chapter_number)
                all_chunks.extend(section_chunks)

        return all_chunks


def chunk_textbook(
    chapters: List[Dict[str, Any]],
    target_tokens: int = 300,
    overlap_tokens: int = 100,
) -> List[Dict[str, Any]]:
    """
    Apply chunking strategy to parsed textbook.

    Args:
        chapters: List of parsed chapters.
        target_tokens: Target chunk size in tokens.
        overlap_tokens: Overlap between chunks.

    Returns:
        List of chunks ready for embedding.
    """
    strategy = ChunkingStrategy(target_tokens, overlap_tokens)
    chunks = strategy.chunk_chapters(chapters)

    print(f"✅ Created {len(chunks)} chunks from textbook")

    # Print statistics
    token_counts = [chunk["token_count"] for chunk in chunks]
    avg_tokens = sum(token_counts) / len(token_counts) if token_counts else 0
    print(f"   Average tokens per chunk: {avg_tokens:.0f}")
    print(f"   Min/Max tokens: {min(token_counts)}/{max(token_counts)}")

    return chunks


if __name__ == "__main__":
    from content_parser import parse_textbook

    chapters = parse_textbook()
    chunks = chunk_textbook(chapters)
    print(f"\nFirst 3 chunks:")
    for chunk in chunks[:3]:
        print(f"  {chunk['chunk_id']}: {chunk['token_count']} tokens")
