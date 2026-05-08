import { Hero } from './(marketing)/components/Hero'
import { ValueProps } from './(marketing)/components/ValueProps'
import { HowItWorks } from './(marketing)/components/HowItWorks'
import { Testimonials } from './(marketing)/components/Testimonials'
import { Footer } from './(marketing)/components/Footer'
import { ResetButton } from '@/components/ResetButton'

export default function HomePage() {
  return (
    <main className="min-h-screen">
      <ResetButton />
      <Hero />
      <ValueProps />
      <HowItWorks />
      <Testimonials />
      <Footer />
    </main>
  )
}
