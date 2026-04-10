import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import './index.css'
import LoginGate from './auth/LoginGate.jsx'
import ErrorBoundary from './components/ErrorBoundary.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <LoginGate>
        <ErrorBoundary>
          <App />
        </ErrorBoundary>
      </LoginGate>
    </BrowserRouter>
  </React.StrictMode>,
)
