import { Link, NavLink, Outlet, ScrollRestoration } from 'react-router-dom';
import './Layout.css';

const NAV = [
  { to: '/', label: 'Mapa', end: true },
  { to: '/explore', label: 'Explorar', end: false },
] as const;

export function Layout() {
  return (
    <div className="app">
      <header className="topbar">
        <div className="container topbar__inner">
          <Link to="/" className="brand" aria-label="CARDEEP — inicio">
            <span className="brand__mark" aria-hidden="true" />
            <span className="brand__word">
              CARD<span className="brand__deep">EEP</span>
            </span>
          </Link>

          <nav className="topnav" aria-label="Navegacion principal">
            {NAV.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) => `topnav__link${isActive ? ' is-active' : ''}`}
              >
                {item.label}
              </NavLink>
            ))}
            <a className="topnav__cta" href="https://github.com/sublimine/Cardeep" target="_blank" rel="noreferrer noopener">
              Acceso API
            </a>
          </nav>
        </div>
      </header>

      <main className="app__main">
        <Outlet />
      </main>

      <footer className="appfoot">
        <div className="container appfoot__inner">
          <span className="mono appfoot__tag">CARDEEP · ES</span>
          <span className="appfoot__note">
            El mapa completo de un mercado que hoy nadie tiene entero.
          </span>
        </div>
      </footer>

      <ScrollRestoration />
    </div>
  );
}
