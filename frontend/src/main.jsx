import RealWasteMap from './RealWasteMap';
import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';
import AiIntelligence from './AiIntelligence';

const API = 'http://127.0.0.1:8000';

const NAV_ITEMS = [
  { id: 'command', label: 'Command Center', icon: '⌂' },
  { id: 'bins', label: 'Smart Bins', icon: '◉' },
  { id: 'reports', label: 'Citizen Reports', icon: '▤' },
  { id: 'ai', label: 'AI Intelligence', icon: '✦' },
  { id: 'operations', label: 'Operations', icon: '↗' },
  { id: 'circular', label: 'Circular Hub', icon: '♻' },
  { id: 'security', label: 'Security', icon: '◈' },
];

function getPriority(fill) {
  if (fill >= 90) return 'CRITICAL';
  if (fill >= 70) return 'HIGH';
  if (fill >= 45) return 'MEDIUM';
  return 'LOW';
}

function getPriorityClass(priority) {
  return priority.toLowerCase();
}

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setLoading(true);

    try {
      const body = new URLSearchParams();
      body.append('username', username);
      body.append('password', password);

      const loginResponse = await fetch(`${API}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body,
      });

      const loginData = await loginResponse.json();

      if (!loginResponse.ok) {
        throw new Error(loginData.detail || 'Login failed');
      }

      localStorage.setItem('access_token', loginData.access_token);

      const meResponse = await fetch(`${API}/api/auth/me`, {
        headers: {
          Authorization: `Bearer ${loginData.access_token}`,
        },
      });

      const user = await meResponse.json();

      if (!meResponse.ok) {
        throw new Error(user.detail || 'Unable to verify user');
      }

      onLogin(user);
    } catch (error) {
      localStorage.removeItem('access_token');
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-screen">
      <div className="login-grid"></div>

      <section className="login-panel">
        <div className="brand-mark">♻</div>

        <p className="eyebrow">CSE7102 • PRJ_628</p>

        <h1>
          Smart City
          <span>Waste Command Center</span>
        </h1>

        <p className="login-description">
          Intelligent monitoring, prediction, collection and material recovery
          in one operational platform.
        </p>

        <div className="login-status">
          <span className="status-dot"></span>
          SYSTEM ONLINE
        </div>

        <form onSubmit={handleSubmit}>
          <label>USERNAME</label>
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            placeholder="Enter username"
            autoComplete="username"
            required
          />

          <label>PASSWORD</label>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Enter password"
            autoComplete="current-password"
            required
          />

          {error && <div className="login-error">{error}</div>}

          <button className="primary-action" type="submit" disabled={loading}>
            {loading ? 'AUTHENTICATING...' : 'ENTER COMMAND CENTER →'}
          </button>
        </form>

        <div className="login-footer">
          <span>JWT SECURITY</span>
          <span>ROLE BASED ACCESS</span>
          <span>AUDIT LOGGING</span>
        </div>
      </section>
    </main>
  );
}

function Sidebar({ active, setActive, user, onLogout }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">♻</div>
        <div>
          <strong>PRJ_628</strong>
          <span>WASTE COMMAND</span>
        </div>
      </div>

      <div className="sidebar-section">
        <span className="sidebar-title">OPERATIONS</span>

        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            className={`nav-button ${active === item.id ? 'active' : ''}`}
            onClick={() => setActive(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </div>

      <div className="sidebar-bottom">
        <div className="operator-card">
          <div className="operator-avatar">
            {user.username.slice(0, 1).toUpperCase()}
          </div>

          <div>
            <strong>{user.username}</strong>
            <span>{user.role}</span>
          </div>
        </div>

        <button className="logout-button" onClick={onLogout}>
          Sign out
        </button>
      </div>
    </aside>
  );
}

function TopBar({ user, onRefresh, loading }) {
  return (
    <header className="topbar">
      <div>
        <span className="live-indicator">
          <span className="status-dot"></span>
          LIVE OPERATIONS
        </span>
        <span className="topbar-separator">/</span>
        <span className="topbar-role">{user.role} ACCESS</span>
      </div>

      <button className="refresh-button" onClick={onRefresh}>
        {loading ? 'SYNCING...' : '↻ SYNC DATA'}
      </button>
    </header>
  );
}

function StatCard({ label, value, suffix, detail, alert }) {
  return (
    <div className={`stat-card ${alert ? 'alert-card' : ''}`}>
      <div className="stat-top">
        <span>{label}</span>
        {alert && <span className="tiny-alert">ACTION</span>}
      </div>

      <div className="stat-value">
        {value}
        {suffix && <small>{suffix}</small>}
      </div>

      <span className="stat-detail">{detail}</span>
    </div>
  );
}

function NetworkMap({ bins, selectedBin, onSelect }) {
  const positions = useMemo(() => {
    if (!bins.length) return {};

    const lats = bins.map((bin) => Number(bin.latitude) || 0);
    const lngs = bins.map((bin) => Number(bin.longitude) || 0);

    const minLat = Math.min(...lats);
    const maxLat = Math.max(...lats);
    const minLng = Math.min(...lngs);
    const maxLng = Math.max(...lngs);

    const latRange = maxLat - minLat || 1;
    const lngRange = maxLng - minLng || 1;

    const result = {};

    bins.forEach((bin) => {
      const lat = Number(bin.latitude) || 0;
      const lng = Number(bin.longitude) || 0;

      const left = 12 + ((lng - minLng) / lngRange) * 76;
      const top = 80 - ((lat - minLat) / latRange) * 62;

      result[bin.id] = {
        left: `${Math.min(88, Math.max(8, left))}%`,
        top: `${Math.min(84, Math.max(10, top))}%`,
      };
    });

    return result;
  }, [bins]);

  return (
    <div className="network-map">
      <div className="map-grid"></div>

      <div className="map-road road-a"></div>
      <div className="map-road road-b"></div>
      <div className="map-road road-c"></div>

      <div className="map-label map-label-a">WARD NETWORK</div>
      <div className="map-label map-label-b">COLLECTION ZONE</div>
      <div className="map-label map-label-c">RECOVERY CORRIDOR</div>

      {bins.map((bin) => {
        const priority = getPriority(bin.fill_level);
        const selected = selectedBin?.id === bin.id;

        return (
          <button
            key={bin.id}
            className={`bin-marker ${getPriorityClass(priority)} ${
              selected ? 'selected' : ''
            }`}
            style={positions[bin.id]}
            onClick={() => onSelect(bin)}
            title={`${bin.code} — ${bin.fill_level}%`}
          >
            <span className="marker-core"></span>
            <span className="marker-pulse"></span>
          </button>
        );
      })}

      <div className="map-legend">
        <span><i className="legend-dot critical"></i> Critical</span>
        <span><i className="legend-dot high"></i> High</span>
        <span><i className="legend-dot medium"></i> Medium</span>
        <span><i className="legend-dot low"></i> Low</span>
      </div>

      <div className="map-corner">
        <span>NETWORK STATUS</span>
        <strong>OPERATIONAL</strong>
      </div>
    </div>
  );
}

function SelectedBin({ bin }) {
  if (!bin) {
    return (
      <div className="empty-selection">
        <span className="empty-icon">◉</span>
        <strong>Select a bin</strong>
        <span>Click any marker on the network map.</span>
      </div>
    );
  }

  const priority = getPriority(bin.fill_level);
  const remaining = Math.max(0, 100 - Number(bin.fill_level));

  return (
    <div className="selected-bin">
      <div className="selected-bin-head">
        <div>
          <span className="eyebrow">SELECTED ASSET</span>
          <h3>{bin.code}</h3>
          <span className="ward-label">{bin.ward}</span>
        </div>

        <span className={`priority-badge ${getPriorityClass(priority)}`}>
          {priority}
        </span>
      </div>

      <div className="fill-display">
        <div
          className="fill-ring"
          style={{ '--fill': `${bin.fill_level}%` }}
        >
          <div className="fill-ring-inner">
            <strong>{bin.fill_level}</strong>
            <span>% FULL</span>
          </div>
        </div>

        <div className="fill-info">
          <span>CAPACITY</span>
          <strong>{bin.capacity_kg} kg</strong>

          <span>AVAILABLE</span>
          <strong>{Math.round((remaining / 100) * bin.capacity_kg)} kg</strong>

          <span>RECOMMENDED ACTION</span>
          <strong className="action-text">
            {priority === 'CRITICAL'
              ? 'COLLECT NOW'
              : priority === 'HIGH'
              ? 'SCHEDULE'
              : 'MONITOR'}
          </strong>
        </div>
      </div>

      <div className="asset-meta">
        <div>
          <span>LATITUDE</span>
          <strong>{Number(bin.latitude).toFixed(4)}</strong>
        </div>

        <div>
          <span>LONGITUDE</span>
          <strong>{Number(bin.longitude).toFixed(4)}</strong>
        </div>
      </div>
    </div>
  );
}

function CommandCenter({ bins, reports, selectedBin, setSelectedBin }) {
  const critical = bins.filter((bin) => bin.fill_level >= 90).length;
  const high = bins.filter(
    (bin) => bin.fill_level >= 70 && bin.fill_level < 90
  ).length;

  const average = bins.length
    ? Math.round(
        bins.reduce((total, bin) => total + Number(bin.fill_level), 0) /
          bins.length
      )
    : 0;

  const recentReports = [...reports].reverse().slice(0, 3);

  const highestBin = [...bins].sort(
    (a, b) => Number(b.fill_level) - Number(a.fill_level)
  )[0];

  return (
    <>
      <section className="hero">
        <div>
          <p className="eyebrow">CITY OPERATIONS / REAL-TIME OVERVIEW</p>
          <h1>
            Waste Network
            <span>Command Center</span>
          </h1>
          <p>
            Monitor collection pressure, identify priority assets and move
            recoverable material through the circular economy.
          </p>
        </div>

        <div className="hero-signal">
          <span className="signal-label">NETWORK HEALTH</span>
          <strong>{critical > 0 ? 'ATTENTION REQUIRED' : 'STABLE'}</strong>
          <span>
            {critical} critical asset{critical === 1 ? '' : 's'} detected
          </span>
        </div>
      </section>

      <section className="stats-grid">
        <StatCard
          label="MONITORED BINS"
          value={bins.length}
          detail="Active network assets"
        />

        <StatCard
          label="CRITICAL PRESSURE"
          value={critical}
          detail={`${high} additional high-priority assets`}
          alert={critical > 0}
        />

        <StatCard
          label="NETWORK FILL"
          value={average}
          suffix="%"
          detail="Average current fill level"
        />

        <StatCard
          label="CITIZEN SIGNALS"
          value={reports.length}
          detail="Reported waste incidents"
        />
      </section>

      <section className="main-grid">
        <div className="panel map-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">LIVE NETWORK</span>
              <h2>City waste map</h2>
            </div>

            <span className="panel-status">
              <span className="status-dot"></span>
              {bins.length} ASSETS
            </span>
          </div>

          <RealWasteMap bins={bins} />

        </div>
        <div className="panel intelligence-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">ASSET INTELLIGENCE</span>
              <h2>Bin diagnostics</h2>
            </div>
          </div>

          <SelectedBin bin={selectedBin || highestBin} />
        </div>
      </section>

      <section className="lower-grid">
        <div className="panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">OPERATIONAL SIGNALS</span>
              <h2>Priority queue</h2>
            </div>
          </div>

          <div className="priority-list">
            {[...bins]
              .sort((a, b) => b.fill_level - a.fill_level)
              .map((bin) => {
                const priority = getPriority(bin.fill_level);

                return (
                  <button
                    className="priority-row"
                    key={bin.id}
                    onClick={() => setSelectedBin(bin)}
                  >
                    <div className="priority-rank">
                      {String(bin.id).padStart(2, '0')}
                    </div>

                    <div className="priority-main">
                      <strong>{bin.code}</strong>
                      <span>{bin.ward}</span>
                    </div>

                    <div className="priority-meter">
                      <div>
                        <span>{bin.fill_level}%</span>
                        <span>{priority}</span>
                      </div>
                      <div className="meter-track">
                        <div
                          className={`meter-fill ${getPriorityClass(
                            priority
                          )}`}
                          style={{ width: `${bin.fill_level}%` }}
                        ></div>
                      </div>
                    </div>

                    <span className={`priority-badge ${getPriorityClass(priority)}`}>
                      {priority}
                    </span>
                  </button>
                );
              })}
          </div>
        </div>

        <div className="panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">CITIZEN SIGNALS</span>
              <h2>Recent reports</h2>
            </div>

            <span className="count-chip">{reports.length}</span>
          </div>

          <div className="report-feed">
            {recentReports.length === 0 ? (
              <div className="empty-feed">No reports available.</div>
            ) : (
              recentReports.map((report) => (
                <article className="report-item" key={report.id}>
                  <div className="report-icon">!</div>

                  <div className="report-content">
                    <div>
                      <strong>{report.waste_type}</strong>
                      <span>{report.ward}</span>
                    </div>
                    <p>{report.description}</p>
                    <small>{report.status}</small>
                  </div>
                </article>
              ))
            )}
          </div>
        </div>
      </section>

      <section className="module-strip">
        <div className="module-intro">
          <span className="eyebrow">PRJ_628 ENGINE</span>
          <h2>Integrated intelligence</h2>
          <p>
            One operational layer connecting monitoring, AI, logistics,
            recovery and security.
          </p>
        </div>

        <div className="module-item">
          <span>01</span>
          <strong>ML FORECAST</strong>
          <small>Waste generation prediction</small>
        </div>

        <div className="module-item">
          <span>02</span>
          <strong>DL VISION</strong>
          <small>Waste image classification</small>
        </div>

        <div className="module-item">
          <span>03</span>
          <strong>ROUTE ENGINE</strong>
          <small>Priority-based routing</small>
        </div>

        <div className="module-item">
          <span>04</span>
          <strong>RECOVERY HUB</strong>
          <small>Recycler matching</small>
        </div>

        <div className="module-item">
          <span>05</span>
          <strong>SECURITY</strong>
          <small>JWT + audit trails</small>
        </div>
      </section>
    </>
  );
}

function PlaceholderView({ id }) {
  const data = {
    bins: [
      'SMART BIN CONTROL',
      'Detailed bin telemetry, fill updates and collection actions will live here.',
    ],
    reports: [
      'CITIZEN REPORT CENTER',
      'Report review, status management and operational response will live here.',
    ],
    ai: [
      'AI INTELLIGENCE LAB',
      'ML waste forecasting and DL image classification will be connected here.',
    ],
    operations: [
      'COLLECTION OPERATIONS',
      'Tasks and route optimization will be visualized here.',
    ],
    circular: [
      'CIRCULAR ECONOMY HUB',
      'Recoverable materials, recycler matching and transactions will live here.',
    ],
    security: [
      'SECURITY CENTER',
      'Authentication, role permissions and audit activity will be visualized here.',
    ],
  };

  const [title, description] = data[id] || [
    'COMMAND CENTER',
    'Operational dashboard',
  ];

  return (
    <section className="placeholder-view">
      <span className="eyebrow">MODULE INITIALIZED</span>
      <h1>{title}</h1>
      <p>{description}</p>
      <div className="placeholder-box">
        <span>MODULE READY</span>
        <strong>API INTEGRATION NEXT</strong>
      </div>
    </section>
  );
}

function App() {
  const [user, setUser] = useState(null);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [activeView, setActiveView] = useState('command');
  const [bins, setBins] = useState([]);
  const [reports, setReports] = useState([]);
  const [selectedBin, setSelectedBin] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dataError, setDataError] = useState('');

  useEffect(() => {
    async function checkAuth() {
      const token = localStorage.getItem('access_token');

      if (!token) {
        setCheckingAuth(false);
        return;
      }

      try {
        const response = await fetch(`${API}/api/auth/me`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          localStorage.removeItem('access_token');
          setUser(null);
        } else {
          setUser(await response.json());
        }
      } catch {
        localStorage.removeItem('access_token');
        setUser(null);
      } finally {
        setCheckingAuth(false);
      }
    }

    checkAuth();
  }, []);

  async function loadDashboard() {
    const token = localStorage.getItem('access_token');

    if (!token) return;

    setLoading(true);

    try {
      const headers = {
        Authorization: `Bearer ${token}`,
      };

      const [binsResponse, reportsResponse] = await Promise.all([
        fetch(`${API}/api/bins`, { headers }),
        fetch(`${API}/api/reports`, { headers }),
      ]);

      if (!binsResponse.ok || !reportsResponse.ok) {
        throw new Error('Unable to synchronize operational data');
      }

      const binData = await binsResponse.json();
      const reportData = await reportsResponse.json();

      setBins(binData);
      setReports(reportData);
      setDataError('');

      if (!selectedBin && binData.length) {
        const highest = [...binData].sort(
          (a, b) => b.fill_level - a.fill_level
        )[0];

        setSelectedBin(highest);
      }
    } catch (error) {
      setDataError(error.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (user) {
      loadDashboard();
    }
  }, [user]);

  function logout() {
    localStorage.removeItem('access_token');
    setUser(null);
    setBins([]);
    setReports([]);
    setSelectedBin(null);
  }

  if (checkingAuth) {
    return (
      <main className="loading-screen">
        <div className="loading-orbit"></div>
        <span>INITIALIZING COMMAND CENTER</span>
      </main>
    );
  }

  if (!user) {
    return <Login onLogin={setUser} />;
  }

  return (
    <div className="app-shell">
      <Sidebar
        active={activeView}
        setActive={setActiveView}
        user={user}
        onLogout={logout}
      />

      <div className="content-shell">
        <TopBar
          user={user}
          onRefresh={loadDashboard}
          loading={loading}
        />

        {dataError && (
          <div className="data-error">
            <strong>SYNC ERROR</strong>
            <span>{dataError}</span>
          </div>
        )}

        <main className="dashboard">
          {activeView === 'command' ? (
            <CommandCenter
              bins={bins}
              reports={reports}
              selectedBin={selectedBin}
              setSelectedBin={setSelectedBin}
            />
          ) : activeView === 'ai' ? (
            <AiIntelligence />
          ) : (
            <PlaceholderView id={activeView} />
          )}
        </main>
      </div>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
