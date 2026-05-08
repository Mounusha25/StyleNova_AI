import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

const sampleProducts = [
  {
    id: "prod_1",
    brand: "Everlane",
    title: "The Relaxed Blazer",
    price: 198,
    tags: ["blazer", "work", "smart-casual", "versatile"],
    fit: "relaxed",
    colors: ["black", "navy", "beige"],
    gender: "women",
    sizes: ["XS", "S", "M", "L", "XL"],
    imageUrl: "/images/relaxed-blazer.jpg"
  },
  {
    id: "prod_2",
    brand: "Madewell",
    title: "High-Rise Skinny Jeans",
    price: 128,
    tags: ["jeans", "casual", "high-rise", "skinny"],
    fit: "skinny",
    colors: ["indigo", "black", "white"],
    gender: "women",
    sizes: ["24", "25", "26", "27", "28", "29", "30"],
    imageUrl: "/images/high-rise-jeans.jpg"
  },
  {
    id: "prod_3",
    brand: "COS",
    title: "Oversized Wool Sweater",
    price: 89,
    tags: ["sweater", "cozy", "oversized", "minimalist"],
    fit: "oversized",
    colors: ["cream", "grey", "black"],
    gender: "women",
    sizes: ["XS", "S", "M", "L"],
    imageUrl: "/images/wool-sweater.jpg"
  },
  {
    id: "prod_4",
    brand: "Reformation",
    title: "Midi Slip Dress",
    price: 168,
    tags: ["dress", "party", "midi", "feminine"],
    fit: "fitted",
    colors: ["black", "burgundy", "emerald"],
    gender: "women",
    sizes: ["0", "2", "4", "6", "8", "10"],
    imageUrl: "/images/midi-dress.jpg"
  },
  {
    id: "prod_5",
    brand: "Allbirds",
    title: "Tree Runners",
    price: 98,
    tags: ["sneakers", "sustainable", "comfortable", "casual"],
    fit: "true-to-size",
    colors: ["white", "grey", "navy"],
    gender: "unisex",
    sizes: ["6", "7", "8", "9", "10", "11"],
    imageUrl: "/images/tree-runners.jpg"
  },
  {
    id: "prod_6",
    brand: "Uniqlo",
    title: "Cashmere Crew Neck Sweater",
    price: 59,
    tags: ["sweater", "cashmere", "basic", "versatile"],
    fit: "regular",
    colors: ["beige", "grey", "navy", "pink"],
    gender: "women",
    sizes: ["XS", "S", "M", "L", "XL"],
    imageUrl: "/images/cashmere-sweater.jpg"
  },
  // Add more products to reach 60-100 items...
]

const sampleQuestions = [
  {
    id: "q1",
    step: 1,
    type: "single",
    required: true,
    label: "What's your gender?",
    options: ["Women", "Men", "Non-binary", "Prefer not to say"]
  },
  {
    id: "q2",
    step: 1,
    type: "single", 
    required: true,
    label: "What's your age range?",
    options: ["18-24", "25-34", "35-44", "45-54", "55+"]
  },
  {
    id: "q3",
    step: 1,
    type: "size",
    required: true,
    label: "What are your sizes?",
    sizeTypes: ["top", "bottom", "shoe"]
  },
  {
    id: "q4",
    step: 2,
    type: "scale",
    required: true,
    label: "How much do you typically spend on a top?",
    min: 20,
    max: 200,
    stepSize: 10
  },
  {
    id: "q5",
    step: 2,
    type: "scale",
    required: true,
    label: "How much do you typically spend on bottoms?",
    min: 30,
    max: 300,
    stepSize: 10
  },
  {
    id: "q6",
    step: 3,
    type: "multi",
    required: true,
    label: "What occasions do you dress for most?",
    options: ["Work/Professional", "Casual/Weekend", "Date Night", "Social Events", "Travel", "Exercise/Athletic"]
  },
  {
    id: "q7",
    step: 3,
    type: "multi",
    required: true,
    label: "Which styles appeal to you?",
    options: ["Classic", "Trendy", "Bohemian", "Minimalist", "Edgy", "Romantic", "Sporty"],
    imageChoices: true
  },
  {
    id: "q8",
    step: 4,
    type: "multi",
    required: false,
    label: "What colors do you love?",
    options: ["Black", "White", "Navy", "Grey", "Beige", "Pink", "Red", "Green", "Blue", "Purple"]
  },
  {
    id: "q9",
    step: 4,
    type: "multi",
    required: false,
    label: "What colors do you avoid?",
    options: ["Brown", "Orange", "Yellow", "Bright Pink", "Neon Colors", "Pastels"]
  },
  {
    id: "q10",
    step: 5,
    type: "single",
    required: true,
    label: "What's your preferred jean fit?",
    options: ["Skinny", "Straight", "Bootcut", "Wide Leg", "Boyfriend", "High-Rise", "Low-Rise"]
  },
  {
    id: "q11",
    step: 5,
    type: "scale",
    required: true,
    label: "How adventurous are you with trends? (1 = stick to classics, 5 = love trying new trends)",
    min: 1,
    max: 5,
    stepSize: 1
  },
  {
    id: "q12",
    step: 6,
    type: "single",
    required: true,
    label: "What's your body type?",
    options: ["Petite", "Tall", "Curvy", "Athletic", "Plus Size", "Prefer not to say"]
  }
]

async function main() {
  console.log('Start seeding...')
  
  // Create a sample user
  const user = await prisma.user.create({
    data: {
      email: 'demo@clozyt.com',
    },
  })

  console.log('Created user:', user)

  // You can add sample quiz data here if needed
  console.log('Seeding finished.')
}

main()
  .then(async () => {
    await prisma.$disconnect()
  })
  .catch(async (e) => {
    console.error(e)
    await prisma.$disconnect()
    process.exit(1)
  })