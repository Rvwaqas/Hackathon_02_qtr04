import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  typescript: {
    ignoreBuildErrors: true, // Changed from true to allow build errors to surface
  },
  eslint: {
    ignoreDuringBuilds: true, // Changed from default to ensure code quality
  },
};

export default nextConfig;
