// Test script to verify new catalog is working
import { catalogData } from '../lib/catalog.js';

console.log('🧪 Testing New Catalog Data...\n');

console.log(`📊 Catalog Statistics:`);
console.log(`   - Total products: ${catalogData.length}`);
console.log(`   - Unique brands: ${[...new Set(catalogData.map(p => p.brand))].length}`);
console.log(`   - Price range: $${Math.min(...catalogData.map(p => p.price))} - $${Math.max(...catalogData.map(p => p.price))}`);

console.log(`\n🛍️ Sample Products:`);
catalogData.slice(0, 5).forEach((product, i) => {
  console.log(`   ${i + 1}. ${product.title} by ${product.brand} - $${product.price}`);
  console.log(`      ID: ${product.id}, Category: ${product.category}`);
});

console.log(`\n🔍 Product ID Check:`);
console.log(`   - First 10 IDs: ${catalogData.slice(0, 10).map(p => p.id).join(', ')}`);

console.log(`\n✅ Catalog verification complete!`);