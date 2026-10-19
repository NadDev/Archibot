import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { fileURLToPath } from "node:url";

const workspaceRoot = fileURLToPath(new URL("..", import.meta.url));

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    fs: {
      allow: [workspaceRoot],
    },
    host: "0.0.0.0",
    port: 5173,
    strictPort: true,
  },
});
