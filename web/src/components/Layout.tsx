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
          <Link to="/" className="brand" aria-label="cardeep — inicio">
            <img
              className="brand__icon"
              src="/brand/cardeep-icon-blue.png"
              alt=""
              aria-hidden="true"
              width={34}
              height={34}
            />
            <span className="brand__word">cardeep</span>
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
          <span className="appfoot__brand">
            <img src="/brand/cardeep-icon-blue.png" alt="" aria-hidden="true" width={20} height={20} />
            <span className="mono appfoot__tag">cardeep · ES</span>
          </span>
          <span className="appfoot__note">
            El mapa completo de un mercado que hoy nadie tiene entero.
          </span>
        </div>
      </footer>

      <ScrollRestoration />
    </div>
  );
}
