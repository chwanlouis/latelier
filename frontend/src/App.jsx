import { useMemo, useState } from 'react'
import './App.css'

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
  // 👇 新增外部控制台跳轉選項
  { key: 'graphdb-console', label: '🗄️ GraphDB Console' }, 
]

const recipeSearchItems = [
  'I - Ordinary or White Consommé',
  'II - Clarified Consommé for Clear Soups',
  'Fonds de Cuisine (No. 3)',
  'Guide to Modern Cookery (Page 4)',
]

function Sidebar({ activeKey, onSelect }) {
  const handleMenuClick = (key) => {
    if (key === 'graphdb-console') {
      // 获取当前 EC2 的公网 IP / 域名，並將連接埠動態替換為 Neo4j Web 埠 7474
      const currentHost = window.location.hostname;
      window.open(`http://${currentHost}:7474`, '_blank'); // _blank 會在新分頁開啟，不影響目前的 React App
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
              onClick={() => handleMenuClick(item.key)} // 👇 修改為觸發自訂跳轉邏輯
            >
              {item.label}
            </button>
          </li>
        ))}
      </ul>
      <div className="sidebar-footer">© 2026 L&apos;atelier Project</div>
    </nav>
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
              onKeyDown={onSearchKeyDown}
            />
          </div>
        </div>
      </header>
    </div>
  )
}
