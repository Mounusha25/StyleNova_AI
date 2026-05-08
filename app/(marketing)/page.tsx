import { Hero } from './components/Hero'
import { ValueProps } from './components/ValueProps'
import { HowItWorks } from './components/HowItWorks'
import { Testimonials } from './components/Testimonials'
import { Footer } from './components/Footer'

export default function HomePage() {
  return (
    <main className="min-h-screen">
      <Hero />
      <ValueProps />
      <HowItWorks />
      <Testimonials />
      <Footer />
    </main>
  )
}