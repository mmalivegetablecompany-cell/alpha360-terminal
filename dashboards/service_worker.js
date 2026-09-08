// Service Worker for 24/7 Offline Caching & Background App Shell
const CACHE_NAME = 'market-radar-cache-v2';
const URLS_TO_CACHE = [
  './Advance_Technical_Analysis_424_Stocks.html',
  './Stock_Growth_and_Selection_Analyzer.html',
  './xlsx.full.min.js'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(URLS_TO_CACHE);
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(name => {
          if (name !== CACHE_NAME) {
            return caches.delete(name);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  // Network first for APIs, cache fallback for shell
  if (event.request.url.includes('/api/')) {
    event.respondWith(
      fetch(event.request).catch(() => new Response('{"status":"offline"}', { headers: { 'Content-Type': 'application/json' } }))
    );
  } else {
    event.respondWith(
      fetch(event.request).catch(() => caches.match(event.request))
    );
  }
});
