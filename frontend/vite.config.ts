import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [
      vue(),
      {
        name: 'inject-api-url',
        transformIndexHtml(html) {
          // Use a placeholder that won't be treated as valid URL
          // The actual backend URL is fetched at runtime from /config.js
          return html;
        },
      },
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      port: Number(env.VITE_PORT) || 3000,
      host: env.VITE_HOST || '0.0.0.0',
    },
    define: {
      'import.meta.env.VITE_API_URL': JSON.stringify(env.VITE_API_URL || ''),
    },
  };
});
