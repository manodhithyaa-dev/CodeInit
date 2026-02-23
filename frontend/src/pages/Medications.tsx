import { useState, useEffect } from 'react';
import { 
  createMedication, getMedications, deleteMedication, 
  markMedicationTaken, getMedicationSummary 
} from '../api';

export default function Medications() {
  const [medications, setMedications] = useState<any[]>([]);
  const [summary, setSummary] = useState<{ current_streak: number; weekly_adherence: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: '', dosage: '', frequency_per_day: 1, reminder_time: '' });
  const [submitting, setSubmitting] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [medsRes, summaryRes] = await Promise.all([getMedications(), getMedicationSummary()]);
      setMedications(medsRes.data);
      setSummary(summaryRes.data);
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
      await createMedication({
        name: formData.name,
        dosage: formData.dosage || undefined,
        frequency_per_day: formData.frequency_per_day,
        reminder_time: formData.reminder_time || undefined,
      });
      setShowForm(false);
      setFormData({ name: '', dosage: '', frequency_per_day: 1, reminder_time: '' });
      fetchData();
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this medication?')) return;
    try {
      await deleteMedication(id);
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleMarkTaken = async (id: number) => {
    const today = new Date().toISOString().split('T')[0];
    try {
      await markMedicationTaken(id, { taken_date: today, taken: true });
      fetchData();
      alert('Marked as taken!');
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="page">
      <div className="flex justify-between items-center mb-6">
        <h1 className="title" style={{ marginBottom: 0 }}>Medications</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'Add Medication'}
        </button>
      </div>

      {/* Summary Cards */}
      <div className="stats-grid mb-6">
        <div className="stat-card">
          <div className="stat-value">{summary?.current_streak || 0}</div>
          <div className="stat-label">Current Streak (Days)</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{summary?.weekly_adherence || 0}%</div>
          <div className="stat-label">Weekly Adherence</div>
        </div>
      </div>

      {/* Add Form */}
      {showForm && (
        <div className="card mb-6">
          <h2 className="title">Add Medication</h2>
          <form onSubmit={handleSubmit}>
            <div className="grid grid-2">
              <div className="form-group">
                <label className="label">Name *</label>
                <input
                  type="text"
                  className="input"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label className="label">Dosage</label>
                <input
                  type="text"
                  className="input"
                  value={formData.dosage}
                  onChange={(e) => setFormData({ ...formData, dosage: e.target.value })}
                  placeholder="e.g., 500mg"
                />
              </div>
            </div>
            <div className="grid grid-2">
              <div className="form-group">
                <label className="label">Times per day</label>
                <input
                  type="number"
                  className="input"
                  value={formData.frequency_per_day}
                  onChange={(e) => setFormData({ ...formData, frequency_per_day: parseInt(e.target.value) })}
                  min={1}
                />
              </div>
              <div className="form-group">
                <label className="label">Reminder Time</label>
                <input
                  type="time"
                  className="input"
                  value={formData.reminder_time}
                  onChange={(e) => setFormData({ ...formData, reminder_time: e.target.value })}
                />
              </div>
            </div>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Adding...' : 'Add Medication'}
            </button>
          </form>
        </div>
      )}

      {/* Medications List */}
      {loading ? (
        <div className="loading">Loading...</div>
      ) : medications.length === 0 ? (
        <div className="empty-state">
          <p>No medications added yet.</p>
        </div>
      ) : (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Dosage</th>
                <th>Frequency</th>
                <th>Reminder</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {medications.map((med) => (
                <tr key={med.id}>
                  <td>{med.name}</td>
                  <td>{med.dosage || '-'}</td>
                  <td>{med.frequency_per_day}x/day</td>
                  <td>{med.reminder_time || '-'}</td>
                  <td className="flex gap-2">
                    <button className="btn btn-primary" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }} onClick={() => handleMarkTaken(med.id)}>
                      Mark Taken
                    </button>
                    <button className="btn btn-danger" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }} onClick={() => handleDelete(med.id)}>
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
