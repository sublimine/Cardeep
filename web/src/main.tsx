import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import './styles/global.css';
import { Layout } from './components/Layout';
import { Landing } from './routes/Landing';
import { Explore } from './routes/Explore';
import { Dealer } from './routes/Dealer';
import { Vehicle } from './routes/Vehicle';
import { NotFound } from './routes/NotFound';

const qc = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 60_000, retry: 1, refetchOnWindowFocus: false },
  },
});

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Landing /> },
      { path: 'explore', element: <Explore /> },
      { path: 'dealer/:cdp', element: <Dealer /> },
      { path: 'vehicle/:ulid', element: <Vehicle /> },
      { path: '*', element: <NotFound /> },
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
