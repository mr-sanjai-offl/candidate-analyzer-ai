import type { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: ['/dashboard/admin/', '/dashboard/recruiter/'],
    },
    sitemap: 'https://apexguidance.ai/sitemap.xml',
  }
}
