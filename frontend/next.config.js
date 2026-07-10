/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow images from any HTTPS source (logo_url may be external CDN or data URI)
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**" },
    ],
  },

  // Expose public env vars to the browser — all must be prefixed NEXT_PUBLIC_
  // No secrets here; secrets live server-side only.
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
};

module.exports = nextConfig;
