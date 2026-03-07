/**
 * T013: DocItem/Content Component (Swizzled)
 *
 * Wraps the Docusaurus DocItem/Content component to inject TranslationButton.
 * This swizzle intercepts the article rendering and adds the translation button above content.
 *
 * Generated via: npm run swizzle @docusaurus/theme-classic DocItem/Content -- --wrap
 *
 * Integration:
 * - TranslationButton is injected before article content
 * - ErrorBoundary wraps TranslationButton to handle errors gracefully
 * - Applies to all documentation pages in Modules 1-4
 */

import React from 'react';
import Content from '@theme-original/DocItem/Content';
import TranslationButton from '@site/src/components/TranslationButton';
import TranslationErrorBoundary from '@site/src/components/TranslationButton/ErrorBoundary';
import { PersonalizationButton } from '@site/src/components/PersonalizationButton';
import PersonalizationErrorBoundary from '@site/src/components/PersonalizationButton/ErrorBoundary';

/**
 * Wrapped DocItem Content component
 *
 * Injects TranslationButton before the original content.
 * Uses ErrorBoundary to prevent translation feature failures from breaking the page.
 *
 * @param {Object} props - Original DocItem/Content props
 * @returns {JSX.Element}
 */
export default function ContentWrapper(props) {
  return (
    <>
      <TranslationErrorBoundary>
        <TranslationButton />
      </TranslationErrorBoundary>
      <PersonalizationErrorBoundary>
        <PersonalizationButton />
      </PersonalizationErrorBoundary>
      <Content {...props} />
    </>
  );
}
