'use client'

import { Card, CardContent } from '@/components/ui/card'
import { motion } from 'framer-motion'
import { Sparkles, Truck, CreditCard, Users } from 'lucide-react'

const valueProps = [
  {
    icon: Sparkles,
    title: "Try Us Free",
    description: "No subscription, no commitment. Take the quiz and get personalized recommendations at no cost.",
    highlight: "100% Free"
  },
  {
    icon: Users,
    title: "Human Stylists",
    description: "Our recommendations are powered by real fashion experts who understand your unique style preferences.",
    highlight: "Expert Curated"
  },
  {
    icon: Truck,
    title: "Free Shipping & Returns",
    description: "Try clothes at home with free shipping both ways. Keep what you love, return the rest.",
    highlight: "No Risk"
  },
  {
    icon: CreditCard,
    title: "Your Style, Your Budget",
    description: "Set your budget and we'll find amazing pieces that fit both your style and your wallet.",
    highlight: "Budget Friendly"
  }
]

export function ValueProps() {
  return (
    <section className="py-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            What You Get
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Experience personal styling without the commitment. Get expert recommendations 
            tailored to your style, budget, and lifestyle.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {valueProps.map((prop, index) => (
            <motion.div
              key={prop.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <Card className="h-full border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
                <CardContent className="p-6 text-center">
                  <div className="mb-4">
                    <div className="inline-flex items-center justify-center w-12 h-12 bg-black text-white rounded-full mb-2">
                      <prop.icon className="w-6 h-6" />
                    </div>
                    <div className="text-xs font-semibold text-green-600 bg-green-100 rounded-full px-2 py-1 inline-block">
                      {prop.highlight}
                    </div>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {prop.title}
                  </h3>
                  <p className="text-gray-600 text-sm leading-relaxed">
                    {prop.description}
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}