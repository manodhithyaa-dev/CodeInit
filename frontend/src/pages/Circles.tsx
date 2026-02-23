import { useState, useEffect } from 'react';
import { createCircle, getCircles, joinCircle, getCircleMessages, sendCircleMessage, leaveCircle } from '../api';

export default function Circles() {
  const [circles, setCircles] = useState<any[]>([]);
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showMessages, setShowMessages] = useState<number | null>(null);
  const [circleIdInput, setCircleIdInput] = useState('');
  const [newCircleName, setNewCircleName] = useState('');
  const [messageText, setMessageText] = useState('');
  const [selectedCircle, setSelectedCircle] = useState<any>(null);

  const fetchCircles = async () => {
    setLoading(true);
    try {
      console.log('Fetching circles...');
      const res = await getCircles();
      console.log('Circles response:', res.data);
      setCircles(res.data);
    } catch (err: any) {
      console.error('Error fetching circles:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCircles();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCircleName.trim()) {
      alert('Please enter a circle name');
      return;
    }
    try {
      console.log('Creating circle with name:', newCircleName);
      const result = await createCircle(newCircleName);
      console.log('Circle created:', result.data);
      setNewCircleName('');
      setCircles([]);
      await fetchCircles();
    } catch (err: any) {
      console.error('Error creating circle:', err);
      console.error('Error response:', err.response);
      const msg = err?.response?.data?.detail || err?.response?.data || err?.message || 'Failed to create circle';
      alert('Error: ' + JSON.stringify(msg));
    }
  };

  const handleJoin = async () => {
    if (!circleIdInput) return;
    try {
      const circleId = circleIdInput.trim();
      if (!circleId) {
        alert('Please enter a circle ID');
        return;
      }
      await joinCircle(circleId);
      setCircleIdInput('');
      setCircles([]);
      await fetchCircles();
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || 'Failed to join circle';
      alert(msg);
    }
  };

  const handleLeave = async (id: number) => {
    if (!confirm('Leave this circle?')) return;
    try {
      await leaveCircle(id);
      setCircles(circles.filter(c => c.id !== id));
      await fetchCircles();
    } catch (err: any) {
      console.error('Error leaving circle:', err);
      const msg = err?.response?.data?.detail || err?.message || 'Failed to leave circle';
      alert(msg);
    }
  };

  const handleViewMessages = async (circle: any) => {
    setSelectedCircle(circle);
    setShowMessages(circle.id);
    try {
      const res = await getCircleMessages(circle.id);
      setMessages(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!messageText || !selectedCircle) return;
    try {
      await sendCircleMessage(selectedCircle.id, {
        receiver_id: selectedCircle.members?.[0]?.user_id || 1,
        message: messageText
      });
      setMessageText('');
      setMessages([]);
      await handleViewMessages(selectedCircle);
    } catch (err: any) {
      console.error('Error sending message:', err);
      alert(err.response?.data?.detail || 'Failed to send message');
    }
  };

  return (
    <div className="page">
      <h1 className="title">Support Circles</h1>

      {/* Actions */}
      <div className="grid grid-2 gap-4 mb-6">
        <div className="card">
          <h3 className="mb-4">Create New Circle</h3>
          <form onSubmit={handleCreate}>
            <div className="form-group">
              <input
                type="text"
                className="input"
                placeholder="Circle name"
                value={newCircleName}
                onChange={(e) => setNewCircleName(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary">Create Circle</button>
          </form>
        </div>
        <div className="card">
          <h3 className="mb-4">Join Existing Circle</h3>
          <div className="flex gap-2">
            <input
              type="text"
              className="input"
              placeholder="Circle ID"
              value={circleIdInput}
              onChange={(e) => setCircleIdInput(e.target.value)}
            />
            <button className="btn btn-primary" onClick={handleJoin}>Join</button>
          </div>
        </div>
      </div>

      {/* Circles List */}
      {loading ? (
        <div className="loading">Loading...</div>
      ) : circles.length === 0 ? (
        <div className="empty-state">
          <p>No circles yet. Create or join one!</p>
        </div>
      ) : (
        <div className="grid grid-2 gap-4">
          {circles.map((circle) => (
            <div key={circle.id} className="card">
              <h3>{circle.name}</h3>
              <p className="text-muted text-sm">ID: {circle.id}</p>
              <p className="text-muted text-sm">Created: {new Date(circle.created_at).toLocaleDateString()}</p>
              <div className="flex gap-2 mt-4">
                <button className="btn btn-primary" onClick={() => handleViewMessages(circle)}>
                  Messages
                </button>
                <button className="btn btn-danger" onClick={() => handleLeave(circle.id)}>
                  Leave
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Messages Modal */}
      {showMessages && (
        <div className="modal-overlay" onClick={() => setShowMessages(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Messages - {selectedCircle?.name}</h2>
              <button className="modal-close" onClick={() => setShowMessages(null)}>&times;</button>
            </div>
            
            <div style={{ maxHeight: '300px', overflowY: 'auto', marginBottom: '1rem' }}>
              {messages.length === 0 ? (
                <p className="text-muted text-center">No messages yet</p>
              ) : (
                messages.map((msg) => (
                  <div key={msg.id} className="p-4 mb-2" style={{ background: '#f8fafc', borderRadius: '0.5rem' }}>
                    <p className="text-sm">{msg.message}</p>
                    <p className="text-muted text-sm">{new Date(msg.created_at).toLocaleString()}</p>
                  </div>
                ))
              )}
            </div>

            <form onSubmit={handleSendMessage}>
              <div className="form-group">
                <textarea
                  className="input"
                  placeholder="Send an encouraging message..."
                  value={messageText}
                  onChange={(e) => setMessageText(e.target.value)}
                  rows={2}
                />
              </div>
              <button type="submit" className="btn btn-primary">Send</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
