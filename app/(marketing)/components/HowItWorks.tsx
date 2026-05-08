'use client'

import { Button } from '@/components/ui/button'
import { motion } from 'framer-motion'
import { CheckCircle, Heart, Sparkles } from 'lucide-react'
import Link from 'next/link'

const steps = [
  {
    number: "01",
    icon: CheckCircle,
    title: "Take Your Style Quiz",
    description: "Tell us about your style preferences, budget, and lifestyle in just 5 minutes.",
    details: [
      "Share your size and fit preferences",
      "Choose your favorite styles and colors", 
      "Set your budget and occasions",
      "Tell us about your lifestyle"
    ]
  },
  {
    number: "02",
    icon: Sparkles,
    title: "Get Matched with Perfect Pieces",
    description: "Our styling algorithm finds clothes that match your unique taste from 1,000s of brands.",
    details: [
      "AI-powered style matching",
      "Curated by human stylists",
      "From affordable to luxury brands",
      "Personalized for your body type"
    ]
  },
  {
    number: "03",
    icon: Heart,
    title: "Swipe & Discover",
    description: "Browse through your personalized recommendations and save the pieces you love.",
    details: [
      "Tinder-style browsing experience",
      "Like or pass on each recommendation",
      "Build your wishlist of favorites",
      "Get similar style suggestions"
    ]
  }
]

export function HowItWorks() {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-black text-gray-900 mb-6">
            How It Works
          </h2>
          <p className="text-xl text-gray-700 max-w-3xl mx-auto leading-relaxed font-medium">
            Get personalized style recommendations in three simple steps. 
            No subscription, no commitment—just great style discoveries.
          </p>
        </motion.div>

        <div className="space-y-16">
          {steps.map((step, index) => (
            <motion.div
              key={step.number}
              initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50, y: 30 }}
              whileInView={{ opacity: 1, x: 0, y: 0 }}
              whileHover={{ 
                scale: 1.02,
                rotateY: index % 2 === 0 ? 2 : -2,
                transition: { duration: 0.3 }
              }}
              transition={{ 
                duration: 0.8, 
                delay: index * 0.2,
                type: "spring",
                stiffness: 100,
                damping: 20
              }}
              viewport={{ once: true }}
              className={`flex flex-col lg:flex-row items-center gap-8 lg:gap-12 ${
                index % 2 === 1 ? 'lg:flex-row-reverse' : ''
              } transform-gpu`}
              style={{
                transformStyle: "preserve-3d"
              }}
            >
              <div className="flex-1 text-center lg:text-left">
                <div className="inline-flex items-center gap-3 mb-4">
                  <motion.div 
                    className="flex items-center justify-center w-16 h-16 bg-black text-white rounded-full shadow-lg"
                    whileHover={{ 
                      scale: 1.1, 
                      rotate: 5,
                      boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.3)"
                    }}
                    animate={{
                      y: [0, -5, 0],
                    }}
                    transition={{
                      y: {
                        duration: 2,
                        repeat: Infinity,
                        ease: "easeInOut"
                      }
                    }}
                  >
                    <step.icon className="w-8 h-8" />
                  </motion.div>
                  <motion.span 
                    className="text-[2rem] md:text-[4rem] lg:text-[5rem] xl:text-[6rem] font-black text-black/40 leading-none select-none"
                    whileHover={{ 
                      scale: 1.1,
                      color: "rgba(0, 0, 0, 0.6)"
                    }}
                    animate={{
                      x: [0, 3, 0],
                    }}
                    transition={{
                      x: {
                        duration: 3,
                        repeat: Infinity,
                        ease: "easeInOut",
                        delay: index * 0.5
                      }
                    }}
                    style={{
                      fontSize: "clamp(2rem, 5vw, 6rem)",
                      textShadow: "2px 2px 4px rgba(0,0,0,0.1)"
                    }}
                  >
                    {step.number}
                  </motion.span>
                </div>
                <h3 className="text-3xl md:text-4xl font-black text-gray-900 mb-6">
                  {step.title}
                </h3>
                <p className="text-xl text-gray-700 mb-8 leading-relaxed font-medium">
                  {step.description}
                </p>
                <ul className="space-y-3 text-left">
                  {step.details.map((detail) => (
                    <li key={detail} className="flex items-center gap-3 text-gray-700">
                      <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                      <span className="font-medium">{detail}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="flex-1">
                <motion.div 
                  className="bg-gradient-to-br from-gray-50 via-white to-gray-100 rounded-2xl p-6 aspect-square flex items-center justify-center overflow-hidden shadow-xl border border-gray-200/50"
                  whileHover={{ 
                    rotateY: 5, 
                    rotateX: 5, 
                    scale: 1.02,
                    boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)"
                  }}
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  style={{
                    transformStyle: "preserve-3d",
                    perspective: "1000px"
                  }}
                >
                  {step.title === "Take Your Style Quiz" ? (
                    <motion.img 
                      src="/images/quiz_gen.png"
                      alt={step.title}
                      className="w-full h-full object-cover rounded-xl shadow-lg"
                      whileHover={{ 
                        scale: 1.05,
                        rotateZ: 2,
                        filter: "brightness(1.1)"
                      }}
                      transition={{ duration: 0.3 }}
                      style={{
                        transform: "translateZ(20px)"
                      }}
                    />
                  ) : step.title === "Get Matched with Perfect Pieces" ? (
                    <motion.img 
                      src="/images/pieced_image.png"
                      alt={step.title}
                      className="w-full h-full object-cover rounded-xl shadow-lg"
                      whileHover={{ 
                        scale: 1.05,
                        rotateZ: 2,
                        filter: "brightness(1.1)"
                      }}
                      transition={{ duration: 0.3 }}
                      style={{
                        transform: "translateZ(20px)"
                      }}
                    />
                  ) : step.title === "Swipe & Discover" ? (
                    <motion.img 
                      src="/images/tinder.png"
                      alt={step.title}
                      className="w-full h-full object-cover rounded-xl shadow-lg"
                      whileHover={{ 
                        scale: 1.05,
                        rotateZ: 2,
                        filter: "brightness(1.1)"
                      }}
                      transition={{ duration: 0.3 }}
                      style={{
                        transform: "translateZ(20px)"
                      }}
                    />
                  ) : (
                    <motion.div
                      className="relative"
                      whileHover={{ 
                        rotateY: 10,
                        scale: 1.1
                      }}
                      transition={{ duration: 0.3 }}
                      style={{
                        transform: "translateZ(30px)"
                      }}
                    >
                      <step.icon className="w-28 h-28 text-gray-400 drop-shadow-lg" />
                      <div className="absolute -inset-4 bg-gradient-to-r from-purple-400/20 to-pink-400/20 blur-xl rounded-full"></div>
                    </motion.div>
                  )}
                </motion.div>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
          className="text-center mt-16"
        >
          <Button asChild size="lg" className="text-lg px-8 py-6">
            <Link href="/quiz">Start Your Style Quiz</Link>
          </Button>
          <p className="text-sm text-gray-500 mt-4">
            No payment required • Takes less than 5 minutes
          </p>
        </motion.div>
      </div>
    </section>
  )
}