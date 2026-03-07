"""
LLM service for GPT-4 integration with grounding and citation extraction.

Handles prompt construction, LLM calls, response validation, and citation extraction.
"""

import json
import re
from typing import List, Dict, Any, Tuple
from openai import AsyncOpenAI
from app.core.config import settings
from app.utils.citation_formatter import CitationFormatter


SYSTEM_PROMPT = """You are an expert tutor assistant for the Physical AI textbook course.

YOUR ROLE:
- Answer questions based primarily on the provided textbook context
- Use the textbook excerpts to construct comprehensive answers
- If context directly addresses the question, provide a thorough answer
- If context is partial but relevant, use it as foundation and clearly cite what comes from the text
- Always prefer answering from the provided context over declining to answer

RESPONSE GUIDELINES:
1. ALWAYS answer questions if any relevant context is provided (even if partial)
2. Build answers using the textbook excerpts as primary source
3. Include citations in IEEE format: [Chapter X, Section Y: "Section Title"]
4. If multiple sections are relevant, list all citations
5. Be clear, concise, and educational
6. Avoid unnecessary caveats - if context is available, use it confidently

CITATIONS:
- Include full citations for all sources
- Format: [Chapter X, Section Y: "Section Title"]
- Include multiple citations if applicable
- Embed citations inline within the answer text (do not add a separate "Citations:" footer)

TONE:
- Educational and helpful
- Confident when drawing from provided context
- Focus on answering the user's question completely
"""


class LLMService:
    """Manages GPT-4 LLM operations with grounding and citation extraction."""

    def __init__(self):
        """Initialize OpenAI async client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def generate_grounded_response(
        self,
        question: str,
        retrieved_chunks: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]] = None,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Generate a grounded answer using retrieved chunks.

        Args:
            question: User's question.
            retrieved_chunks: List of relevant chunks from vector search.
            conversation_history: Previous messages for context (optional).

        Returns:
            Tuple of (answer_text, citations).

        Raises:
            Exception: If LLM call fails.
        """
        try:
            # Build context from chunks
            context = self._build_context_from_chunks(retrieved_chunks)

            # Build messages
            messages = []

            if conversation_history:
                messages.extend(conversation_history)

            messages.append({
                "role": "user",
                "content": f"""Context from textbook:
{context}

User question: {question}

Provide a clear, grounded answer based only on the provided context. Include IEEE-formatted citations for all sources used.""",
            })

            # Call LLM
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *messages,
                ],
                temperature=0.7,
                max_tokens=1000,
            )

            answer_text = response.choices[0].message.content

            # Extract citations and metadata
            citations = self._extract_citations(answer_text, retrieved_chunks)

            return answer_text, citations

        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")

    def _build_context_from_chunks(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Build context string from retrieved chunks.

        Args:
            chunks: List of chunks with payload metadata.

        Returns:
            Formatted context string.
        """
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            payload = chunk.get("payload", {})
            chapter = payload.get("chapter_number", "?")
            section = payload.get("section_id", "?")
            section_title = payload.get("section_title", "Unknown Section")
            content = payload.get("content", "")
            score = chunk.get("score", 0)

            # Format context with consistent citation format that LLM will use in response
            context_parts.append(
                f"[Chapter {chapter}, Section {section}: \"{section_title}\" (relevance: {score:.2f})]\n{content}\n"
            )

        return "\n".join(context_parts)

    def _extract_citations(
        self,
        answer_text: str,
        retrieved_chunks: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Extract citations from answer text and match with chunks.

        Args:
            answer_text: LLM-generated answer.
            retrieved_chunks: Retrieved chunks for reference.

        Returns:
            List of citation objects with metadata.
        """
        citations = []

        # Pattern: [Chapter X, Section Y: "Title"]
        pattern = r"\[Chapter\s+(\d+),\s+Section\s+([^:]+):\s+\"([^\"]+)\"\]"
        matches = re.findall(pattern, answer_text)

        for chapter, section, title in matches:
            # Find matching chunk
            matching_chunk = None
            for chunk in retrieved_chunks:
                payload = chunk.get("payload", {})
                if (
                    str(payload.get("chapter_number")) == chapter
                    and section.strip() in (payload.get("section_id", ""), payload.get("section_title", ""))
                ):
                    matching_chunk = chunk
                    break

            # Generate Docusaurus URL for navigation
            docusaurus_url = CitationFormatter.generate_docusaurus_url(
                int(chapter), section.strip()
            )

            citation = {
                "chapter_number": int(chapter),
                "section_id": section.strip(),
                "section_title": title,
                "score": matching_chunk.get("score", 0) if matching_chunk else 0,
                "chunk_id": matching_chunk.get("id", "") if matching_chunk else "",
                "url": docusaurus_url,  # Add Docusaurus navigation URL
            }
            citations.append(citation)

        return citations

    async def health_check(self) -> bool:
        """
        Check if OpenAI API is accessible.

        Returns:
            True if API is reachable, False otherwise.
        """
        try:
            await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "health check"}],
                max_tokens=10,
            )
            return True
        except Exception:
            return False


# Global instance
llm_service = LLMService()
