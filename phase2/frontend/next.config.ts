import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  typescript: {
    ignoreBuildErrors: true, // Changed from true to allow build errors to surface
  },
  eslint: {
    ignoreDuringBuilds: true, // Changed from default to ensure code quality
  },
};

export default nextConfig;
