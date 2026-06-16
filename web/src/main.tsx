import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import './styles/global.css';
import { Layout } from './components/Layout';
import { Landing } from './routes/Landing';

const qc = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 60_000, retry: 1, refetchOnWindowFocus: false },
  },
});

function Stub({ title }: { title: string }) {
  return (
    <div className="container" style={{ padding: 'var(--space-16) 0', minHeight: '60vh' }}>
      <h2 style={{ fontSize: 'var(--text-xl)' }}>{title}</h2>
      <p style={{ color: 'var(--text-2)', marginTop: 'var(--space-3)' }}>
        En construccion — siguiente fase del plan de implementacion.
      </p>
    </div>
  );
}

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Landing /> },
      { path: 'explore', element: <Stub title="Explorar inventario" /> },
      { path: 'dealer/:cdp', element: <Stub title="Dealer" /> },
      { path: 'vehicle/:ulid', element: <Stub title="Vehiculo" /> },
    ],
  },
]);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={qc}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>,
);
