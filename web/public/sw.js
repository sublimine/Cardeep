// Tombstone service worker.
//
// The previous frontend registered a cache-first service worker that answered every
// navigation from a cached `/index.html`. Browsers that visited the old site still
// have it installed, so simply deleting the file is not enough — they would keep
// serving the stale shell. This replacement takes over, drops every cache it finds,
// unregisters itself, and reloads open clients onto the live site. Once a visitor
// has run it, no service worker remains for this origin.
//
// Keep this file until it is safe to assume no stale installs are left in the wild.

self.addEventListener('install', () => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(keys.map((key) => caches.delete(key)));
      await self.registration.unregister();

      const clients = await self.clients.matchAll({ type: 'window' });
      for (const client of clients) {
        client.navigate(client.url);
      }
    })(),
  );
});

// Never intercept a request: everything goes straight to the network.
