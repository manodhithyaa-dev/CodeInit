import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { updateProfile, deleteAccount } from '../api';
import { useAuth } from '../context/AuthContext';

export default function Profile() {
  const { user, setUser, logout } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: user?.name || '',
    age_range: user?.age_range || '',
    primary_goal: user?.primary_goal || 'MOOD',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    try {
      const data: any = {
        name: formData.name,
        age_range: formData.age_range,
        primary_goal: formData.primary_goal,
      };
      if (formData.password) {
        data.password = formData.password;
      }
      const res = await updateProfile(data);
      setUser(res.data);
      setMessage('Profile updated successfully!');
      setFormData({ ...formData, password: '' });
    } catch (err) {
      setMessage('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete your account? This cannot be undone.')) return;
    if (!confirm('Really delete? All your data will be lost forever.')) return;
    try {
      await deleteAccount();
      logout();
      navigate('/login');
    } catch (err) {
      alert('Failed to delete account');
    }
  };

  return (
    <div className="page">
      <h1 className="title">Profile</h1>

      <div className="card" style={{ maxWidth: '600px' }}>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="label">Email</label>
            <input type="email" className="input" value={user?.email} disabled />
          </div>
          <div className="form-group">
            <label className="label">Name</label>
            <input
              type="text"
              className="input"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label className="label">Age Range</label>
            <select
              className="select"
              value={formData.age_range}
              onChange={(e) => setFormData({ ...formData, age_range: e.target.value })}
            >
              <option value="">Select age range</option>
              <option value="13-17">13-17</option>
              <option value="18-24">18-24</option>
              <option value="25-34">25-34</option>
              <option value="35-44">35-44</option>
              <option value="45-54">45-54</option>
              <option value="55-64">55-64</option>
              <option value="65+">65+</option>
            </select>
          </div>
          <div className="form-group">
            <label className="label">Primary Goal</label>
            <select
              className="select"
              value={formData.primary_goal}
              onChange={(e) => setFormData({ ...formData, primary_goal: e.target.value })}
            >
              <option value="MOOD">Mood Tracking</option>
              <option value="MEDICATION">Medication Tracking</option>
              <option value="FITNESS">Fitness Tracking</option>
              <option value="STRESS">Stress Management</option>
            </select>
          </div>
          <div className="form-group">
            <label className="label">New Password (leave blank to keep current)</label>
            <input
              type="password"
              className="input"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="Enter new password"
            />
          </div>
          {message && <p className={message.includes('success') ? 'success' : 'error'}>{message}</p>}
          <div className="flex gap-2">
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
            <button type="button" className="btn btn-danger" onClick={logout}>
              Logout
            </button>
          </div>
        </form>

        <hr style={{ margin: '2rem 0', border: 'none', borderTop: '1px solid #e2e8f0' }} />

        <div>
          <h3 className="text-danger mb-2">Danger Zone</h3>
          <button className="btn btn-danger" onClick={handleDelete}>
            Delete Account
          </button>
          <p className="text-muted text-sm mt-2">
            This will permanently delete your account and all associated data.
          </p>
        </div>
      </div>
    </div>
  );
}
