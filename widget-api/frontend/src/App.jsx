import React, { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [products, setProducts] = useState([])
  const [search, setSearch] = useState("")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  // Fetch history on mount
  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = () => {
    fetch('http://localhost:8005/public/products')
      .then(res => res.json())
      .then(data => setProducts(data))
      .catch(err => console.error(err))
  }

  const handleSearch = () => {
    if (!search.trim()) return
    setLoading(true)
    fetch(`http://localhost:8005/public/product/${search}`)
      .then(res => {
        if (res.ok) return res.json()
        throw new Error("Product not found")
      })
      .then(data => {
        setResult(data)
        fetchHistory() // Refresh history list
      })
      .catch(err => {
        console.error(err)
        setResult(null)
        alert(err.message)
      })
      .finally(() => setLoading(false))
  }

  return (
    <div className="App">
      <h1>🌱 EcoLabel Widget</h1>

      <div className="main-container">
        {/* Left Column: Search & Result */}
        <div className="card">
          <div className="search-box">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Enter product name (e.g. Tomato Sauce)..."
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button onClick={handleSearch} disabled={loading}>
              {loading ? 'Scanning...' : 'Analyze'}
            </button>
          </div>

          {result ? (
            <div className="score-display">
              <div className={`grade-circle grade-${result.score_letter}`}>
                {result.score_letter}
              </div>
              <h3>{result.product_name}</h3>
              <div className="detail-row">
                <span>Eco Score</span>
                <b>{result.score_numerical}/100</b>
              </div>
              <div className="detail-row">
                <span>Confidence Index</span>
                <b>{Math.round(result.confidence * 100)}%</b>
              </div>
            </div>
          ) : (
            <div style={{ color: '#9ca3af', marginTop: '2rem' }}>
              Start by typing a product name to see its environmental impact.
            </div>
          )}
        </div>

        {/* Right Column: History */}
        <div className="card">
          <h2 className="history-title">🕒 Recent Scans</h2>
          {products.length === 0 ? (
            <p style={{ color: '#9ca3af', textAlign: 'left' }}>No history yet.</p>
          ) : (
            <ul className="history-list">
              {products.map(p => (
                <li key={p.id} className="history-item" onClick={() => setResult(p)}>
                  <div>
                    <strong>{p.product_name}</strong>
                    <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>
                      {new Date(p.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  <div className={`history-badge grade-${p.score_letter}`}>
                    {p.score_letter}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
