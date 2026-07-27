// Retired: the previous cache-first strategy served stale builds indefinitely
// after every deploy (cached /index.html on every navigation, cached assets
// forever). Self-destructs instead: clears its caches and unregisters so any
// browser that still has the old sw.js installed cleans itself up on next load.
self.addEventListener('install', () => {
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.map((k) => caches.delete(k))))
      .then(() => self.registration.unregister())
      .then(() => self.clients.matchAll())
      .then((clients) => clients.forEach((client) => client.navigate(client.url)))
  );
});
