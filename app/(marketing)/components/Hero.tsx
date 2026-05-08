'use client'

import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { motion } from 'framer-motion'
import Link from 'next/link'

const heroContent = {
  women: {
    title: "Your Perfect Style, Discovered",
    subtitle: "Take our style quiz and get personalized clothing recommendations from 1,000s of brands. No subscription required.",
    image: "/images/hero-women.png"
  },
  men: {
    title: "Find Your Style, Effortlessly",
    subtitle: "Discover clothes that fit your style and lifestyle. Curated recommendations just for you.",
    image: "/images/hero-men.png"
  },
  kids: {
    title: "Stylish Kids' Clothes Made Easy",
    subtitle: "Find the perfect outfits for your little ones with our fun, easy style quiz.",
    image: "/images/hero-kids.png"
  }
}

export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      <Tabs defaultValue="women" className="w-full">
        <div className="absolute inset-0 z-0">
          <TabsContent value="women" className="m-0">
            <div 
              className="absolute inset-0 bg-cover bg-[center_bottom]"
              style={{ 
                backgroundImage: `url(${heroContent.women.image})`,
                filter: 'blur(1px)'
              }}
            />
            <div className="absolute inset-0 bg-black/50" />
          </TabsContent>
          <TabsContent value="men" className="m-0">
            <div 
              className="absolute inset-0 bg-cover bg-[center_bottom]"
              style={{ 
                backgroundImage: `url(${heroContent.men.image})`,
                filter: 'blur(1px)'
              }}
            />
            <div className="absolute inset-0 bg-black/50" />
          </TabsContent>
          <TabsContent value="kids" className="m-0">
            <div 
              className="absolute inset-0 bg-cover bg-center"
              style={{ 
                backgroundImage: `url(${heroContent.kids.image})`,
                filter: 'blur(1px)'
              }}
            />
            <div className="absolute inset-0 bg-black/50" />
          </TabsContent>
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <TabsList className="mb-8 bg-white/15 backdrop-blur-sm p-1 gap-1 h-auto rounded-xl">
            <TabsTrigger 
              value="women" 
              className="data-[state=active]:bg-white data-[state=active]:text-black px-8 py-4 text-lg font-semibold rounded-lg transition-all duration-300 text-white"
            >
              Women
            </TabsTrigger>
            <TabsTrigger 
              value="men" 
              className="data-[state=active]:bg-white data-[state=active]:text-black px-8 py-4 text-lg font-semibold rounded-lg transition-all duration-300 text-white"
            >
              Men
            </TabsTrigger>
            <TabsTrigger 
              value="kids" 
              className="data-[state=active]:bg-white data-[state=active]:text-black px-8 py-4 text-lg font-semibold rounded-lg transition-all duration-300 text-white"
            >
              Kids
            </TabsTrigger>
          </TabsList>

          <TabsContent value="women">
            <HeroContent content={heroContent.women} />
          </TabsContent>
          <TabsContent value="men">
            <HeroContent content={heroContent.men} />
          </TabsContent>
          <TabsContent value="kids">
            <HeroContent content={heroContent.kids} />
          </TabsContent>
        </div>
      </Tabs>
    </section>
  )
}

function HeroContent({ content }: { content: typeof heroContent.women }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      className="text-white"
    >
      <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight text-shadow-lg">
        {content.title}
      </h1>
      <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto leading-relaxed text-shadow">
        {content.subtitle}
      </p>
      <div className="flex flex-col sm:flex-row gap-8 justify-center items-center px-4">
        <motion.div
          whileHover={{ 
            scale: 1.15,
            y: -8,
            rotate: 1,
            boxShadow: "0 20px 40px rgba(59, 130, 246, 0.6)"
          }}
          transition={{ duration: 0.3 }}
          className="z-10"
        >
          <Button asChild size="lg" className="text-lg px-8 py-6 bg-black text-white hover:bg-blue-600 transition-colors duration-300 shadow-lg border-2 border-transparent hover:border-yellow-400">
            <Link href="/quiz">Start Your Style Quiz</Link>
          </Button>
        </motion.div>
        <Button 
          variant="outline" 
          size="lg" 
          className="text-lg px-8 py-6 bg-white/20 backdrop-blur-sm border-white text-white hover:bg-white hover:text-black hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-xl z-0"
        >
          Learn More
        </Button>
      </div>
      <div className="mt-8 text-lg md:text-xl font-medium opacity-95 text-shadow">
        ✨ No subscription required • 📦 Free shipping & returns • 👗 1,000s of brands
      </div>
    </motion.div>
  )
}