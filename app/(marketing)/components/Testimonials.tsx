'use client'

import { Card, CardContent } from '@/components/ui/card'
import { motion } from 'framer-motion'
import { Star } from 'lucide-react'

const testimonials = [
  {
    name: "Sarah Chen",
    location: "San Francisco, CA", 
    rating: 5,
    text: "Finally! A styling service that actually gets my taste. The recommendations were spot-on and I found pieces I never would have discovered on my own.",
    image: "/images/testimonial-1.jpg"
  },
  {
    name: "Marcus Johnson",
    location: "New York, NY",
    rating: 5, 
    text: "I was skeptical at first, but the style quiz really worked. Got some amazing recommendations that fit my budget and style perfectly.",
    image: "/images/testimonial-2.jpg"
  },
  {
    name: "Emma Rodriguez",
    location: "Austin, TX",
    rating: 5,
    text: "Love that there's no subscription! I can take the quiz whenever I need fresh style inspiration. The swipe feature is so fun and addictive.",
    image: "/images/testimonial-3.jpg"
  },
  {
    name: "David Kim",
    location: "Seattle, WA",
    rating: 5,
    text: "The algorithm really understands my style. I've found so many great pieces from brands I'd never heard of before. Highly recommend!",
    image: "/images/testimonial-4.jpg"
  }
]

export function Testimonials() {
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
            What Our Style Seekers Say
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Join thousands who've discovered their perfect style with our personalized recommendations.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={testimonial.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <Card className="h-full border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
                <CardContent className="p-6">
                  <div className="flex items-center gap-1 mb-4">
                    {Array.from({ length: testimonial.rating }, (_, i) => (
                      <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <p className="text-gray-700 text-sm leading-relaxed mb-6">
                    "{testimonial.text}"
                  </p>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                      <span className="text-sm font-semibold text-gray-600">
                        {testimonial.name.split(' ').map(n => n[0]).join('')}
                      </span>
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900 text-sm">
                        {testimonial.name}
                      </p>
                      <p className="text-gray-500 text-xs">
                        {testimonial.location}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
          className="text-center mt-12"
        >
          <div className="flex items-center justify-center gap-2 text-sm text-gray-600">
            <div className="flex">
              {Array.from({ length: 5 }, (_, i) => (
                <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
              ))}
            </div>
            <span>4.9/5 from 2,847 reviews</span>
          </div>
        </motion.div>
      </div>
    </section>
  )
}