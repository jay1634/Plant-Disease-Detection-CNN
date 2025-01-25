import React from 'react';
import ReactDOM from 'react-dom/client'; // import from 'react-dom/client' in React 18
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root')); // Create a root
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
