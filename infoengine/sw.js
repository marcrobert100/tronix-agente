const CACHE = 'stitch-contos-v1';
const ASSETS = [
  '/agente/infoengine/',
  '/agente/infoengine/index.html',
  '/agente/infoengine/manifest.json',
  '/agente/infoengine/design-system/_variables.css',
  '/agente/infoengine/design-system/_typography.css',
  '/agente/infoengine/design-system/_components.css',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(cache => {
      return cache.addAll(ASSETS).catch(() => {});
    })
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)));
    })
  );
});

self.addEventListener('fetch', e => {
  if (e.request.url.includes('wa.me') || e.request.url.includes('html2pdf')) {
    return fetch(e.request).catch(() => {});
  }
  e.respondWith(
    caches.match(e.request).then(cached => {
      return cached || fetch(e.request).then(response => {
        if (response.ok && e.request.url.startsWith(self.location.origin)) {
          const clone = response.clone();
          caches.open(CACHE).then(cache => cache.put(e.request, clone));
        }
        return response;
      }).catch(() => cached);
    })
  );
});
