import { useMemo, useState } from 'react'
import './App.css'
import { useAuth } from './hooks/useAuth'

const menuItems = [
  { key: 'introduction', label: 'Introduction' },
  { key: 'recipes', label: '1. Recipes' },
  { key: 'food', label: '2. Food' },
  { key: 'compounds', label: '3. Compounds' },
  { key: 'enzymes', label: '4. Enzymes' },
  { key: 'gene', label: '5. Gene' },
  { key: 'flavor-fingerprint', label: '6. Flavor Fingerprint' },
  { key: 'recipe-fingerprint', label: '7. Recipe Fingerprint' },
  { key: 'molecular-overlap', label: '8. Molecular Overlap' },
  { key: 'flavor-bridges', label: '9. Flavor Bridges' },
  { key: 'cross-modal', label: '10. Cross-Modal Compensation' },
  { key: 'generation', label: '11. Recipe Generation' },
  { key: 'graphdb-console', label: '🗄️ GraphDB Console' },
]

const recipeSearchItems = [
  'I - Ordinary or White Consommé',
  'II - Clarified Consommé for Clear Soups',
  'Fonds de Cuisine (No. 3)',
  'Guide to Modern Cookery (Page 4)',
]

function Sidebar({ activeKey, onSelect, user, onLogout }) {
  const handleMenuClick = (key) => {
    if (key === 'graphdb-console') {
      window.open(`http://${window.location.hostname}:7474`, '_blank');
      return;
    }
    onSelect(key);
  };
  return (
    <nav className="sidebar">
      <div className="sidebar-header">
        <h1>
          L&apos;atelier<span>.</span>
        </h1>
      </div>
      <ul className="sidebar-menu">
        {menuItems.map((item) => (
          <li className="menu-item" key={item.key}>
            <button
              type="button"
              className={activeKey === item.key ? 'active' : ''}
              onClick={() => handleMenuClick(item.key)}
            >
              {item.label}
            </button>
          </li>
        ))}
      </ul>
      <div className="sidebar-footer">
        {user && (
          <div className="sidebar-user">
            <span className="sidebar-username">{user.username}</span>
            <button type="button" className="logout-btn" onClick={onLogout}>
              Sign out
            </button>
          </div>
        )}
        <div>© 2026 L&apos;atelier Project</div>
      </div>
    </nav>
  )
}

function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await onLogin(username, password)
    } catch (err) {
      setError(err.message || 'Login failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="login-shell">
      <div className="login-card">
        <div className="login-header">
          <h1 className="login-title">
            L&apos;atelier<span className="accent">.</span>
          </h1>
          <p className="login-subtitle">Sign in to continue</p>
        </div>
        <form className="login-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="login-username">Username</label>
            <input
              id="login-username"
              type="text"
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={submitting}
            />
          </div>
          <div className="form-group">
            <label htmlFor="login-password">Password</label>
            <input
              id="login-password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={submitting}
            />
          </div>
          {error && <div className="login-error">{error}</div>}
          <button type="submit" className="login-btn" disabled={submitting}>
            {submitting ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  )
}

function IntroductionPage() {
  return (
    <div className="content-wrapper">
      <h1 className="project-title">
        L&apos;atelier<span className="accent">.</span>
      </h1>
      <div className="subtitle">A Computational Approach to Gastronomy</div>

      <div className="badge-container">
        <span className="badge">Data-Driven Culinary</span>
        <span className="badge">Flavor Networks</span>
        <span className="badge">Molecular Gastronomy</span>
        <span className="badge">AI Generation</span>
      </div>

      <h2>Project Philosophy</h2>
      <p>
        <strong>L&apos;atelier</strong> represents a paradigm shift in how we understand, deconstruct,
        and synthesize culinary art. Gastronomy has traditionally evolved through empirical
        observation and cultural intuition. L&apos;atelier reframes cooking as an exact science
        governed by data networks, discrete mathematical models, and molecular interactions.
      </p>

      <div className="figure-container">
        <img
          src="/template/egg-dark.png"
          alt="The Fluid Geometry of Taste Dashboard Diagram"
        />
        <div className="figure-caption">
          <strong>Figure 1.1: The Fluid Geometry of Taste.</strong> A high-resolution visualization map
          generated inside the L&apos;atelier matrix framework.
        </div>
      </div>

      <h2>The Dual-Core Data Foundation</h2>
      <p>
        To transform gastronomy into a predictive algorithm, <em>L&apos;atelier</em> anchors its
        high-dimensional vectors upon a dual-core foundation.
      </p>

      <div className="framework-grid compact-gap">
        <div className="card card-top">
          <h3>FooDB Macro-Feature Engine</h3>
          <p>
            We systematically ingest data fields from <a href="https://foodb.ca">FooDB</a>, mapping
            profiles on volatile compound concentrations and sensory chemical paths.
          </p>
          <div className="image-frame">
            <img src="/template/foodb.png" alt="FooDB Data Engine Interface" />
          </div>
        </div>

        <div className="card card-top">
          <h3>Le Guide Culinaire Expert Graph</h3>
          <p>
            We digitize Escoffier&apos;s foundational culinary protocols into an expert graph that
            reinforces sensory alignment for AI generation.
          </p>
          <div className="image-frame">
            <img src="/template/escoffier.png" alt="Auguste Escoffier Portrait" />
          </div>
        </div>
      </div>

      <h2>The Fluid Geometry of Taste: A Concept Overview</h2>
      <p>
        The iconic rainbow egg of <strong>L&apos;atelier</strong> is a living roadmap of flavor harmony.
      </p>

      <div className="framework-grid">
        <div className="card card-left">
          <h3>The Uncharted Flavor Map</h3>
          <p>Gradient regions represent known and unexplored ingredient combinations.</p>
        </div>
        <div className="card card-left">
          <h3>The Dynamic Culinary Fluid</h3>
          <p>
            Small cooking decisions, like heat level and fermentation time, systematically reshape
            the flavor landscape.
          </p>
        </div>
        <div className="card card-left">
          <h3>Sensory Singularities</h3>
          <p>
            Vortex centers mark points of strong harmony where ingredient clashes dissolve into a
            unified profile.
          </p>
        </div>
        <div className="card card-left">
          <h3>Seamless Sensory Bridges</h3>
          <p>
            The framework calculates aromatic bridges so substitutions retain taste continuity.
          </p>
        </div>
      </div>

      <h2>System Roadmap</h2>
      <p>
        L&apos;atelier bridges computer logic with culinary artistry, supporting sustainable recipe
        engineering and scientific gastronomy.
      </p>

      <section className="creator-section">
        <div className="creator-header">
          <div className="creator-title">About the Creator</div>
          <div className="social-links">
            <a href="https://github.com" target="_blank" rel="noreferrer" className="social-icon">
              GH
            </a>
            <a href="https://linkedin.com" target="_blank" rel="noreferrer" className="social-icon">
              IN
            </a>
          </div>
        </div>
        <p className="creator-text">
          Created to bridge neural-network precision with the sensory heritage of classic gastronomy.
        </p>
      </section>
    </div>
  )
}

function RecipePage() {
  const [query, setQuery] = useState('')
  const [isOpen, setIsOpen] = useState(false)
  const [focusIndex, setFocusIndex] = useState(-1)

  const matches = useMemo(() => {
    if (!query.trim()) return []
    return recipeSearchItems.filter((item) => item.toLowerCase().includes(query.toLowerCase().trim()))
  }, [query])

  const selectValue = (value) => {
    setQuery(value)
    setIsOpen(false)
    setFocusIndex(-1)
  }

  const onSearchKeyDown = (event) => {
    if (!matches.length) return

    if (event.key === 'ArrowDown') {
      event.preventDefault()
      setFocusIndex((index) => (index + 1 >= matches.length ? 0 : index + 1))
      setIsOpen(true)
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      setFocusIndex((index) => (index - 1 < 0 ? matches.length - 1 : index - 1))
      setIsOpen(true)
    } else if (event.key === 'Enter') {
      event.preventDefault()
      if (focusIndex >= 0) {
        selectValue(matches[focusIndex])
      }
    } else if (event.key === 'Escape') {
      setIsOpen(false)
      setFocusIndex(-1)
    }
  }

  return (
    <div className="recipe-container">
      <header className="recipe-header">
        <div className="header-content">
          <div>
            <h1 className="project-title">
              L&apos;atelier<span className="accent">.</span>
            </h1>
            <p className="recipe-subtitle">Le Guide Culinaire Expert Engine Output</p>
          </div>

          <div className="search-container">
            <input
              type="text"
              id="search-input"
              placeholder="Search Escoffier protocols..."
              autoComplete="off"
              value={query}
              onChange={(event) => {
                setQuery(event.target.value)
                setIsOpen(Boolean(event.target.value.trim()))
                setFocusIndex(-1)
              }}
              onFocus={() => setIsOpen(Boolean(query.trim()))}
              onBlur={() => setTimeout(() => setIsOpen(false), 100)}
              onKeyDown={onSearchKeyDown}
            />
            {isOpen && matches.length > 0 && (
              <ul id="autocomplete-list">
                {matches.map((match, index) => (
                  <li key={match}>
                    <button
                      type="button"
                      className={focusIndex === index ? 'active-nav autocomplete-item' : 'autocomplete-item'}
                      onClick={() => selectValue(match)}
                    >
                      {match}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </header>

      <section className="meta-grid">
        <div className="meta-card">
          <div className="meta-label">Recipe Target</div>
          <div className="meta-value">Ordinary Consommé</div>
        </div>
        <div className="meta-card">
          <div className="meta-label">Yield Volume</div>
          <div className="meta-value">Four Quarts (4L)</div>
        </div>
        <div className="meta-card">
          <div className="meta-label">Execution Time</div>
          <div className="meta-value">4 - 5 Hours Simmer</div>
        </div>
      </section>

      <main className="recipe-body">
        <section>
          <h2>Ingredients</h2>
          <ul className="ingredients-list">
            <li>
              <span>Shin of Beef</span>
              <span className="quantity">3 lbs</span>
            </li>
            <li>
              <span>Lean Beef</span>
              <span className="quantity">3 lbs</span>
            </li>
            <li>
              <span>Fowls&apos; Carcases</span>
              <span className="quantity">1.5 lbs</span>
            </li>
            <li>
              <span>Carrots</span>
              <span className="quantity">1 lb</span>
            </li>
            <li>
              <span>Turnips</span>
              <span className="quantity">1 lb</span>
            </li>
            <li>
              <span>Leeks</span>
              <span className="quantity">0.5 lb</span>
            </li>
            <li>
              <span>Celery</span>
              <span className="quantity">1 stick</span>
            </li>
            <li>
              <span>Parsnips</span>
              <span className="quantity">0.5 lb</span>
            </li>
            <li>
              <span>Medium Onion (w/ 1 Clove)</span>
              <span className="quantity">1 unit</span>
            </li>
            <li>
              <span>Grey Salt</span>
              <span className="quantity">0.5 oz</span>
            </li>
            <li>
              <span>Water</span>
              <span className="quantity">5 Quarts</span>
            </li>
          </ul>
        </section>

        <section>
          <h2>Preparation Protocol</h2>
          <ol className="instructions-list">
            <li>
              String the beef together, place into a stock-pot with poultry carcases, 5 quarts of
              water, and grey salt.
            </li>
            <li>
              Heat over moderate fire, stirring occasionally. Do not let it boil too quickly to
              ensure proper albumin coagulation.
            </li>
            <li>
              Remove the scum as it forms. Add a little cold water before boiling point to force out
              remaining scum.
            </li>
            <li>Add the vegetable garnishing, remove scum, and wipe the stock-pot edge clean.</li>
            <li>Move to a corner of the fire and simmer slowly for 4 to 5 hours.</li>
            <li>
              Remove from heat, add half a pint of cold water, rest briefly, skim grease, and strain
              through a fine strainer.
            </li>
          </ol>
        </section>
      </main>
    </div>
  )
}

function PlaceholderPage({ title }) {
  return (
    <div className="content-wrapper">
      <h1 className="project-title">
        {title} <span className="accent">.</span>
      </h1>
      <div className="card card-left">
        <h3>Section Coming Soon</h3>
        <p>
          This section is part of the React port and is reserved for upcoming data visualizations and
          domain-specific content.
        </p>
      </div>
    </div>
  )
}

function MainContent({ activeKey }) {
  if (activeKey === 'recipes') {
    return <RecipePage />
  }

  if (activeKey !== 'introduction') {
    const item = menuItems.find((entry) => entry.key === activeKey)
    return <PlaceholderPage title={item?.label ?? 'L\'atelier'} />
  }

  return <IntroductionPage />
}

function App() {
  const [activeKey, setActiveKey] = useState('introduction')
  const { user, loading, login, logout, isAuthenticated } = useAuth()

  if (loading) {
    return (
      <div className="login-shell">
        <div className="login-card">
          <p style={{ textAlign: 'center', color: 'var(--text-muted)' }}>Loading…</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <LoginPage onLogin={login} />
  }

  return (
    <div className="app-shell">
      <Sidebar activeKey={activeKey} onSelect={setActiveKey} user={user} onLogout={logout} />
      <main className="main-content">
        <MainContent activeKey={activeKey} />
      </main>
    </div>
  )
}

export default App;
