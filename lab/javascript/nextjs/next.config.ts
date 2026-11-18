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
  logging: {
    incomingRequests: {
      ignore: [/^\/health$/],
    },
  },
  watchOptions: {
    pollIntervalMs: 1000, // Vérifie les changements toutes les secondes
  },
};

export default nextConfig;
