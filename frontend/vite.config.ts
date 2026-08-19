import { fileURLToPath, URL } from "node:url";

import vue from "@vitejs/plugin-vue";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        // Overridable so Playwright can run several isolated (frontend, backend)
        // pairs at once, each pointed at its own seeded backend instance.
        target: `http://localhost:${process.env.VITE_BACKEND_PORT ?? "5000"}`,
        changeOrigin: true,
      },
    },
  },
});
