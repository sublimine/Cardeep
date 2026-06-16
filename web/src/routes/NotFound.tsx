import { Link } from 'react-router-dom';
import './notfound.css';

export function NotFound() {
  return (
    <div className="container notfound">
      <span className="notfound__code">404</span>
      <p className="notfound__msg">Esta página no existe en el mapa.</p>
      <Link to="/" className="btn btn--primary">
        Volver al inicio
      </Link>
    </div>
  );
}
