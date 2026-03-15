/**
 * Client-side module that injects the PersonalizationButton into chapter pages
 * This runs after the page loads and finds the article element
 */

export default function personalizationInjector() {
  // Wait for DOM to be fully loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectPersonalizationButton);
  } else {
    injectPersonalizationButton();
  }

  // Also listen for page transitions (SPA)
  window.addEventListener('load', injectPersonalizationButton);
}

function injectPersonalizationButton() {
  // Find the article element
  const article = document.querySelector('article');
  if (!article) return;

  // Check if we already injected
  if (article.querySelector('[data-personalization-injected]')) return;

  // Create a marker div
  const marker = document.createElement('div');
  marker.setAttribute('data-personalization-injected', 'true');
  marker.id = 'personalization-button-root';
  marker.style.cssText = 'margin: 16px 0; padding: 8px; border: 2px solid #ff0000; border-radius: 4px; background: #ffe6e6;';
  marker.innerHTML = '<strong style="color: #ff0000;">🔴 PERSONALIZATION BUTTON SHOULD APPEAR HERE (Testing)</strong>';

  // Insert before article content
  article.insertBefore(marker, article.firstChild);

  console.log('✅ Personalization injector ran - if you see the red box above, injection is working');
}
