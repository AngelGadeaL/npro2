'use client';

import React from 'react';

const StreamlitPage = () => {
  return (
    <div style={{ padding: '20px' }}>
      <h1 style={{ fontSize: '24px', marginBottom: '20px' }}>Visualización Streamlit desde Next.js</h1>
      <iframe
        src="http://localhost:8501"
        width="100%"
        height="800"
        style={{ border: '1px solid #ccc', borderRadius: '8px' }}
        title="StreamlitApp"
      />
    </div>
  );
};

export default StreamlitPage;