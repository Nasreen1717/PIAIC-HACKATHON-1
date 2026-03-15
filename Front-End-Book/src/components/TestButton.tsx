import React from 'react';

export const TestButton: React.FC = () => {
  return (
    <button
      style={{
        padding: '8px 16px',
        backgroundColor: '#ff0000',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer',
        fontSize: '14px',
        fontWeight: 'bold',
        marginRight: '8px',
      }}
      onClick={() => alert('TEST BUTTON WORKS!')}
    >
      🧪 TEST
    </button>
  );
};
