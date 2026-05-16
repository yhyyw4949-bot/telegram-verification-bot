/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    remotePatterns: [{ hostname: 'localhost' }],
  },
}

module.exports = nextConfig
