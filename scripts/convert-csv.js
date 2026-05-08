// CSV to TypeScript converter for catalog data
import fs from 'fs';
import path from 'path';

const csvFilePath = '../fashion-reco/catalog.csv';

function convertCsvToTypescript() {
  const csvContent = fs.readFileSync(csvFilePath, 'utf-8');
  const lines = csvContent.trim().split('\n');
  const headers = lines[0].split(',');
  
  const products = [];
  
  for (let i = 1; i < lines.length; i++) {
    const values = [];
    let currentValue = '';
    let insideQuotes = false;
    
    // Parse CSV line considering quoted fields
    for (let j = 0; j < lines[i].length; j++) {
      const char = lines[i][j];
      
      if (char === '"') {
        insideQuotes = !insideQuotes;
      } else if (char === ',' && !insideQuotes) {
        values.push(currentValue.trim());
        currentValue = '';
      } else {
        currentValue += char;
      }
    }
    values.push(currentValue.trim()); // Add the last value
    
    if (values.length >= headers.length) {
      const product = {
        id: values[0],
        title: values[1].replace(/"/g, ''),
        category: values[2],
        price: parseFloat(values[3]) || 0,
        brand: values[4],
        pattern: values[5],
        sizes: values[6] ? values[6].replace(/"/g, '').split(', ').filter(s => s.length > 0) : [],
        tags: values[7] ? values[7].replace(/"/g, '').split(',').map(t => t.trim()).filter(t => t.length > 0) : [],
        imageUrl: values[8] || '',
        // Additional fields required by the Product interface
        fit: 'regular',
        colors: [],
        gender: 'unisex'
      };
      
      products.push(product);
    }
  }
  
  console.log(`Converted ${products.length} products from CSV`);
  return products;
}

// Generate TypeScript catalog file
const products = convertCsvToTypescript();

const tsContent = `import { Product } from './validators'

// Quiz Question Types
export interface QuizQuestion {
  id: string
  step: number
  type: 'single' | 'multi' | 'scale' | 'size'
  required: boolean
  label: string
  options?: string[]
  min?: number
  max?: number
  stepSize?: number
  sizeTypes?: string[]
  imageChoices?: boolean
}

// Catalog data loaded from CSV
export const catalogData: Product[] = ${JSON.stringify(products, null, 2)}

export const quizQuestions = [
  {
    id: "categories",
    step: 1,
    type: "multi" as const,
    required: true,
    label: "What types of clothing are you looking for?",
    options: ["shirt", "pants", "shoes", "dress", "jacket", "sweater", "shorts", "skirt", "blouse", "jeans"]
  },
  {
    id: "colors",
    step: 2,
    type: "multi" as const,
    required: true,
    label: "What colors do you prefer?",
    options: ["black", "white", "navy", "grey", "beige", "pink", "red", "green", "blue", "purple", "brown"]
  },
  {
    id: "brands",
    step: 3,
    type: "multi" as const,
    required: true,
    label: "Which brands do you like?",
    options: ["zara", "h&m", "nike", "adidas", "uniqlo", "mango", "cos", "everlane", "reformation", "ganni"]
  },
  {
    id: "styles",
    step: 4,
    type: "multi" as const,
    required: true,
    label: "Which styles appeal to you?",
    options: ["casual", "formal", "sporty", "trendy", "classic", "minimalist", "bohemian", "edgy", "romantic"],
    imageChoices: true
  },
  {
    id: "size",
    step: 5,
    type: "single" as const,
    required: true,
    label: "What's your size?",
    options: ["XS", "S", "M", "L", "XL", "XXL"]
  },
  {
    id: "budget",
    step: 6,
    type: "scale" as const,
    required: true,
    label: "What's your maximum budget per item?",
    min: 20,
    max: 200,
    stepSize: 10
  }
]
`;

fs.writeFileSync('../lib/catalog.ts', tsContent);
console.log('✅ Generated new catalog.ts with CSV data!');