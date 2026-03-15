// CICT Grade Portal — Service Worker (static assets only)
// IMPORTANT: Do not cache HTML pages with CSRF tokens.
const CACHE_NAME = 'cict-portal-static-v2';

// Pre-cache static assets only.
const PRECACHE_ASSETS = [
  '/static/css/main.css',
  '/static/manifest.webmanifest',
];

// Install: pre-cache core assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_ASSETS);
    })
  );
  self.skipWaiting();
});

// Activate: clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys
          .filter((key) => key !== CACHE_NAME)
          .map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

// Fetch: cache static files only, never dynamic HTML routes.
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // Ignore cross-origin requests.
  if (url.origin !== self.location.origin) return;

  // Never cache navigation/document requests (dynamic pages, forms, CSRF pages).
  if (event.request.mode === 'navigate') return;

  // Cache only static assets under /static/.
  if (!url.pathname.startsWith('/static/')) return;

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Cache successful responses
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, clone);
          });
        }
        return response;
      })
      .catch(() => {
        // Serve static asset from cache when offline.
        return caches.match(event.request).then((cached) => cached || Response.error());
      })
  );
});
