// ====================================================================
// RiskGuard: Academic Risk Intelligence & Intervention System
// Full React 18 Application matching reference screenshots
// ====================================================================

const { useState, useEffect, useRef } = React;

// Simple inline SVG Icons matching Lucide style
const Icons = {
  Shield: () => (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      <path d="m9 12 2 2 4-4"/>
    </svg>
  ),
  Dashboard: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect width="7" height="9" x="3" y="3" rx="1"/>
      <rect width="7" height="5" x="14" y="3" rx="1"/>
      <rect width="7" height="9" x="14" y="12" rx="1"/>
      <rect width="7" height="5" x="3" y="16" rx="1"/>
    </svg>
  ),
  Users: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
      <circle cx="9" cy="7" r="4"/>
      <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
      <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
    </svg>
  ),
  Bell: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/>
      <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>
    </svg>
  ),
  Insights: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/>
      <path d="M2 12h20"/>
    </svg>
  ),
  Classroom: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"/>
      <path d="M6 6h10"/>
      <path d="M6 10h10"/>
    </svg>
  ),
  Statistics: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" x2="18" y1="20" y2="10"/>
      <line x1="12" x2="12" y1="20" y2="4"/>
      <line x1="6" x2="6" y1="20" y2="14"/>
    </svg>
  ),
  Logout: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
      <polyline points="16 17 21 12 16 7"/>
      <line x1="21" x2="9" y1="12" y2="12"/>
    </svg>
  ),
  Search: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8"/>
      <line x1="21" x2="16.65" y1="21" y2="16.65"/>
    </svg>
  ),
  Plus: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" x2="12" y1="5" y2="19"/>
      <line x1="5" x2="19" y1="12" y2="12"/>
    </svg>
  ),
  Mail: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect width="20" height="16" x="2" y="4" rx="2"/>
      <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
    </svg>
  ),
  ChevronDown: () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="6 9 12 15 18 9"/>
    </svg>
  ),
  ChevronUp: () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="18 15 12 9 6 15"/>
    </svg>
  ),
  Close: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" x2="6" y1="6" y2="18"/>
      <line x1="6" x2="18" y1="6" y2="18"/>
    </svg>
  )
};

// ================= API SERVICE =================
const API = {
  login: async (username, password) => {
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || 'Invalid Username or Password');
    }

    return data;
  },

  register: async (formData) => {
    const res = await fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || 'Account already exists.');
    }

    return data;
  },

  getCurrentUser: async () => {
    const res = await fetch('/api/me');

    if (!res.ok) {
      return null;
    }

    const data = await res.json();
    return data.user;
  },

  logout: async () => {
    await fetch('/api/logout', {
      method: 'POST'
    });
  },

  getStudents: async (search = '', risk = '', dept = '') => {
    const params = new URLSearchParams();

    if (search) {
      params.append('search', search);
    }

    if (risk && risk !== 'All') {
      params.append('risk_level', risk);
    }

    if (dept && dept !== 'All') {
      params.append('department', dept);
    }

    const res = await fetch(`/api/students?${params.toString()}`);

    return await res.json();
  },

  addStudent: async (studentData) => {
    const res = await fetch('/api/students', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(studentData)
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(
        data.error || 'Failed to save student.'
      );
    }

    return data;
  },

  // ==========================================
  // UPLOAD CSV / EXCEL DATASET
  // ==========================================
  uploadDataset: async (file) => {
    const formData = new FormData();

    formData.append('file', file);

    const res = await fetch('/api/dataset/upload', {
      method: 'POST',
      body: formData
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(
        data.message ||
        data.error ||
        'Failed to upload dataset.'
      );
    }

    return data;
  },

  deleteStudent: async (id) => {
    const res = await fetch(
      `/api/students/${id}`,
      {
        method: 'DELETE'
      }
    );

    return await res.json();
  },

  getStatistics: async () => {
    const res = await fetch('/api/statistics');

    return await res.json();
  },

  getAlerts: async () => {
    const res = await fetch('/api/alerts');

    return await res.json();
  },

  getStudentAlerts: async (email = '') => {
    const res = await fetch(
      `/api/student/alerts?email=${encodeURIComponent(email)}`
    );

    return await res.json();
  },

  getStudentStats: async (email = '') => {
    const res = await fetch(
      `/api/student/statistics?email=${encodeURIComponent(email)}`
    );

    return await res.json();
  },

  getAdminStats: async () => {
    const res = await fetch('/api/admin/statistics');

    return await res.json();
  },

  getFacultyMembers: async () => {
    const res = await fetch('/api/admin/faculty');

    return await res.json();
  },

  addFaculty: async (formData) => {
    const res = await fetch('/api/admin/faculty', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(
        data.error || 'Failed to add faculty member'
      );
    }

    return data;
  },

  
getModelInsights: async () => {
  const res = await fetch('/api/prediction/insights', {
    method: 'GET',
    cache: 'no-store',
    credentials: 'same-origin',
    headers: {
      'Accept': 'application/json'
    }
  });

  if (!res.ok) {
    throw new Error(
      `Model Insights API failed: HTTP ${res.status}`
    );
  }

  return await res.json();
},


  getClassroomStatus: async () => {
    const res = await fetch(
      '/api/google-classroom/status'
    );

    return await res.json();
  },

  sendEmailRetry: async (alertId) => {
    const res = await fetch(
      `/api/alerts/${alertId}/send-email`,
      {
        method: 'POST'
      }
    );

    return await res.json();
  }
};

// ================= RISK BADGE COMPONENT =================
function RiskBadge({ level }) {
  let badgeClass = 'low';
  let label = 'Low Risk';

  if (!level) return null;
  if (level.includes('High')) {
    badgeClass = 'high';
    label = 'High Risk';
  } else if (level.includes('Medium')) {
    badgeClass = 'medium';
    label = 'Medium Risk';
  }

  return (
    <span className={`risk-badge ${badgeClass}`}>
      <span className="dot"></span>
      {label}
    </span>
  );
}

// ================= STAT CARD COMPONENT =================

// ================= AUTH LEFT PANEL =================
function AuthLeftPanel() {
  return (
    <div className="auth-left">
      <div className="auth-brand">
        <Icons.Shield />
        <span className="auth-brand-name">RiskGuard</span>
      </div>

      <div className="auth-hero">
        <h1 className="auth-hero-title">
          Predict. Explain.<br />
          Intervene.
        </h1>
        <p className="auth-hero-desc">
          AI-powered academic risk prediction with explainable insights,
          personalized interventions and automated alerts for higher education.
        </p>
      </div>

      <div className="auth-pipeline">
        Predict &rarr; Explain &rarr; Recommend &rarr; Alert &rarr; Intervene &rarr; Monitor
      </div>
    </div>
  );
}

// ================= LOGIN PAGE =================
function LoginPage({ onLoginSuccess, onNavigateRegister }) {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await API.login(identifier, password);
      onLoginSuccess(res.user);
    } catch (err) {
      setError(err.message || 'Invalid Username or Password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <AuthLeftPanel />
      <div className="auth-right">
        <div className="auth-form-card">
          <div className="auth-form-header">
            <h2 className="auth-form-title">Welcome back</h2>
            <p className="auth-form-subtitle">Sign in to your dashboard</p>
          </div>

          {error && <div className="alert-box alert-error">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Email</label>
              <input
                type="text"
                className="form-input"
                placeholder="Enter your email or username"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                type="password"
                className="form-input"
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          <div className="auth-footer">
            New here?{' '}
            <button type="button" onClick={onNavigateRegister}>
              Create an account
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ================= CREATE ACCOUNT PAGE =================
function RegisterPage({ onNavigateLogin }) {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('Student');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);
    try {
      await API.register({
        full_name: fullName,
        email: email,
        password: password,
        role: role
      });
      setSuccess('Account Created Successfully');
      setTimeout(() => {
        onNavigateLogin();
      }, 1500);
    } catch (err) {
      setError(err.message || 'Account already exists.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <AuthLeftPanel />
      <div className="auth-right">
        <div className="auth-form-card">
          <div className="auth-form-header">
            <h2 className="auth-form-title">Create account</h2>
            <p className="auth-form-subtitle">Register to get started</p>
          </div>

          {error && <div className="alert-box alert-error">{error}</div>}
          {success && <div className="alert-box alert-success">{success}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Full name</label>
              <input
                type="text"
                className="form-input"
                placeholder="Enter full name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Email</label>
              <input
                type="text"
                className="form-input"
                placeholder="Enter email or username"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                type="password"
                className="form-input"
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Role</label>
              <select
                className="form-select"
                value={role}
                onChange={(e) => setRole(e.target.value)}
              >
                <option value="Student">Student</option>
                <option value="Faculty">Faculty / Mentor</option>
                <option value="Admin">Admin</option>
              </select>
            </div>

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Creating account...' : 'Create account'}
            </button>
          </form>

          <div className="auth-footer">
            Already have an account?{' '}
            <button type="button" onClick={onNavigateLogin}>
              Sign in
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ================= SIDEBAR COMPONENT =================
function Sidebar({ activeTab, onSelectTab, currentUser, onLogout }) {
  const role = currentUser?.role || 'Faculty';

  // Navigation Items by Role
  const getNavItems = () => {
    if (role === 'Faculty') {
      return [
        { id: 'dashboard', label: 'Dashboard', icon: Icons.Dashboard },
        { id: 'students', label: 'Students', icon: Icons.Users },
        { id: 'alerts', label: 'Alert History', icon: Icons.Bell },
        { id: 'insights', label: 'Model Insights', icon: Icons.Insights },
        { id: 'classroom', label: 'Google Classroom', icon: Icons.Classroom },
        { id: 'statistics', label: 'Statistics', icon: Icons.Statistics }
      ];
    } else if (role === 'Student') {
      return [
        { id: 'dashboard', label: 'Dashboard', icon: Icons.Dashboard },
        { id: 'performance', label: 'My Performance', icon: Icons.Statistics },
        { id: 'alerts', label: 'Alert History', icon: Icons.Bell },
        { id: 'statistics', label: 'Statistics', icon: Icons.Insights },
        { id: 'classroom', label: 'Google Classroom', icon: Icons.Classroom }
      ];
    } else {
      // Admin
      return [
        { id: 'dashboard', label: 'Dashboard', icon: Icons.Dashboard },
        { id: 'students', label: 'Students', icon: Icons.Users },
        { id: 'faculty', label: 'Faculty', icon: Icons.Users },
        { id: 'risk_monitoring', label: 'Risk Monitoring', icon: Icons.Insights },
        { id: 'statistics', label: 'Statistics', icon: Icons.Statistics },
        { id: 'alerts', label: 'Alerts', icon: Icons.Bell }
      ];
    }
  };

  const navItems = getNavItems();

  return (
    <aside className="sidebar">
      <div>
        <div className="sidebar-brand">
          <div className="sidebar-logo-row">
            <Icons.Shield />
            <span>RiskGuard</span>
          </div>
          <div className="sidebar-subtitle">Academic Risk Intelligence</div>
        </div>

        <div className="sidebar-divider"></div>

        <ul className="nav-list">
          {navItems.map((item) => {
            const IconComponent = item.icon;
            const isActive = activeTab === item.id;
            return (
              <li key={item.id}>
                <button
                  className={`nav-link ${isActive ? 'active' : ''}`}
                  onClick={() => onSelectTab(item.id)}
                >
                  <IconComponent />
                  <span>{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </div>

      <div className="sidebar-bottom">
        <div className="user-profile-info">
          <div className="user-name">{currentUser?.username || 'User'}</div>
          <div className="user-role">{currentUser?.role || 'Role'}</div>
        </div>
        <button className="signout-btn" onClick={onLogout}>
          <Icons.Logout />
          <span>Sign out</span>
        </button>
      </div>
    </aside>
  );
}

// ================= DOUGHNUT CHART =================
function DoughnutRiskChart({ data }) {
  const canvasRef = useRef(null);
  const chartInstance = useRef(null);

  useEffect(() => {
    if (!canvasRef.current || !data) return;

    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = canvasRef.current.getContext('2d');
    chartInstance.current = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: data.labels,
        datasets: [{
          data: data.data,
          backgroundColor: data.colors,
          borderWidth: 2,
          borderColor: '#FFFFFF'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '68%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 12,
              padding: 16,
              font: { family: 'Inter', size: 12 }
            }
          }
        }
      }
    });

    return () => {
      if (chartInstance.current) chartInstance.current.destroy();
    };
  }, [data]);

  return <canvas ref={canvasRef} />;
}

// ================= BAR CHART =================
function DepartmentBarChart({ data }) {
  const canvasRef = useRef(null);
  const chartInstance = useRef(null);

  useEffect(() => {
    if (!canvasRef.current || !data) return;

    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = canvasRef.current.getContext('2d');
    chartInstance.current = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [{
          label: 'Students at Risk',
          data: data.data,
          backgroundColor: '#C48A47',
          borderRadius: 4,
          barThickness: 36
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1,
              font: { family: 'Inter', size: 11 }
            },
            grid: {
              color: '#F3F4F6',
              borderDash: [4, 4]
            }
          },
          x: {
            grid: { display: false },
            ticks: { font: { family: 'Inter', size: 11 } }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });

    return () => {
      if (chartInstance.current) chartInstance.current.destroy();
    };
  }, [data]);

  return <canvas ref={canvasRef} />;
}

function StatisticsPageView() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const chartRefs = useRef({});
  const chartInstances = useRef({});

  useEffect(() => {
    let cancelled = false;

    async function loadStatistics() {
      try {
        setLoading(true);
        setError('');

        const response = await fetch('/api/admin/statistics');

        if (!response.ok) {
          throw new Error('Unable to load statistics from the server.');
        }

        const result = await response.json();

        if (!cancelled) setStats(result);
      } catch (err) {
        if (!cancelled) {
          setError(err.message || 'Failed to load statistics.');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadStatistics();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!stats || typeof Chart === 'undefined') return;

    Object.values(chartInstances.current).forEach(chart => {
      if (chart) chart.destroy();
    });
    chartInstances.current = {};

    const departments = stats.department_statistics || [];
    const departmentRisk = stats.department_risk_statistics || [];

    const performanceCanvas = chartRefs.current.performance;
    if (performanceCanvas) {
      chartInstances.current.performance = new Chart(
        performanceCanvas.getContext('2d'),
        {
          type: 'bar',
          data: {
            labels: departments.map(d => d.department || 'Unknown'),
            datasets: [{
              label: 'Average Academic Performance (%)',
              data: departments.map(d => Number(d.avg_performance) || 0),
              backgroundColor: '#285743',
              borderRadius: 5
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                max: 100,
                title: { display: true, text: 'Performance (%)' }
              },
              x: { grid: { display: false } }
            },
            plugins: { legend: { display: false } }
          }
        }
      );
    }

    const distributionCanvas = chartRefs.current.distribution;
    if (distributionCanvas) {
      chartInstances.current.distribution = new Chart(
        distributionCanvas.getContext('2d'),
        {
          type: 'pie',
          data: {
            labels: departments.map(d => d.department || 'Unknown'),
            datasets: [{
              label: 'Students',
              data: departments.map(d => Number(d.students_count) || 0),
              backgroundColor: [
                '#285743', '#D9A36C', '#B84A2B',
                '#6B7280', '#537C68', '#C6A15B',
                '#16382C', '#9CA3AF'
              ],
              borderColor: '#FFFFFF',
              borderWidth: 2
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'bottom' }
            }
          }
        }
      );
    }

    const riskCanvas = chartRefs.current.risk;
    if (riskCanvas) {
      chartInstances.current.risk = new Chart(
        riskCanvas.getContext('2d'),
        {
          type: 'bar',
          data: {
            labels: departmentRisk.map(d => d.department || 'Unknown'),
            datasets: [
              {
                label: 'Low Risk',
                data: departmentRisk.map(d => Number(d.low_risk) || 0),
                backgroundColor: '#285743'
              },
              {
                label: 'Medium Risk',
                data: departmentRisk.map(d => Number(d.medium_risk) || 0),
                backgroundColor: '#D9A36C'
              },
              {
                label: 'High Risk',
                data: departmentRisk.map(d => Number(d.high_risk) || 0),
                backgroundColor: '#B84A2B'
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              x: {
                stacked: false,
                grid: { display: false }
              },
              y: {
                beginAtZero: true,
                ticks: { precision: 0 }
              }
            },
            plugins: {
              legend: { position: 'bottom' }
            }
          }
        }
      );
    }

    return () => {
      Object.values(chartInstances.current).forEach(chart => {
        if (chart) chart.destroy();
      });
      chartInstances.current = {};
    };
  }, [stats]);

  if (loading) {
    return <div className="page-container"><p>Loading statistics...</p></div>;
  }

  if (error) {
    return (
      <div className="page-container">
        <h1 className="page-title">Statistics</h1>
        <p role="alert">{error}</p>
        <button
          className="primary-btn"
          onClick={() => window.location.reload()}
        >
          Retry
        </button>
      </div>
    );
  }

  const departments = stats?.department_statistics || [];
  const departmentRisk = stats?.department_risk_statistics || [];

  const average = key => {
    const values = departments
      .map(d => Number(d[key]))
      .filter(value => Number.isFinite(value));

    if (!values.length) return 0;

    return values.reduce((sum, value) => sum + value, 0) / values.length;
  };

  const avgPerformance = Number(stats?.avg_performance);
  const avgAttendance = Number(stats?.avg_attendance);
  const avgCgpa = Number(stats?.avg_cgpa);

  const cards = [
    {
      label: 'TOTAL STUDENTS',
      value: stats?.total_students ?? 0
    },
    {
      label: 'AVG. ATTENDANCE',
      value: `${Number.isFinite(avgAttendance) ? avgAttendance.toFixed(1) : '0.0'}%`
    },
    {
      label: 'AVG. PERFORMANCE',
      value: `${Number.isFinite(avgPerformance) ? avgPerformance.toFixed(1) : '0.0'}%`
    },
    {
      label: 'AVG. CGPA',
      value: Number.isFinite(avgCgpa) ? avgCgpa.toFixed(2) : '0.00'
    }
  ];

  return (
    <div className="page-container">
      <div className="page-header-row">
        <div>
          <h1 className="page-title">Statistics</h1>
          <p className="page-subtitle">
            Department-wise academic performance, student distribution and risk overview
          </p>
        </div>
      </div>

      <div className="stat-cards-grid">
        {cards.map(card => (
          <div className="stat-card" key={card.label}>
            <div className="stat-card-label">{card.label}</div>
            <div className="stat-card-value">{card.value}</div>
          </div>
        ))}
      </div>

      {departments.length === 0 ? (
        <div className="content-card">
          <p>No department statistics are available yet.</p>
        </div>
      ) : (
        <>
          <div className="content-card" style={{ marginTop: 24 }}>
            <h2>Department-wise Academic Performance</h2>
            <p className="page-subtitle">
              Average academic performance percentage for each department
            </p>
            <div style={{ position: 'relative', height: 320, marginTop: 20 }}>
              <canvas ref={el => { chartRefs.current.performance = el; }} />
            </div>
          </div>

          <div
            className="content-card"
            style={{ marginTop: 24 }}
          >
            <h2>Department-wise Student Distribution</h2>
            <p className="page-subtitle">
              Number of students in each department
            </p>
            <div style={{ position: 'relative', height: 340, marginTop: 20 }}>
              <canvas ref={el => { chartRefs.current.distribution = el; }} />
            </div>
          </div>

          <div className="content-card" style={{ marginTop: 24 }}>
            <h2>Department-wise Risk Distribution</h2>
            <p className="page-subtitle">
              Low, medium and high-risk student counts by department
            </p>
            {departmentRisk.length === 0 ? (
              <p>
                Risk-by-department data is not available yet. Complete Step 2 below
                to enable this chart.
              </p>
            ) : (
              <div style={{ position: 'relative', height: 360, marginTop: 20 }}>
                <canvas ref={el => { chartRefs.current.risk = el; }} />
              </div>
            )}
          </div>

          <div className="content-card" style={{ marginTop: 24 }}>
            <h2>Department Summary</h2>
            <div style={{ overflowX: 'auto', marginTop: 16 }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={{ textAlign: 'left', padding: 12 }}>Department</th>
                    <th style={{ textAlign: 'right', padding: 12 }}>Students</th>
                    <th style={{ textAlign: 'right', padding: 12 }}>Avg. Performance</th>
                    <th style={{ textAlign: 'right', padding: 12 }}>Avg. Attendance</th>
                  </tr>
                </thead>
                <tbody>
                  {departments.map((department, index) => (
                    <tr key={`${department.department || 'unknown'}-${index}`}>
                      <td style={{ padding: 12 }}>
                        {department.department || 'Unknown'}
                      </td>
                      <td style={{ textAlign: 'right', padding: 12 }}>
                        {department.students_count ?? 0}
                      </td>
                      <td style={{ textAlign: 'right', padding: 12 }}>
                        {Number(department.avg_performance || 0).toFixed(1)}%
                      </td>
                      <td style={{ textAlign: 'right', padding: 12 }}>
                        {Number(department.avg_attendance || 0).toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}


// ================= FACULTY DASHBOARD =================
function FacultyDashboardView({ stats, onNavigateStudents }) {
  return (
    <div>
      <div className="page-header-row">
        <div>
          <h1 className="page-title">Faculty Dashboard</h1>
          <p className="page-subtitle">Overview of student academic risk across your institution</p>
        </div>
      </div>

      <div className="stat-cards-grid">
        <StatCard label="TOTAL STUDENTS" value={stats?.total_students ?? 4} type="dark" />
        <StatCard label="LOW RISK" value={stats?.low_risk ?? 1} type="green" />
        <StatCard label="MEDIUM RISK" value={stats?.medium_risk ?? 2} type="orange" />
        <StatCard label="HIGH RISK" value={stats?.high_risk ?? 1} type="red" />
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3 className="chart-card-title">Risk Distribution</h3>
          <div className="chart-wrapper">
            {stats?.risk_distribution && <DoughnutRiskChart data={stats.risk_distribution} />}
          </div>
        </div>

        <div className="chart-card">
          <h3 className="chart-card-title">Risk by Department</h3>
          <div className="chart-wrapper">
            {stats?.risk_by_department && <DepartmentBarChart data={stats.risk_by_department} />}
          </div>
        </div>
      </div>
    </div>
  );
}

// ============== STUDENTS PAGE =================
function StudentsPageView({ onOpenAddStudentModal }) {

  const [students, setStudents] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRisk, setFilterRisk] = useState('All');
  const [loading, setLoading] = useState(true);

  // Dataset upload states
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const [uploadError, setUploadError] = useState('');

  // ---------------------------------------------------------
  // Load Students
  // ---------------------------------------------------------
  const loadStudents = async () => {

    setLoading(true);

    try {

      const data = await API.getStudents(
        searchTerm,
        filterRisk
      );

      setStudents(data);

    } catch (err) {

      console.error(err);

    } finally {

      setLoading(false);

    }
  };


  // ---------------------------------------------------------
  // Reload students when search/filter changes
  // ---------------------------------------------------------
  useEffect(() => {

    loadStudents();

  }, [searchTerm, filterRisk]);


  // ---------------------------------------------------------
  // Dataset Upload
  // ---------------------------------------------------------
  const handleDatasetUpload = async (e) => {

    const file = e.target.files?.[0];

    if (!file) {
      return;
    }

    // Clear previous messages
    setUploadMessage('');
    setUploadError('');


    // -------------------------------------------------------
    // Check file extension
    // -------------------------------------------------------

    const fileName = file.name.toLowerCase();

    const validFile =
      fileName.endsWith('.csv') ||
      fileName.endsWith('.xlsx');


    if (!validFile) {

      setUploadError(
        'Please select a CSV or Excel (.xlsx) file.'
      );

      e.target.value = '';

      return;
    }


    // -------------------------------------------------------
    // Start Upload
    // -------------------------------------------------------

    setUploading(true);


    try {

      const result = await API.uploadDataset(file);


      // -----------------------------------------------------
      // Show upload result
      // -----------------------------------------------------

      setUploadMessage(
        `${result.added_students} students uploaded successfully. ` +
        `High Risk: ${result.high_risk}, ` +
        `Medium Risk: ${result.medium_risk}, ` +
        `Low Risk: ${result.low_risk}.`
      );


      // -----------------------------------------------------
      // Refresh Student Table
      // -----------------------------------------------------

      await loadStudents();


    } catch (err) {

      console.error(
        'Dataset upload error:',
        err
      );

      setUploadError(
        err.message ||
        'Dataset upload failed.'
      );

    } finally {

      setUploading(false);

      // Allow same file to be selected again
      e.target.value = '';

    }
  };


  // =========================================================
  // UI
  // =========================================================

  return (

    <div>

      {/* ===================================================
          PAGE HEADER
      =================================================== */}

      <div className="page-header-row">

        <div>

          <h1 className="page-title">
            Students
          </h1>

          <p className="page-subtitle">
            Search, filter and monitor academic risk
          </p>

        </div>


        {/* =================================================
            ACTION BUTTONS
        ================================================= */}

        <div
          style={{
            display: 'flex',
            gap: '10px',
            alignItems: 'center'
          }}
        >

          {/* -----------------------------------------------
              EXISTING ADD STUDENT BUTTON
          ------------------------------------------------ */}

          <button
            className="btn-header-action"
            onClick={onOpenAddStudentModal}
          >

            <Icons.Plus />

            <span>
              Add Student
            </span>

          </button>


          {/* -----------------------------------------------
              UPLOAD DATASET BUTTON
          ------------------------------------------------ */}

          <label
            className="btn-header-action"
            style={{
              cursor: uploading
                ? 'not-allowed'
                : 'pointer',

              opacity: uploading
                ? 0.6
                : 1
            }}
          >

            <span>
              {uploading
                ? 'Uploading...'
                : 'Upload Dataset'}
            </span>


            <input
              type="file"
              accept=".csv,.xlsx"
              onChange={handleDatasetUpload}
              disabled={uploading}
              style={{
                display: 'none'
              }}
            />

          </label>

        </div>

      </div>


      {/* ===================================================
          SUCCESS MESSAGE
      =================================================== */}

      {uploadMessage && (

        <div
          className="alert-box alert-success"
          style={{
            marginBottom: '16px'
          }}
        >

          {uploadMessage}

        </div>

      )}


      {/* ===================================================
          ERROR MESSAGE
      =================================================== */}

      {uploadError && (

        <div
          className="alert-box alert-error"
          style={{
            marginBottom: '16px'
          }}
        >

          {uploadError}

        </div>

      )}


      {/* ===================================================
          SEARCH + FILTER
      =================================================== */}

      <div className="filter-search-bar">

        <div className="search-input-wrapper">

          <span className="search-icon">

            <Icons.Search />

          </span>


          <input
            type="text"
            className="search-input"
            placeholder="Search by name or ID..."
            value={searchTerm}
            onChange={(e) =>
              setSearchTerm(e.target.value)
            }
          />

        </div>


        <div className="filter-pills">

          {[
            'All',
            'Low',
            'Medium',
            'High'
          ].map((pill) => (

            <button
              key={pill}
              className={`filter-pill ${
                filterRisk === pill
                  ? 'active'
                  : ''
              }`}
              onClick={() =>
                setFilterRisk(pill)
              }
            >

              {pill}

            </button>

          ))}

        </div>

      </div>


      {/* ===================================================
          STUDENT TABLE
      =================================================== */}

      <div className="table-card">

        <table className="custom-table">

          <thead>

            <tr>

              <th>
                Student
              </th>

              <th>
                ID
              </th>

              <th>
                Department
              </th>

              <th>
                Attendance
              </th>

              <th>
                CGPA
              </th>

              <th>
                Risk
              </th>

            </tr>

          </thead>


          <tbody>

            {students.length === 0 ? (

              <tr>

                <td
                  colSpan="6"
                  style={{
                    textAlign: 'center',
                    padding: '32px',
                    color: '#6B7280'
                  }}
                >

                  {loading
                    ? 'Loading student records...'
                    : 'No matching students found.'
                  }

                </td>

              </tr>

            ) : (

              students.map((student) => (

                <tr key={student.id}>

                  <td
                    style={{
                      fontWeight: 600
                    }}
                  >

                    {student.student_name}

                  </td>


                  <td
                    style={{
                      color: '#4B5563'
                    }}
                  >

                    {student.register_number}

                  </td>


                  <td>

                    {student.department}

                  </td>


                  <td>

                    {student.attendance_percentage}%

                  </td>


                  <td>

                    {student.previous_semester_cgpa}

                  </td>


                  <td>

                    <RiskBadge
                      level={student.risk_level}
                    />

                  </td>

                </tr>

              ))

            )}

          </tbody>

        </table>

      </div>

    </div>

  );
}

// ================= ADD STUDENT MODAL =================
function AddStudentModal({ onClose, onStudentAdded }) {
  const [formData, setFormData] = useState({
    student_name: '',
    register_number: '',
    email: '',
    department: '',
    attendance_percentage: '',
    previous_semester_cgpa: '',
    assignment_score: '',
    cia_marks: '',
    laboratory_performance: '',
    subject_wise_marks: ''
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await API.addStudent(formData);
      onStudentAdded(res);
    } catch (err) {
      setError(err.message || 'Error saving student');
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-container">
        <div className="modal-header">
          <h2 className="modal-title">Add Student</h2>
          <button className="modal-close-btn" onClick={onClose}>
            <Icons.Close />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && <div className="alert-box alert-error">{error}</div>}

            <div className="form-section-title">Personal Information</div>
            <div className="form-group">
              <label className="form-label">Student Name</label>
              <input
                type="text"
                name="student_name"
                className="form-input"
                placeholder="e.g. Priyadharshini"
                value={formData.student_name}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-grid-2">
              <div className="form-group">
                <label className="form-label">Register Number</label>
                <input
                  type="text"
                  name="register_number"
                  className="form-input"
                  placeholder="e.g. 202524ubca099"
                  value={formData.register_number}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Email ID</label>
                <input
                  type="email"
                  name="email"
                  className="form-input"
                  placeholder="student@university.edu"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="form-section-title">Academic Information</div>

            <div className="form-grid-2">
              <div className="form-group">
                <label className="form-label">Department</label>
                <select
                  name="department"
                  className="form-select"
                  value={formData.department}
                  onChange={handleChange}
                >
                  <option value="Computer Science">Computer Science</option>
                  <option value="Information Technology">Information Technology</option>
                  <option value="Tamil">Tamil</option>
                  <option value="Artificial Intelligence">Artificial Intelligence</option>
                  <option value="BCA">BCA</option>
                  <option value="English">English</option>
                  <option value="Chemistry">Chemistry</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Attendance Percentage (0-100)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="100"
                  name="attendance_percentage"
                  className="form-input"
                  placeholder="e.g. 62.5"
                  value={formData.attendance_percentage}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="form-grid-2">
              <div className="form-group">
                <label className="form-label">Previous Semester CGPA (0-10)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="10"
                  name="previous_semester_cgpa"
                  className="form-input"
                  placeholder="e.g. 5.4"
                  value={formData.previous_semester_cgpa}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Assignment Score (0-100)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="100"
                  name="assignment_score"
                  className="form-input"
                  placeholder="e.g. 58"
                  value={formData.assignment_score}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="form-grid-2">
              <div className="form-group">
                <label className="form-label">CIA Marks (0-100)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="100"
                  name="cia_marks"
                  className="form-input"
                  placeholder="e.g. 48"
                  value={formData.cia_marks}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Laboratory Performance (0-100)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="100"
                  name="laboratory_performance"
                  className="form-input"
                  placeholder="e.g. 55"
                  value={formData.laboratory_performance}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Subject-wise Marks (0-100)</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="100"
                name="subject_wise_marks"
                className="form-input"
                placeholder="e.g. 50"
                value={formData.subject_wise_marks}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-secondary" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button
              type="submit"
              className="btn-header-action"
              style={{ padding: '0 20px', height: '40px' }}
              disabled={loading}
            >
              {loading ? 'Processing ML Prediction...' : 'Save & Predict'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ================= PREDICTION RESULT MODAL =================
function PredictionResultModal({ resultData, onClose }) {
  if (!resultData) return null;
  const { student, prediction, email_status } = resultData;

  return (
    <div className="modal-overlay">
      <div className="modal-container" style={{ maxWidth: '580px' }}>
        <div className="modal-header">
          <h2 className="modal-title">Academic Risk Result</h2>
          <button className="modal-close-btn" onClick={onClose}>
            <Icons.Close />
          </button>
        </div>

        <div className="modal-body">
          <div className="result-badge-row">
            <div>
              <div style={{ fontSize: '13px', color: '#6B7280' }}>Student Name</div>
              <div style={{ fontSize: '18px', fontWeight: 700, color: '#09284A' }}>
                {student.student_name}
              </div>
              <div style={{ fontSize: '12px', color: '#9CA3AF' }}>ID: {student.register_number}</div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '4px' }}>Risk Assessment</div>
              <RiskBadge level={prediction.risk_level} />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', margin: '16px 0' }}>
            <div style={{ background: '#F8FAF9', padding: '12px 16px', borderRadius: '8px', border: '1px solid #E5E7EB' }}>
              <div style={{ fontSize: '12px', color: '#6B7280' }}>Overall Performance</div>
              <div style={{ fontSize: '24px', fontWeight: 700, color: '#16382C' }}>
                {prediction.overall_performance}%
              </div>
            </div>

            <div style={{ background: '#F8FAF9', padding: '12px 16px', borderRadius: '8px', border: '1px solid #E5E7EB' }}>
              <div style={{ fontSize: '12px', color: '#6B7280' }}>Risk Probability</div>
              <div style={{ fontSize: '24px', fontWeight: 700, color: '#C0392B' }}>
                {prediction.risk_probability}%
              </div>
            </div>
          </div>

          <div style={{ marginTop: '16px' }}>
            <h4 style={{ fontSize: '13px', fontWeight: 700, color: '#09284A', textTransform: 'uppercase' }}>
              Contributing Risk Factors
            </h4>
            <ul className="result-list">
              {prediction.risk_factors.map((f, i) => (
                <li key={i}>{f}</li>
              ))}
            </ul>
          </div>

          <div style={{ marginTop: '16px' }}>
            <h4 style={{ fontSize: '13px', fontWeight: 700, color: '#16382C', textTransform: 'uppercase' }}>
              Recommended Interventions
            </h4>
            <ul className="result-list">
              {prediction.recommendations.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>

          <div style={{ marginTop: '20px', padding: '12px 16px', background: '#F9FAFB', borderRadius: '8px', border: '1px solid #E5E7EB', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '13px', color: '#4B5563' }}>Automated Student Alert:</span>
            <span
              className={`email-status-badge ${
                email_status === 'SENT'
                  ? 'email-status-sent'
                  : email_status === 'FAILED'
                  ? 'email-status-failed'
                  : 'email-status-not-configured'
              }`}
            >
              {email_status === 'NOT_CONFIGURED' ? 'EMAIL NOT CONFIGURED' : email_status}
            </span>
          </div>
        </div>

        <div className="modal-footer">
          <button type="button" className="btn-header-action" onClick={onClose}>
            Done & View Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}

// ================= ALERT HISTORY PAGE =================
function AlertHistoryPageView({ currentUser }) {
  const [alerts, setAlerts] = useState([]);
  const [expandedId, setExpandedId] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const isStudent = currentUser?.role === 'Student';
      const data = isStudent
        ? await API.getStudentAlerts(currentUser?.email)
        : await API.getAlerts();
      setAlerts(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, [currentUser]);

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div>
      <div className="page-header-row">
        <div>
          <h1 className="page-title">Alert History</h1>
          <p className="page-subtitle">Automated email alerts recorded by the system</p>
        </div>
      </div>

      {alerts.length === 0 ? (
        <div className="table-card" style={{ padding: '48px 32px', textAlign: 'center', color: '#6B7280' }}>
          {loading
            ? 'Loading alert logs...'
            : currentUser?.role === 'Student'
            ? 'No academic risk alerts have been issued for your profile.'
            : 'No alert logs recorded yet.'}
        </div>
      ) : (
        alerts.map((alert) => {
          const isExpanded = expandedId === alert.id;
          return (
            <div key={alert.id} className="alert-card-item">
              <div className="alert-card-top">
                <div className="alert-icon-title">
                  <div className="alert-mail-icon">
                    <Icons.Mail />
                  </div>
                  <div>
                    <h3 className="alert-subject">
                      Academic Risk Alert – Immediate Attention Required
                    </h3>
                    <div className="alert-meta">
                      <span>{alert.student_email}</span>
                      <span className="alert-meta-dot">&bull;</span>
                      <span>ID: {alert.student_reg_no}</span>
                      <span className="alert-meta-dot">&bull;</span>
                      <span>{alert.created_at}</span>
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <RiskBadge level={alert.risk_level} />
                  <span
                    className={`email-status-badge ${
                      alert.email_status === 'SENT'
                        ? 'email-status-sent'
                        : alert.email_status === 'FAILED'
                        ? 'email-status-failed'
                        : 'email-status-not-configured'
                    }`}
                  >
                    {alert.email_status === 'NOT_CONFIGURED' ? 'EMAIL NOT CONFIGURED' : alert.email_status}
                  </span>
                </div>
              </div>

              <button
                type="button"
                className="email-toggle-btn"
                onClick={() => toggleExpand(alert.id)}
              >
                <span>{isExpanded ? 'Hide email content' : 'View email content'}</span>
                {isExpanded ? <Icons.ChevronUp /> : <Icons.ChevronDown />}
              </button>

              {isExpanded && (
                <div className="email-expanded-panel">
                  <div style={{ marginBottom: '8px' }}>
                    <strong>To:</strong> {alert.student_email} ({alert.student_name})
                  </div>
                  <div style={{ marginBottom: '8px' }}>
                    <strong>Subject:</strong> Academic Risk Alert – Immediate Attention Required
                  </div>
                  <div style={{ marginBottom: '8px' }}>
                    <strong>Risk Level:</strong> {alert.risk_level}
                  </div>
                  <div style={{ marginBottom: '12px' }}>
                    <strong>Message:</strong>
                    <p style={{ marginTop: '4px', color: '#4B5563' }}>{alert.alert_message}</p>
                  </div>
                  <div>
                    <strong>Recommendations:</strong>
                    <p style={{ marginTop: '4px', color: '#285743' }}>{alert.recommendation}</p>
                  </div>
                </div>
              )}
            </div>
          );
        })
      )}
    </div>
  );
}

 // ================= MODEL INSIGHTS PAGE =================

function StatCard({ label, value, type }) {
  return (
    <div className={`stat-card ${type || ''}`}>
      <div className="stat-card-label">{label}</div>
      <div className="stat-card-value">{value}</div>
    </div>
  );
}

function ModelInsightsPageView() {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;

    const loadInsights = async () => {
      try {
        setLoading(true);
        setError('');

        const data = await API.getModelInsights();

        if (!active) return;

        if (
          !data ||
          !data.summary ||
          !Array.isArray(data.features) ||
          !Array.isArray(data.key_risk_drivers)
        ) {
          throw new Error(
            'Invalid API response. Check the Model Insights backend.'
          );
        }

        setInsights(data);
      } catch (err) {
        console.error('Model Insights error:', err);

        if (active) {
          setError(
            err.message || 'Failed to load Model Insights.'
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    loadInsights();

    return () => {
      active = false;
    };
  }, []);

  if (loading) {
    return (
      <div className="page-content">
        <h2>Model Insights</h2>
        <p>Loading model insights...</p>
      </div>
    );
  }

  if (error || !insights) {
    return (
      <div className="page-content">
        <h2>Model Insights</h2>
        <p>{error || 'Unable to load model insights.'}</p>
        <button onClick={() => window.location.reload()}>
          Retry
        </button>
      </div>
    );
  }

  const totalStudents = Number(insights.total_students) || 0;
  const avgAttendance =
    Number(insights.summary.avg_attendance) || 0;
  const avgCgpa =
    Number(insights.summary.avg_cgpa) || 0;

  return (
    <div className="page-content">
      <div className="page-header-row">
        <div>
          <h2>Model Insights</h2>
          <p>
            Academic performance and institutional risk factors
          </p>
        </div>
      </div>

      <div className="stat-cards-grid">
        <StatCard
          label="CLASSIFIER ARCHITECTURE"
          value="Random Forest"
          type="dark"
        />

        <StatCard
          label="TOTAL STUDENTS"
          value={totalStudents}
          type="green"
        />

        <StatCard
          label="AVERAGE ATTENDANCE"
          value={`${avgAttendance.toFixed(2)}%`}
          type="dark"
        />

        <StatCard
          label="AVERAGE CGPA"
          value={avgCgpa.toFixed(2)}
          type="dark"
        />
      </div>

      {totalStudents === 0 && (
        <p>
          No student records found. Import student data to view insights.
        </p>
      )}

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Top Risk Factors (Feature Importance)</h3>

          {insights.features.length === 0 ? (
            <p>Feature importance data is not available.</p>
          ) : (
            insights.features.map((item, idx) => {
              const importance = Math.min(
                100,
                Math.max(0, Number(item.importance) || 0)
              );

              return (
                <div
                  key={item.feature || idx}
                  className="feature-row"
                >
                  <div className="feature-label">
                    <span>
                      {item.feature || 'Unknown feature'}
                    </span>
                    <span>{importance.toFixed(1)}%</span>
                  </div>

                  <div className="feature-bar-bg">
                    <div
                      className="feature-bar"
                      style={{ width: `${importance}%` }}
                    />
                  </div>
                </div>
              );
            })
          )}
        </div>

        <div className="chart-card">
          <h3>Institutional Risk Drivers</h3>

          {insights.key_risk_drivers.length === 0 ? (
            <p>No risk driver information available.</p>
          ) : (
            insights.key_risk_drivers.map((driver, idx) => (
              <div
                key={driver.driver || idx}
                className="risk-driver-item"
              >
                <h4>{driver.driver || 'Risk factor'}</h4>
                <p>
                  {driver.impact || 'No details available.'}
                </p>

                {driver.recommendation && (
                  <p>
                    <strong>Recommendation:</strong>{' '}
                    {driver.recommendation}
                  </p>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

// ================= GOOGLE CLASSROOM =================

function GoogleClassroomPageView() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/google-classroom/status')
      .then(async (res) => {
        const data = await res.json();

        if (!res.ok) {
          throw new Error(
            data.error || 'Unable to check Google Classroom status.'
          );
        }

        return data;
      })
      .then((data) => {
        setStatus(data);
      })
      .catch((err) => {
        console.error('Google Classroom status error:', err);

        setStatus({
          configured: false,
          authenticated: false,
          message: err.message
        });
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const handleConnectClassroom = () => {
    // Start Google OAuth authentication
    window.location.href = '/api/google-classroom/auth';
  };

  if (loading) {
    return (
      <div>
        <div className="page-header-row">
          <div>
            <h1 className="page-title">Google Classroom</h1>
            <p className="page-subtitle">
              Access your assignments and intervention tasks
            </p>
          </div>
        </div>

        <div
          className="table-card"
          style={{
            padding: '40px',
            textAlign: 'center',
            marginTop: '24px'
          }}
        >
          Checking Google Classroom configuration...
        </div>
      </div>
    );
  }

  const isConfigured = status?.configured === true;
  const isAuthenticated = status?.authenticated === true;

  return (
    <div>
      {/* PAGE HEADER */}
      <div className="page-header-row">
        <div>
          <h1 className="page-title">Google Classroom</h1>

          <p className="page-subtitle">
            Access your assignments and intervention tasks
          </p>
        </div>
      </div>

      {/* GOOGLE CLASSROOM CARD */}
      <div
        className="table-card"
        style={{
          marginTop: '24px',
          padding: '28px'
        }}
      >

        {/* HEADER */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
            marginBottom: '24px'
          }}
        >
          <div
            style={{
              width: '52px',
              height: '52px',
              borderRadius: '12px',
              background: '#EAF3ED',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#16382C'
            }}
          >
            <Icons.Classroom />
          </div>

          <div>
            <h2
              style={{
                margin: 0,
                fontSize: '20px',
                fontWeight: 800,
                color: '#09284A'
              }}
            >
              Google Classroom Integration
            </h2>

            <p
              style={{
                margin: '6px 0 0',
                fontSize: '14px',
                color: '#6B7280'
              }}
            >
              Automatically provide intervention assignments
              for High Risk students.
            </p>
          </div>
        </div>


        {/* CONFIGURATION STATUS */}
        <div
          style={{
            border: '1px solid #E5E7EB',
            borderRadius: '10px',
            padding: '18px',
            marginBottom: '24px'
          }}
        >
          <div
            style={{
              fontSize: '13px',
              fontWeight: 700,
              color: '#374151',
              marginBottom: '8px'
            }}
          >
            Configuration Status:
          </div>

          <div
            style={{
              fontSize: '14px',
              color:
                isConfigured
                  ? '#285743'
                  : '#C0392B'
            }}
          >
            {status?.message ||
              'Google Classroom API is not configured.'}
          </div>
        </div>


        {/* BUTTONS */}
        <div
          style={{
            display: 'flex',
            gap: '14px',
            flexWrap: 'wrap'
          }}
        >

          {/* OPEN GOOGLE CLASSROOM */}
          <a
            href={
              status?.classroom_url ||
              'https://classroom.google.com'
            }
            target="_blank"
            rel="noopener noreferrer"
            className="btn-header-action"
            style={{
              textDecoration: 'none'
            }}
          >
            Open Google Classroom
          </a>


          {/* CONNECT CLASSROOM */}
          <button
            type="button"
            className="btn-secondary"
            onClick={handleConnectClassroom}
          >
            {isAuthenticated
              ? 'Reconnect Classroom'
              : 'Connect Classroom'}
          </button>

        </div>


        {/* INFORMATION */}
        {!isConfigured && (
          <div
            style={{
              marginTop: '20px',
              padding: '14px 16px',
              borderRadius: '8px',
              background: '#FFF7ED',
              border: '1px solid #FED7AA',
              color: '#9A3412',
              fontSize: '13px',
              lineHeight: 1.6
            }}
          >
            Google Classroom credentials are not configured.
            Please configure GOOGLE_CLIENT_ID and
            GOOGLE_CLIENT_SECRET in the backend environment.
          </div>
        )}

        {isConfigured && !isAuthenticated && (
          <div
            style={{
              marginTop: '20px',
              padding: '14px 16px',
              borderRadius: '8px',
              background: '#EFF6FF',
              border: '1px solid #BFDBFE',
              color: '#1D4ED8',
              fontSize: '13px',
              lineHeight: 1.6
            }}
          >
            Google Classroom is configured.
            Click <strong>Connect Classroom</strong> to authorize
            your Google account.
          </div>
        )}

        {isAuthenticated && (
          <div
            style={{
              marginTop: '20px',
              padding: '14px 16px',
              borderRadius: '8px',
              background: '#F0FDF4',
              border: '1px solid #BBF7D0',
              color: '#166534',
              fontSize: '13px',
              lineHeight: 1.6
            }}
          >
            Google Classroom is authenticated successfully.
          </div>
        )}

      </div>
    </div>
  );
}
// ================= STUDENT DASHBOARD =================
function StudentDashboardView({ currentUser }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    API.getStudentStats(currentUser?.email)
      .then((data) => setStats(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [currentUser]);

  if (loading || !stats) {
    return (
      <div>
        <h1 className="page-title">Welcome, {currentUser?.full_name || currentUser?.username}</h1>
        <p className="page-subtitle">Track your academic performance and risk status</p>
        <div className="table-card" style={{ padding: '36px', textAlign: 'center', color: '#6B7280', marginTop: '24px' }}>
          Loading your academic evaluation profile...
        </div>
      </div>
    );
  }

  const s = stats.student;

  // Strict data isolation: when no faculty evaluation has been submitted for THIS student
  if (!s || stats.has_data === false) {
    return (
      <div>
        <div className="page-header-row">
          <div>
            <h1 className="page-title">Welcome, {currentUser?.full_name || currentUser?.username}</h1>
            <p className="page-subtitle">Track your academic performance and risk status</p>
          </div>
        </div>

        <div className="table-card" style={{ padding: '56px 32px', textAlign: 'center', maxWidth: '720px', margin: '24px auto' }}>
          <div style={{ width: '60px', height: '60px', borderRadius: '50%', background: '#EAF3ED', color: '#16382C', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px' }}>
            <Icons.Shield />
          </div>
          <h2 style={{ fontSize: '20px', fontWeight: 800, color: '#09284A', marginBottom: '10px' }}>
            No Academic Evaluation Records Found
          </h2>
          <p style={{ fontSize: '14px', color: '#6B7280', maxWidth: '500px', margin: '0 auto 24px', lineHeight: 1.6 }}>
            Your account ({currentUser?.email || currentUser?.username}) does not have academic metrics registered yet. Once your faculty mentor submits your semester evaluations, your academic performance score, risk classification, and personalized interventions will be displayed here.
          </p>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '8px 18px', background: '#F9FAFB', borderRadius: '6px', border: '1px solid #E5E7EB', fontSize: '13px', color: '#4B5563', fontWeight: 500 }}>
            <span>Status: Awaiting Faculty Evaluation</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header-row">
        <div>
          <h1 className="page-title">Welcome, {currentUser?.full_name || currentUser?.username}</h1>
          <p className="page-subtitle">Track your academic performance and risk status</p>
        </div>
      </div>

      <div className="stat-cards-grid">
        <StatCard label="OVERALL PERFORMANCE" value={`${stats.overall_performance}%`} type="dark" />
        <StatCard label="ATTENDANCE" value={`${stats.attendance}%`} type="green" />
        <div className="stat-card">
          <div className="stat-card-label">CURRENT RISK</div>
          <div style={{ marginTop: '6px' }}>
            <RiskBadge level={stats.current_risk} />
          </div>
        </div>
        <StatCard label="PENDING ALERTS" value={stats.pending_alerts} type="orange" />
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3 className="chart-card-title">Academic Metrics Breakdown</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {stats.performance_breakdown.map((item, idx) => (
              <div key={idx}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '4px' }}>
                  <span>{item.subject}</span>
                  <span style={{ fontWeight: 600 }}>{item.score}%</span>
                </div>
                <div style={{ width: '100%', height: '8px', background: '#F3F4F6', borderRadius: '4px' }}>
                  <div
                    style={{
                      width: `${item.score}%`,
                      height: '100%',
                      background: item.score >= 75 ? '#285743' : item.score >= 50 ? '#C48A47' : '#C0392B',
                      borderRadius: '4px'
                    }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="chart-card">
          <h3 className="chart-card-title">Academic Profile & Advisement</h3>
          <div style={{ fontSize: '14px', lineHeight: 1.8, color: '#374151' }}>
            <p><strong>Department:</strong> {s.department}</p>
            <p><strong>Register Number:</strong> {s.register_number}</p>
            <p><strong>Previous Semester CGPA:</strong> {s.previous_semester_cgpa} / 10</p>
            <p><strong>Continuous Assessment (CIA):</strong> {s.cia_marks}%</p>
            <p><strong>Laboratory Practical Score:</strong> {s.laboratory_performance}%</p>
            <div style={{ marginTop: '16px', padding: '14px', background: '#EAF3ED', borderRadius: '8px', color: '#16382C' }}>
              <strong>Advisory:</strong> Attend regular classes to keep attendance above 75% and schedule consultation with your mentor for targeted assistance.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ================= ADMIN DASHBOARD =================
function AdminDashboardView() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    API.getAdminStats()
      .then((data) => setStats(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading || !stats) {
    return (
      <div>
        <h1 className="page-title">Admin Dashboard</h1>
        <p className="page-subtitle">Overall academic risk monitoring and institutional insights</p>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header-row">
        <div>
          <h1 className="page-title">Admin Dashboard</h1>
          <p className="page-subtitle">Overall academic risk monitoring and institutional insights</p>
        </div>
      </div>

      <div className="stat-cards-grid">
        <StatCard label="TOTAL STUDENTS" value={stats.total_students} type="dark" />
        <StatCard label="TOTAL FACULTY" value={stats.total_faculty} type="dark" />
        <StatCard label="LOW RISK" value={stats.low_risk} type="green" />
        <StatCard label="HIGH RISK" value={stats.high_risk} type="red" />
      </div>

      <div className="stat-cards-grid" style={{ marginBottom: '32px' }}>
        <StatCard label="MEDIUM RISK" value={stats.medium_risk} type="orange" />
        <StatCard label="AVERAGE ATTENDANCE" value={`${stats.avg_attendance}%`} type="green" />
        <StatCard label="AVERAGE PERFORMANCE" value={`${stats.avg_performance}%`} type="dark" />
        <StatCard label="AVERAGE CGPA" value={stats.avg_cgpa} type="dark" />
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3 className="chart-card-title">Risk Distribution</h3>
          <div className="chart-wrapper">
            <DoughnutRiskChart data={stats.risk_distribution} />
          </div>
        </div>

        <div className="chart-card">
          <h3 className="chart-card-title">Department-wise Academic Summary</h3>
          <div className="table-card" style={{ boxShadow: 'none', border: 'none' }}>
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Department</th>
                  <th>Students</th>
                  <th>Avg Score</th>
                  <th>Avg Attendance</th>
                </tr>
              </thead>
              <tbody>
                {stats.department_statistics.map((dept, i) => (
                  <tr key={i}>
                    <td style={{ fontWeight: 600 }}>{dept.department}</td>
                    <td>{dept.students_count}</td>
                    <td>{dept.avg_performance}%</td>
                    <td>{dept.avg_attendance}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

// ================= ADMIN FACULTY PAGE =================
function AdminFacultyPageView() {
  const [faculty, setFaculty] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState({ name: '', email: '', department: 'Computer Science' });

  const loadFaculty = async () => {
    setLoading(true);
    try {
      const data = await API.getFacultyMembers();
      setFaculty(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFaculty();
  }, []);

  const handleAddSubmit = async (e) => {
    e.preventDefault();
    try {
      await API.addFaculty(formData);
      setShowAddModal(false);
      setFormData({ name: '', email: '', department: 'Computer Science' });
      loadFaculty();
    } catch (err) {
      alert(err.message || 'Error adding faculty');
    }
  };

  return (
    <div>
      <div className="page-header-row">
        <div>
          <h1 className="page-title">Faculty Directory</h1>
          <p className="page-subtitle">Manage faculty mentors and departmental assignment</p>
        </div>
        <button className="btn-header-action" onClick={() => setShowAddModal(true)}>
          <Icons.Plus />
          <span>Add Faculty</span>
        </button>
      </div>

      <div className="table-card">
        <table className="custom-table">
          <thead>
            <tr>
              <th>Faculty Name</th>
              <th>Email</th>
              <th>Department</th>
              <th>Number of Students</th>
              <th>Status</th>
              <th>Created Date</th>
            </tr>
          </thead>
          <tbody>
            {faculty.map((f) => (
              <tr key={f.id}>
                <td style={{ fontWeight: 600 }}>{f.name}</td>
                <td>{f.email}</td>
                <td>{f.department}</td>
                <td>{f.student_count}</td>
                <td>
                  <span style={{ color: '#285743', fontWeight: 600, fontSize: '13px' }}>● {f.status}</span>
                </td>
                <td>{f.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showAddModal && (
        <div className="modal-overlay">
          <div className="modal-container" style={{ maxWidth: '480px' }}>
            <div className="modal-header">
              <h2 className="modal-title">Add Faculty Member</h2>
              <button className="modal-close-btn" onClick={() => setShowAddModal(false)}>
                <Icons.Close />
              </button>
            </div>
            <form onSubmit={handleAddSubmit}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Full Name</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="Prof. Name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Email</label>
                  <input
                    type="email"
                    className="form-input"
                    placeholder="faculty@university.edu"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Department</label>
                  <select
                    className="form-select"
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                  >
                    <option value="Computer Science">Computer Science</option>
                    <option value="Information Technology">Information Technology</option>
                    <option value="English">English</option>
                    <option value="Tamil">Tamil</option>
                    <option value="BCA">BCA</option>
                    <option value="Chemistry">Chemistry</option>
                    <option value="Artificial Intelligence">Artificial Intelligence</option>
                  </select>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setShowAddModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-header-action">
                  Save Faculty
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

// ================= MAIN APP CONTROLLER =================

function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [authView, setAuthView] = useState('login');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);

  // Modal states
  const [isAddStudentOpen, setIsAddStudentOpen] = useState(false);
  const [predictionResult, setPredictionResult] = useState(null);

  // Check existing session
  useEffect(() => {
    API.getCurrentUser().then((user) => {
      if (user) {
        setCurrentUser(user);
        setActiveTab('dashboard');
      }
    }).catch((error) => {
      console.error('Failed to check current session:', error);
    });
  }, []);

  // Load faculty statistics
  const refreshStats = () => {
    API.getStatistics()
      .then((data) => setStats(data))
      .catch((error) => console.error('Failed to load statistics:', error));
  };

  useEffect(() => {
    if (currentUser) {
      refreshStats();
    }
  }, [currentUser, activeTab]);

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    setActiveTab('dashboard');
  };

  const handleLogout = async () => {
    try {
      await API.logout();
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setCurrentUser(null);
      setActiveTab('dashboard');
      setAuthView('login');
    }
  };

  const handleStudentAdded = (result) => {
    setIsAddStudentOpen(false);
    setPredictionResult(result);
    refreshStats();
  };

  // Unauthenticated screen
  if (!currentUser) {
    if (authView === 'register') {
      return (
        <RegisterPage
          onNavigateLogin={() => setAuthView('login')}
        />
      );
    }

    return (
      <LoginPage
        onLoginSuccess={handleLoginSuccess}
        onNavigateRegister={() => setAuthView('register')}
      />
    );
  }

  // Render content based on role and selected tab
  const renderContent = () => {
    const role = currentUser.role;

    // Google Classroom page
    if (activeTab === 'classroom') {
      return <GoogleClassroomPageView />;
    }

    // Faculty pages
    if (role === 'Faculty') {
      switch (activeTab) {
        case 'dashboard':
          return (
            <FacultyDashboardView
              stats={stats}
              onNavigateStudents={() => setActiveTab('students')}
            />
          );

        case 'students':
          return (
            <StudentsPageView
              onOpenAddStudentModal={() => setIsAddStudentOpen(true)}
            />
          );

        case 'alerts':
          return <AlertHistoryPageView currentUser={currentUser} />;

        case 'insights':
          return <ModelInsightsPageView />;

        case 'statistics':
          return <StatisticsPageView />;

        default:
          return <FacultyDashboardView stats={stats} />;
      }
    }

    // Student pages
    if (role === 'Student') {
      switch (activeTab) {
        case 'dashboard':
          return <StudentDashboardView currentUser={currentUser} />;

        case 'performance':
          return <StudentDashboardView currentUser={currentUser} />;

        case 'statistics':
          return <StudentDashboardView currentUser={currentUser} />;

        case 'alerts':
          return <AlertHistoryPageView currentUser={currentUser} />;

        default:
          return <StudentDashboardView currentUser={currentUser} />;
      }
    }

    // Admin pages
    switch (activeTab) {
      case 'dashboard':
        return <AdminDashboardView />;

      case 'students':
        return (
          <StudentsPageView
            onOpenAddStudentModal={() => setIsAddStudentOpen(true)}
          />
        );

      case 'faculty':
        return <AdminFacultyPageView />;

      case 'risk_monitoring':
        return <ModelInsightsPageView />;

      case 'statistics':
        return <StatisticsPageView />;

      case 'alerts':
        return <AlertHistoryPageView currentUser={currentUser} />;

      default:
        return <AdminDashboardView />;
    }
  };

  return (
    <div className="app-container">
      <Sidebar
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        currentUser={currentUser}
        onLogout={handleLogout}
      />

      <main className="main-wrapper">
        {renderContent()}
      </main>

      {/* Add Student Modal */}
      {isAddStudentOpen && (
        <AddStudentModal
          onClose={() => setIsAddStudentOpen(false)}
          onStudentAdded={handleStudentAdded}
        />
      )}

      {/* Prediction Result Modal */}
      {predictionResult && (
        <PredictionResultModal
          resultData={predictionResult}
          onClose={() => setPredictionResult(null)}
        />
      )}
    </div>
  );
}

// Render React App
const rootElement = document.getElementById('root');
const root = ReactDOM.createRoot(rootElement);
root.render(<App />);
