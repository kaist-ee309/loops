/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: "/_loops_api/:path*",
        destination: "https://loops-api-273611200488.asia-northeast3.run.app/:path*",
      },
      {
        source: "/loops_api/:path*",
        destination: "https://loops-api-273611200488.asia-northeast3.run.app/:path*",
      },
    ]
  },
}

export default nextConfig
