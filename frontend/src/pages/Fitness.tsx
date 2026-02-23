import { useState, useEffect } from 'react';
import { createFitness, getFitnessLogs, deleteFitness, getWeeklyFitness } from '../api';

export default function Fitness() {
  const [logs, setLogs] = useState<any[]>([]);
  const [weekly, setWeekly] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    log_date: new Date().toISOString().split('T')[0],
    activity_completed: false,
    steps: 0,
    minutes_exercised: 0,
    intensity: 'LOW'
  });
  const [submitting, setSubmitting] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      console.log('Fetching fitness data...');
      const logsRes = await getFitnessLogs({ limit: 20 });
      console.log('Fitness logs:', logsRes.data);
      setLogs(logsRes.data);
      
      const weeklyRes = await getWeeklyFitness();
      console.log('Weekly fitness:', weeklyRes.data);
      setWeekly(weeklyRes.data);
    } catch (err: any) {
      console.error('Error fetching fitness data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      console.log('Creating fitness with data:', formData);
      const result = await createFitness({
        log_date: formData.log_date,
        activity_completed: formData.activity_completed,
        steps: formData.steps,
        minutes_exercised: formData.minutes_exercised,
        intensity: formData.intensity,
      });
      console.log('Fitness created:', result.data);
      setShowForm(false);
      setFormData({
        log_date: new Date().toISOString().split('T')[0],
        activity_completed: false,
        steps: 0,
        minutes_exercised: 0,
        intensity: 'LOW'
      });
      setLogs([]);
      await fetchData();
    } catch (err: any) {
      console.error('Error creating fitness log:', err);
      console.error('Error response:', err.response);
      const msg = err?.response?.data?.detail || err?.response?.data || err?.message || 'Failed to create fitness log';
      alert('Error: ' + JSON.stringify(msg));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this fitness log?')) return;
    try {
      await deleteFitness(id);
      setLogs(logs.filter(l => l.id !== id));
      await fetchData();
    } catch (err: any) {
      console.error('Error deleting fitness log:', err);
      const msg = err?.response?.data?.detail || err?.message || 'Failed to delete fitness log';
      alert(msg);
    }
  };

  return (
    <div className="page">
      <div className="flex justify-between items-center mb-6">
        <h1 className="title" style={{ marginBottom: 0 }}>Fitness</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'Log Activity'}
        </button>
      </div>

      {/* Stats */}
      <div className="stats-grid mb-6">
        <div className="stat-card">
          <div className="stat-value">{weekly?.total_steps?.toLocaleString() || 0}</div>
          <div className="stat-label">Steps This Week</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{weekly?.total_minutes || 0}</div>
          <div className="stat-label">Minutes This Week</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{weekly?.days_active || 0}</div>
          <div className="stat-label">Days Active</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{weekly?.current_streak || 0}</div>
          <div className="stat-label">Current Streak</div>
        </div>
      </div>

      {/* Add Form */}
      {showForm && (
        <div className="card mb-6">
          <h2 className="title">Log Activity</h2>
          <form onSubmit={handleSubmit}>
            <div className="grid grid-2">
              <div className="form-group">
                <label className="label">Date</label>
                <input
                  type="date"
                  className="input"
                  value={formData.log_date}
                  onChange={(e) => setFormData({ ...formData, log_date: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label className="label">Intensity</label>
                <select
                  className="select"
                  value={formData.intensity}
                  onChange={(e) => setFormData({ ...formData, intensity: e.target.value })}
                >
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HIGH">High</option>
                </select>
              </div>
            </div>
            <div className="grid grid-2">
              <div className="form-group">
                <label className="label">Steps</label>
                <input
                  type="number"
                  className="input"
                  value={formData.steps}
                  onChange={(e) => setFormData({ ...formData, steps: parseInt(e.target.value) || 0 })}
                  min={0}
                />
              </div>
              <div className="form-group">
                <label className="label">Minutes Exercised</label>
                <input
                  type="number"
                  className="input"
                  value={formData.minutes_exercised}
                  onChange={(e) => setFormData({ ...formData, minutes_exercised: parseInt(e.target.value) || 0 })}
                  min={0}
                />
              </div>
            </div>
            <div className="form-group">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.activity_completed}
                  onChange={(e) => setFormData({ ...formData, activity_completed: e.target.checked })}
                />
                Activity Completed
              </label>
            </div>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Saving...' : 'Save Activity'}
            </button>
          </form>
        </div>
      )}

      {/* Logs List */}
      {loading ? (
        <div className="loading">Loading...</div>
      ) : logs.length === 0 ? (
        <div className="empty-state">
          <p>No fitness logs yet. Start tracking!</p>
        </div>
      ) : (
        <div className="card">
          <h2 className="title">Recent Activity</h2>
          <table className="table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Steps</th>
                <th>Minutes</th>
                <th>Intensity</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
              <tbody>
              {logs.slice(0, 5).map((log) => (
                <tr key={log.id}>
                  <td>{new Date(log.log_date).toLocaleDateString()}</td>
                  <td>{log.steps.toLocaleString()}</td>
                  <td>{log.minutes_exercised}</td>
                  <td>
                    <span className={`badge ${log.intensity === 'HIGH' ? 'badge-danger' : log.intensity === 'MEDIUM' ? 'badge-warning' : 'badge-success'}`}>
                      {log.intensity}
                    </span>
                  </td>
                  <td>{log.activity_completed ? '✅ Completed' : '❌ Not completed'}</td>
                  <td>
                    <button className="btn btn-danger" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }} onClick={() => handleDelete(log.id)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
