import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getStats, getWeeklyInsights } from '../api';
import { useAuth } from '../context/AuthContext';
import type { UserStats, WeeklyInsights } from '../types';

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [insights, setInsights] = useState<WeeklyInsights | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getStats(), getWeeklyInsights()])
      .then(([statsRes, insightsRes]) => {
        setStats(statsRes.data);
        setInsights(insightsRes.data);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">Loading...</div>;

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const getMoodEmoji = (score: number) => {
    if (score >= 0.5) return '😊';
    if (score >= 0.1) return '🙂';
    if (score >= -0.1) return '😐';
    if (score >= -0.5) return '😔';
    return '😢';
  };

  return (
    <div className="page">
      <div className="mb-6">
        <h1 className="title">{getGreeting()}, {user?.name}!</h1>
        <p className="text-muted">Here's your wellness overview</p>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats?.journal.entries_this_week || 0}</div>
          <div className="stat-label">Journal Entries This Week</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats?.medications.current_streak || 0}</div>
          <div className="stat-label">Medication Streak</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats?.fitness.current_streak || 0}</div>
          <div className="stat-label">Fitness Streak</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats?.fitness.total_steps_this_week.toLocaleString() || 0}</div>
          <div className="stat-label">Steps This Week</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mb-6">
        <h2 className="title">Quick Actions</h2>
        <div className="flex gap-4 flex-wrap">
          <Link to="/journal" className="btn btn-primary">New Journal Entry</Link>
          <Link to="/medications" className="btn btn-outline">Log Medication</Link>
          <Link to="/fitness" className="btn btn-outline">Log Activity</Link>
          <Link to="/circles" className="btn btn-outline">Support Circle</Link>
        </div>
      </div>

      {/* AI Insights */}
      {insights && (
        <div className="mb-6">
          <h2 className="title">AI Insights</h2>
          <div className="grid grid-2 gap-4">
            <div className="insight-card">
              <div className="flex justify-between items-center">
                <div>
                  <div className="insight-label">Average Mood</div>
                  <div className="insight-value">
                    {getMoodEmoji(insights.avg_mood)} {insights.avg_mood.toFixed(2)}
                  </div>
                </div>
              </div>
            </div>
            <div className="insight-card" style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' }}>
              <div className="insight-label">Predicted Next Mood</div>
              <div className="insight-value">
                {getMoodEmoji(insights.predicted_next_mood)} {insights.predicted_next_mood.toFixed(2)}
              </div>
            </div>
            <div className="insight-card" style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)' }}>
              <div className="insight-label">Fitness Correlation</div>
              <div className="insight-value">{(insights.fitness_correlation * 100).toFixed(0)}%</div>
            </div>
            <div className="insight-card" style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' }}>
              <div className="insight-label">Medication Correlation</div>
              <div className="insight-value">{(insights.medication_correlation * 100).toFixed(0)}%</div>
            </div>
          </div>
          <div className="card mt-4">
            <p className="text-muted">{insights.summary}</p>
          </div>
        </div>
      )}
    </div>
  );
}
