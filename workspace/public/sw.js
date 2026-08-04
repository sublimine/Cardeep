// Bumped so the activate handler evicts every cache written by the cache-first
// version above — otherwise a browser that already has 'cardeep-v2' keeps serving
// the shell it stored under the old rules.
const CACHE = 'cardeep-v3';
const SHELL = ['/', '/index.html'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  const { request } = e;
  const url = new URL(request.url);

  // API: network-first, fall back to cache (only cache GET — never POST/PUT/PATCH).
  if (url.pathname.startsWith('/api/')) {
    e.respondWith(
      fetch(request)
        .then((res) => {
          const clone = res.clone();
          if (res.ok && request.method === 'GET') {
            caches.open(CACHE).then((c) => c.put(request, clone));
          }
          return res;
        })
        .catch(() => (request.method === 'GET' ? caches.match(request) : Promise.reject(new Error('offline'))))
    );
    return;
  }

  // Navigation: NETWORK FIRST, cache only as the offline fallback.
  //
  // This was cache-first, and cache-first on the document is how a deployment
  // stops being visible: the browser kept serving the shell it had and only
  // reached the network when that failed, so every visitor kept yesterday's page
  // until they cleared storage. It was already fixed once (5e74203) and came back
  // with the full-session revert (8cd8c6c).
  //
  // Offline still works — the cached shell is still there, it is simply the
  // fallback rather than the answer.
  if (request.mode === 'navigate') {
    e.respondWith(
      fetch(request)
        .then((res) => {
          if (res.ok) {
            const clone = res.clone();
            caches.open(CACHE).then((c) => c.put('/index.html', clone));
          }
          return res;
        })
        .catch(() => caches.match('/index.html'))
    );
    return;
  }

  // Static assets: cache-first
  e.respondWith(caches.match(request).then((r) => r || fetch(request)));
});
