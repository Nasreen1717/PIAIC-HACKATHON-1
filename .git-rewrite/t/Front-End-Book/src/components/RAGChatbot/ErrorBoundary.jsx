import React from 'react';

/**
 * T069: Error Boundary Component
 * Catches errors in chatbot components and displays fallback UI.
 * Prevents entire page from breaking due to chat errors.
 */
export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ChatBot Error Boundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            padding: '20px',
            color: '#c33',
            backgroundColor: '#fee',
            borderRadius: '6px',
            margin: '10px',
            fontSize: '13px',
            border: '1px solid #fcc',
          }}
        >
          <h3 style={{ margin: '0 0 8px 0' }}>Chat Assistant Unavailable</h3>
          <p style={{ margin: '0' }}>
            Please refresh the page to try again. If the problem persists,
            contact support.
          </p>
        </div>
      );
    }

    return this.props.children;
  }
}
