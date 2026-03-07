/**
 * Error Boundary for PersonalizationButton
 *
 * Prevents personalization feature errors from crashing the page.
 * If PersonalizationButton fails, the rest of the page continues to work.
 */

import React, { ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export default class PersonalizationErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('PersonalizationButton error:', error, errorInfo);
    // Could send to error logging service here
  }

  render() {
    if (this.state.hasError) {
      // Silently fail - just don't render the button
      // The page content remains fully functional
      return null;
    }

    return this.props.children;
  }
}
