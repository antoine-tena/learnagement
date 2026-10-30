import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    rules: {
      "*.svg": {
        loaders: ["@svgr/webpack"],
        as: "*.js",
      },
    },
  },
  watchOptions: {
    pollIntervalMs: 1000, // Vérifie les changements toutes les secondes
  },
};

export default nextConfig;
