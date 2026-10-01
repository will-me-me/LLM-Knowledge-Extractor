import "@mdi/font/css/materialdesignicons.css";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import "vuetify/styles";
import { createVuetify } from "vuetify";
import { mdi } from "vuetify/iconsets/mdi";

export default defineNuxtPlugin((app) => {
  const vuetify = createVuetify({
    components,
    directives,
    ssr: true,
    icons: {
      defaultSet: "mdi",
      sets: { mdi },
    },
    theme: {
      defaultTheme: "light",
      themes: {
        light: {
          dark: false,
          colors: {
            primary: "#6366f1",
            secondary: "#a855f7",
            accent: "#06b6d4",
            error: "#ef4444",
            info: "#3b82f6",
            success: "#22c55e",
            warning: "#f59e0b",
            background: "#F4F5FB",
            surface: "#FFFFFF",
            "on-background": "#111827",
            "on-surface": "#111827",
            "on-primary": "#FFFFFF",
            "on-secondary": "#FFFFFF",
            "surface-variant": "#E5E7EB",
            "on-surface-variant": "#374151",
            "surface-bright": "#FFFFFF",
            "surface-light": "#F9FAFB",
            "surface-dark": "#1E1E1E",
            "border-color": "#E5E7EB",
          },
          variables: {
            "border-color": "#E5E7EB",
            "border-opacity": 1,
            "high-emphasis-opacity": 0.95,
            "medium-emphasis-opacity": 0.7,
            "disabled-opacity": 0.4,
          },
        },
        dark: {
          dark: true,
          colors: {
            primary: "#818cf8",
            secondary: "#c084fc",
            accent: "#22d3ee",
            error: "#f87171",
            info: "#60a5fa",
            success: "#4ade80",
            warning: "#fbbf24",
            background: "#0B0B14",
            surface: "#15151F",
            "on-background": "#F3F4F6",
            "on-surface": "#F3F4F6",
            "on-primary": "#0B0B14",
            "on-secondary": "#0B0B14",
            "surface-variant": "#2A2A38",
            "on-surface-variant": "#D1D5DB",
            "surface-bright": "#2A2A38",
            "surface-light": "#1F1F2E",
            "surface-dark": "#0B0B14",
            "border-color": "#2A2A38",
          },
          variables: {
            "border-color": "#2A2A38",
            "border-opacity": 1,
            "high-emphasis-opacity": 0.95,
            "medium-emphasis-opacity": 0.7,
            "disabled-opacity": 0.4,
          },
        },
      },
    },
  });
  app.vueApp.use(vuetify);
});
