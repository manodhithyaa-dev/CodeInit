import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Layout() {
  const { logout } = useAuth();

  return (
    <>
      <nav className="nav">
        <NavLink to="/dashboard" className="nav-brand">MindMesh</NavLink>
        <div className="nav-links">
          <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
            Dashboard
          </NavLink>
          <NavLink to="/journal" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
            Journal
          </NavLink>
          <NavLink to="/medications" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
            Medications
          </NavLink>
          <NavLink to="/fitness" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
            Fitness
          </NavLink>
          <NavLink to="/circles" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
            Circles
          </NavLink>
          <NavLink to="/profile" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
            Profile
          </NavLink>
          <button onClick={logout} className="btn btn-outline" style={{ marginLeft: '0.5rem' }}>
            Logout
          </button>
        </div>
      </nav>
      <main>
        <Outlet />
      </main>
    </>
  );
}
