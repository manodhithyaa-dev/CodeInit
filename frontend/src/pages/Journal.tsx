import { useState, useEffect } from 'react';
import { createJournal, getJournals, deleteJournal } from '../api';

export default function Journal() {
  const [content, setContent] = useState('');
  const [entries, setEntries] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [lastResult, setLastResult] = useState<{ sentiment_score: number; emotion_label: string; risk_flag: boolean } | null>(null);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [totalPages, setTotalPages] = useState(1);

  const fetchEntries = async () => {
    setLoading(true);
    try {
      const res = await getJournals({ page, limit: 10, search });
      setEntries(res.data);
      setTotalPages(Math.ceil(res.headers['content-range']?.split('/')[1] || 10 / 10) || 1);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEntries();
  }, [page, search]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;
    setSubmitting(true);
    try {
      const res = await createJournal(content);
      setLastResult(res.data);
      setContent('');
      fetchEntries();
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this entry?')) return;
    try {
      await deleteJournal(id);
      fetchEntries();
    } catch (err) {
      console.error(err);
    }
  };

  const getSentimentClass = (score: number) => {
    if (score > 0.1) return 'sentiment-positive';
    if (score < -0.1) return 'sentiment-negative';
    return 'sentiment-neutral';
  };

  return (
    <div className="page">
      <h1 className="title">Journal</h1>

      {/* Create Entry */}
      <div className="card mb-6">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="label">How are you feeling today?</label>
            <textarea
              className="input"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Write about your day, thoughts, or feelings..."
              rows={4}
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? 'Analyzing...' : 'Save Entry'}
          </button>
        </form>

        {lastResult && (
          <div className="mt-4 p-4" style={{ background: '#f0fdf4', borderRadius: '0.5rem' }}>
            <h3 className="text-sm font-semibold mb-2">Analysis Result</h3>
            <div className="flex gap-4 flex-wrap">
              <div>
                <span className="text-muted text-sm">Sentiment: </span>
                <span className={getSentimentClass(lastResult.sentiment_score)}>
                  {lastResult.sentiment_score.toFixed(2)}
                </span>
              </div>
              <div>
                <span className="text-muted text-sm">Emotion: </span>
                <span>{lastResult.emotion_label}</span>
              </div>
              {lastResult.risk_flag && (
                <span className="badge badge-danger">Risk Flag Detected</span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Search */}
      <div className="mb-4 flex gap-2">
        <input
          type="text"
          className="input"
          placeholder="Search entries..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          style={{ maxWidth: '300px' }}
        />
      </div>

      {/* Entries List */}
      {loading ? (
        <div className="loading">Loading...</div>
      ) : entries.length === 0 ? (
        <div className="empty-state">
          <p>No journal entries yet. Start writing!</p>
        </div>
      ) : (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Content</th>
                <th>Sentiment</th>
                <th>Emotion</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => (
                <tr key={entry.id}>
                  <td>{new Date(entry.created_at).toLocaleDateString()}</td>
                  <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {entry.content.substring(0, 100)}...
                  </td>
                  <td className={getSentimentClass(entry.sentiment_score || 0)}>
                    {entry.sentiment_score?.toFixed(2) || '-'}
                  </td>
                  <td>{entry.emotion_label || '-'}</td>
                  <td>
                    <button
                      className="btn btn-danger"
                      style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                      onClick={() => handleDelete(entry.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination */}
          <div className="pagination">
            <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>
              Previous
            </button>
            <span className="p-4">Page {page}</span>
            <button onClick={() => setPage(p => p + 1)} disabled={page >= totalPages}>
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
