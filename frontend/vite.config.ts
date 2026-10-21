import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

const workspaceRoot = fileURLToPath(new URL("..", import.meta.url));

export default defineConfig(({ mode }) => {
  const frontendEnv = loadEnv(mode, process.cwd(), "VITE_");
  const backendEnv = loadEnv(mode, resolve(workspaceRoot, "backend"), "SUPABASE_");
  const supabaseUrl = frontendEnv.VITE_SUPABASE_URL || backendEnv.SUPABASE_URL || "";
  const supabasePublishableKey =
    frontendEnv.VITE_SUPABASE_PUBLISHABLE_KEY || backendEnv.SUPABASE_PUBLISHABLE_KEY || "";

  return {
    plugins: [react(), tailwindcss()],
    define: {
      "import.meta.env.VITE_SUPABASE_URL": JSON.stringify(supabaseUrl),
      "import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY": JSON.stringify(supabasePublishableKey),
    },
    server: {
      fs: {
        allow: [workspaceRoot],
      },
      host: "0.0.0.0",
      port: 5173,
      strictPort: true,
    },
  };
});
