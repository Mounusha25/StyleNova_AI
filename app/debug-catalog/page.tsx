'use client'

import { useEffect, useState } from 'react'
import { catalogData } from '@/lib/catalog'
import { useRecommendationStore } from '@/lib/store'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function CatalogDebugPage() {
  const [debugInfo, setDebugInfo] = useState<any>(null)
  const { reset, setRecommendations } = useRecommendationStore()
  
  useEffect(() => {
    // Force fresh catalog data
    const info = {
      totalProducts: catalogData.length,
      firstProduct: catalogData[0],
      sampleIds: catalogData.slice(0, 10).map(p => p.id),
      brands: [...new Set(catalogData.map(p => p.brand))].slice(0, 10),
      priceRange: {
        min: Math.min(...catalogData.map(p => p.price)),
        max: Math.max(...catalogData.map(p => p.price))
      }
    }
    setDebugInfo(info)
    console.log('🔍 Fresh Catalog Debug:', info)
  }, [])
  
  const forceClearAndReload = () => {
    // Clear all storage
    localStorage.clear()
    
    // Reset store
    reset()
    
    // Force reload
    window.location.href = '/quiz'
  }
  
  if (!debugInfo) return <div>Loading...</div>
  
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Catalog Debug Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <strong>Total Products:</strong> {debugInfo.totalProducts}
              </div>
              
              <div>
                <strong>First Product:</strong>
                <pre className="bg-gray-100 p-2 rounded mt-2 text-sm overflow-x-auto">
                  {JSON.stringify(debugInfo.firstProduct, null, 2)}
                </pre>
              </div>
              
              <div>
                <strong>Sample Product IDs:</strong>
                <div className="flex flex-wrap gap-2 mt-2">
                  {debugInfo.sampleIds.map((id: string) => (
                    <span key={id} className="bg-blue-100 px-2 py-1 rounded text-sm">
                      {id}
                    </span>
                  ))}
                </div>
              </div>
              
              <div>
                <strong>Brands Available:</strong>
                <div className="flex flex-wrap gap-2 mt-2">
                  {debugInfo.brands.map((brand: string) => (
                    <span key={brand} className="bg-green-100 px-2 py-1 rounded text-sm">
                      {brand}
                    </span>
                  ))}
                </div>
              </div>
              
              <div>
                <strong>Price Range:</strong> ${debugInfo.priceRange.min} - ${debugInfo.priceRange.max}
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button 
              onClick={forceClearAndReload}
              className="w-full"
              size="lg"
            >
              🔄 Force Clear Everything & Start Fresh
            </Button>
            
            <Button 
              variant="outline"
              onClick={() => window.location.href = '/quiz'}
              className="w-full"
            >
              🎯 Go to Quiz (New Session)
            </Button>
            
            <Button 
              variant="outline"
              onClick={() => {
                console.log('Full catalog data:', catalogData)
                alert(`Check console for full catalog data (${catalogData.length} products)`)
              }}
              className="w-full"
            >
              📊 Log Full Catalog to Console
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}