/**
 * T006: Content Parser for Chapter Content
 *
 * Extracts translatable text from article HTML while preserving code blocks.
 * Uses DOM API to parse rendered Docusaurus content safely.
 *
 * Algorithm:
 * 1. Clone article element to avoid modifying DOM
 * 2. Find and extract all code blocks (<pre><code>)
 * 3. Replace code blocks with placeholders in cloned DOM
 * 4. Extract remaining text as translatable prose
 * 5. Return prose + code blocks array for reconstruction
 */

import { ParsedContent, CodeBlock } from '../components/TranslationButton/types';
import { v4 as uuidv4 } from 'uuid';

/**
 * Placeholder template for code blocks during extraction
 * Format: [CODE_BLOCK_<id>] to minimize disruption to translation
 */
const CODE_BLOCK_PLACEHOLDER_TEMPLATE = (id: string) => `[CODE_BLOCK_${id}]`;

/**
 * Selectors for content to exclude from translation
 * Includes navigation, sidebars, metadata, comments
 */
const EXCLUDED_SELECTORS = [
  '.docSidebar', // Docusaurus sidebar
  '.pagination', // Pagination controls
  '.footer', // Footer
  'nav', // Navigation
  '.toc', // Table of contents
  'script', // Scripts
  'style', // Style tags
  '[class*="metadata"]', // Metadata blocks
];

/**
 * Code block selectors to extract
 */
const CODE_BLOCK_SELECTORS = [
  'pre > code',
  'pre',
  'code[class*="language-"]',
];

/**
 * Extract code language from class attribute
 * E.g., "language-python" → "python"
 */
function extractLanguageFromClass(classList: string): string {
  const match = classList.match(/language-(\w+)/);
  return match ? match[1] : 'unknown';
}

/**
 * Get code element and extract language
 */
function getCodeLanguage(element: Element): string {
  // Check for language-X class
  const classList = element.getAttribute('class') || '';
  if (classList.includes('language-')) {
    return extractLanguageFromClass(classList);
  }

  // Check parent elements
  let parent = element.parentElement;
  while (parent && parent !== document.body) {
    const parentClass = parent.getAttribute('class') || '';
    if (parentClass.includes('language-')) {
      return extractLanguageFromClass(parentClass);
    }
    parent = parent.parentElement;
  }

  return 'unknown';
}

/**
 * Extract all code blocks from an element
 * Returns array of CodeBlock objects with unique IDs
 */
function extractCodeBlocks(element: HTMLElement): CodeBlock[] {
  const codeBlocks: CodeBlock[] = [];

  CODE_BLOCK_SELECTORS.forEach(selector => {
    const blocks = element.querySelectorAll(selector);
    blocks.forEach(block => {
      const id = uuidv4();
      const language = getCodeLanguage(block);
      const code = block.textContent || '';

      codeBlocks.push({
        id,
        language,
        code,
        metadata: {
          filename: undefined,
          highlighted: true,
        },
      });
    });
  });

  return codeBlocks;
}

/**
 * Remove specified selectors from a cloned element
 */
function removeExcludedElements(element: HTMLElement): void {
  EXCLUDED_SELECTORS.forEach(selector => {
    element.querySelectorAll(selector).forEach(el => {
      el.remove();
    });
  });
}

/**
 * Replace code block elements with placeholders
 * Returns map of placeholder → CodeBlock ID for reference
 */
function replaceCodeBlocksWithPlaceholders(
  element: HTMLElement,
  codeBlocks: CodeBlock[]
): Map<string, string> {
  const placeholderMap = new Map<string, string>();

  CODE_BLOCK_SELECTORS.forEach(selector => {
    const blocks = element.querySelectorAll(selector);
    blocks.forEach(block => {
      // Find corresponding code block
      const code = block.textContent || '';
      const matching = codeBlocks.find(cb => cb.code === code);

      if (matching) {
        const placeholder = CODE_BLOCK_PLACEHOLDER_TEMPLATE(matching.id);
        const div = document.createElement('div');
        div.textContent = placeholder;
        block.replaceWith(div);
        placeholderMap.set(placeholder, matching.id);
      }
    });
  });

  return placeholderMap;
}

/**
 * Parse chapter content for translation
 *
 * Extracts translatable prose while preserving code blocks.
 * Safe for DOM manipulation (uses cloning, never modifies original).
 *
 * @param articleElement - HTMLElement containing article content
 * @returns ParsedContent with prose and codeBlocks array
 * @throws Error if articleElement is not valid
 */
export function parseChapterContent(articleElement: HTMLElement | null): ParsedContent {
  // Validate input
  if (!articleElement || !(articleElement instanceof HTMLElement)) {
    throw new Error('Article element is not a valid HTMLElement');
  }

  // Clone to avoid modifying original DOM
  const cloned = articleElement.cloneNode(true) as HTMLElement;

  // Step 1: Extract code blocks
  const codeBlocks = extractCodeBlocks(cloned);

  // Step 2: Remove navigation and UI elements
  removeExcludedElements(cloned);

  // Step 3: Replace code blocks with placeholders
  replaceCodeBlocksWithPlaceholders(cloned, codeBlocks);

  // Step 4: Extract HTML with markdown structure preserved
  // Using innerHTML keeps h1, h2, h3, p, li tags, etc.
  const prose = cloned.innerHTML?.trim() || '';

  // Validate extraction
  if (!prose) {
    console.warn('[ContentParser] No translatable content found in article');
  }

  return {
    prose,
    codeBlocks,
    originalElement: articleElement,
  };
}

/**
 * Reconstruct translated content by replacing placeholders
 *
 * Takes translated prose with placeholders and restores code blocks.
 * Placeholders format: [CODE_BLOCK_<uuid>]
 *
 * @param translatedProse - Translated text with placeholder markers
 * @param codeBlocks - Array of code blocks to restore
 * @returns HTML string with code blocks restored
 */
export function reconstructContent(
  translatedProse: string,
  codeBlocks: CodeBlock[]
): string {
  let result = translatedProse;

  // Replace each placeholder with its corresponding code block
  codeBlocks.forEach(block => {
    const placeholder = CODE_BLOCK_PLACEHOLDER_TEMPLATE(block.id);
    const codeHTML = `<pre><code class="language-${block.language}">${escapeHtml(block.code)}</code></pre>`;
    result = result.replace(placeholder, codeHTML);
  });

  return result;
}

/**
 * Escape HTML special characters to prevent XSS
 */
function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  };
  return text.replace(/[&<>"']/g, char => map[char]);
}

/**
 * Check if article content is available and non-empty
 */
export function hasTranslatableContent(articleElement: HTMLElement | null): boolean {
  if (!articleElement || !(articleElement instanceof HTMLElement)) {
    return false;
  }

  const content = articleElement.innerText?.trim();
  return !!content && content.length > 0;
}

/**
 * Get approximate character count of translatable content
 * Useful for estimating API costs
 */
export function getContentLength(articleElement: HTMLElement | null): number {
  if (!articleElement || !(articleElement instanceof HTMLElement)) {
    return 0;
  }

  try {
    const parsed = parseChapterContent(articleElement);
    return parsed.prose.length;
  } catch (error) {
    console.error('[ContentParser] Error calculating content length:', error);
    return 0;
  }
}

/**
 * Extract code block by ID
 * Useful for reference or validation
 */
export function getCodeBlockById(codeBlocks: CodeBlock[], id: string): CodeBlock | undefined {
  return codeBlocks.find(block => block.id === id);
}
