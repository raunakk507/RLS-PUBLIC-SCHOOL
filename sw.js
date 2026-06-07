const CACHE_NAME = 'rlsps-cache-v4';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './manifest.json',
  './logo.png',
  './pwa-icon-192.png',
  './pwa-icon-512.png',
  './activity.jpg',
  'https://cdn.tailwindcss.com',
  'https://unpkg.com/react@18/umd/react.production.min.js',
  'https://unpkg.com/react-dom@18/umd/react-dom.production.min.js',
  'https://unpkg.com/lucide@latest',
  'https://checkout.razorpay.com/v1/checkout.js',
  'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js',
  'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600&display=swap',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css'
];

// Install Service Worker and cache all vital resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[Service Worker] Pre-caching offline portal shell...');
      // Use map to safely cache items one by one, ignoring single failures
      const cachePromises = ASSETS_TO_CACHE.map((asset) => {
        return cache.add(asset).catch((err) => {
          console.warn(`[Service Worker] Failed to cache asset: ${asset}`, err);
        });
      });
      return Promise.all(cachePromises);
    }).then(() => self.skipWaiting())
  );
});

// Activate and clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('[Service Worker] Removing old cache:', key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Intercept fetch requests with an intelligent Network-First strategy
// falls back to cache if offline, except for API routes which bypass cache
self.addEventListener('fetch', (event) => {
  // Avoid caching API calls, external webhook calls or localhost APIs
  if (event.request.url.includes('/api/') || event.request.url.includes('razorpay.com') || event.request.url.includes('chrome-extension')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // Network-First with Cache-Fallback Strategy
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Cache new successful standard GET responses for future offline use
        if (response && response.status === 200 && event.request.method === 'GET') {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      })
      .catch(() => {
        // If network request fails (Offline), attempt to match from Cache
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }
          // Special fallback for root or document navigation if offline
          if (event.request.mode === 'navigate') {
            return caches.match('./') || caches.match('./index.html');
          }
          return new Response('Network connection lost. View is offline.', {
            status: 408,
            headers: { 'Content-Type': 'text/plain' }
          });
        });
      })
  );
});
