// RiskGuard API Client
const BASE_URL = '';

export const API = {
  login: async (username, password) => {
    const res = await fetch(`${BASE_URL}/api/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Invalid Username or Password');
    return data;
  },

  register: async (formData) => {
    const res = await fetch(`${BASE_URL}/api/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Account already exists.');
    return data;
  },

  getCurrentUser: async () => {
    const res = await fetch(`${BASE_URL}/api/me`);
    if (!res.ok) return null;
    const data = await res.json();
    return data.user;
  },

  logout: async () => {
    await fetch(`${BASE_URL}/api/logout`, { method: 'POST' });
  },

  getStudents: async (search = '', risk = '', dept = '') => {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (risk && risk !== 'All') params.append('risk_level', risk);
    if (dept && dept !== 'All') params.append('department', dept);
    const res = await fetch(`${BASE_URL}/api/students?${params.toString()}`);
    return await res.json();
  },

  addStudent: async (studentData) => {
    const res = await fetch(`${BASE_URL}/api/students`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(studentData)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Failed to save student.');
    return data;
  },

  deleteStudent: async (id) => {
    const res = await fetch(`${BASE_URL}/api/students/${id}`, { method: 'DELETE' });
    return await res.json();
  },

  getStatistics: async () => {
    const res = await fetch(`${BASE_URL}/api/statistics`);
    return await res.json();
  },

  getAlerts: async () => {
    const res = await fetch(`${BASE_URL}/api/alerts`);
    return await res.json();
  },

  getStudentAlerts: async (email = '') => {
    const res = await fetch(`${BASE_URL}/api/student/alerts?email=${encodeURIComponent(email)}`);
    return await res.json();
  },

  getStudentStats: async (email = '') => {
    const res = await fetch(`${BASE_URL}/api/student/statistics?email=${encodeURIComponent(email)}`);
    return await res.json();
  },

  getAdminStats: async () => {
    const res = await fetch(`${BASE_URL}/api/admin/statistics`);
    return await res.json();
  },

  getFacultyMembers: async () => {
    const res = await fetch(`${BASE_URL}/api/admin/faculty`);
    return await res.json();
  },

  addFaculty: async (formData) => {
    const res = await fetch(`${BASE_URL}/api/admin/faculty`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Failed to add faculty member');
    return data;
  },

  getModelInsights: async () => {
    const res = await fetch(`${BASE_URL}/api/prediction/insights`);
    return await res.json();
  },

  getClassroomStatus: async () => {
    const res = await fetch(`${BASE_URL}/api/google-classroom/status`);
    return await res.json();
  },

  sendEmailRetry: async (alertId) => {
    const res = await fetch(`${BASE_URL}/api/alerts/${alertId}/send-email`, { method: 'POST' });
    return await res.json();
  }
};
