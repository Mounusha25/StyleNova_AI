'use client'

import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { Star, Info, ShoppingBag, WandSparkles, Loader2 } from 'lucide-react'
import { Product } from '@/lib/validators'
import { ScoredProduct } from '@/lib/scoring'
import { useState } from 'react'
import { getOutfit, OutfitResponse } from '@/lib/fashion-api'

interface ProductCardProps {
  product: Product | ScoredProduct
}

export function ProductCard({ product }: ProductCardProps) {
  const [imageError, setImageError] = useState(false)
  const isScored = 'score' in product && 'reason' in product

  return (
    <Card className="h-full border-0 shadow-2xl overflow-hidden bg-white">
      <div className="relative">
        {/* Product Image */}
        <div className="aspect-[3/4] overflow-hidden bg-gray-100">
          {!imageError ? (
            <img
              src={product.imageUrl}
              alt={product.title}
              className="w-full h-full object-cover"
              onError={() => setImageError(true)}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200">
              <ShoppingBag className="w-16 h-16 text-gray-400" />
            </div>
          )}
        </div>

        {/* Score Badge (if available) */}
        {isScored && (
          <div className="absolute top-4 left-4">
            <Badge className="bg-purple-500 text-white">
              {Math.round(product.score)}% match
            </Badge>
          </div>
        )}

        {/* More Info Button */}
        <div className="absolute top-4 right-4">
          <Sheet>
            <SheetTrigger asChild>
              <Button size="sm" variant="secondary" className="rounded-full w-8 h-8 p-0">
                <Info className="w-4 h-4" />
              </Button>
            </SheetTrigger>
            <SheetContent>
              <SheetHeader>
                <SheetTitle>{product.title}</SheetTitle>
              </SheetHeader>
              <ProductDetails product={product} />
            </SheetContent>
          </Sheet>
        </div>
      </div>

      <CardContent className="p-6">
        <div className="space-y-3">
          {/* Brand */}
          <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">
            {product.brand}
          </p>

          {/* Title */}
          <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
            {product.title}
          </h3>

          {/* Price */}
          <p className="text-2xl font-bold text-gray-900">
            ${product.price}
          </p>

          {/* Tags */}
          <div className="flex flex-wrap gap-1">
            {product.tags.slice(0, 3).map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
            {product.tags.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{product.tags.length - 3}
              </Badge>
            )}
          </div>

          {/* Fit */}
          <p className="text-sm text-gray-600">
            <span className="font-medium">Fit:</span> {product.fit}
          </p>

          {/* Colors */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-600">Colors:</span>
            <div className="flex gap-1">
              {product.colors.slice(0, 4).map((color) => (
                <div
                  key={color}
                  className="w-4 h-4 rounded-full border border-gray-300"
                  style={{ backgroundColor: getColorHex(color) }}
                  title={color}
                />
              ))}
              {product.colors.length > 4 && (
                <span className="text-xs text-gray-500">
                  +{product.colors.length - 4}
                </span>
              )}
            </div>
          </div>

          {/* Match Reasons (if available) */}
          {isScored && product.reason.length > 0 && (
            <div className="pt-2 border-t">
              <p className="text-xs font-medium text-purple-600 mb-1">
                Why we picked this:
              </p>
              <p className="text-xs text-gray-600 line-clamp-2">
                {product.reason[0]}
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

function ProductDetails({ product }: { product: Product | ScoredProduct }) {
  const isScored = 'score' in product && 'reason' in product
  const [outfit, setOutfit] = useState<OutfitResponse | null>(null)
  const [outfitError, setOutfitError] = useState<string | null>(null)
  const [isLoadingOutfit, setIsLoadingOutfit] = useState(false)

  const handleCompleteLook = async () => {
    setIsLoadingOutfit(true)
    setOutfitError(null)
    try {
      setOutfit(await getOutfit(product.id))
    } catch (error) {
      setOutfitError(error instanceof Error ? error.message : 'Could not build an outfit.')
    } finally {
      setIsLoadingOutfit(false)
    }
  }

  return (
    <div className="space-y-6 overflow-y-auto px-4 pb-6">
      {/* Product Image */}
      <div className="aspect-square overflow-hidden rounded-lg bg-gray-100">
        <img
          src={product.imageUrl}
          alt={product.title}
          className="w-full h-full object-cover"
          onError={(e) => {
            const target = e.target as HTMLImageElement
            target.style.display = 'none'
            target.nextElementSibling?.classList.remove('hidden')
          }}
        />
        <div className="hidden w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200">
          <ShoppingBag className="w-16 h-16 text-gray-400" />
        </div>
      </div>

      {/* Product Info */}
      <div className="space-y-4">
        <Button className="w-full gap-2" onClick={handleCompleteLook} disabled={isLoadingOutfit}>
          {isLoadingOutfit ? <Loader2 className="h-4 w-4 animate-spin" /> : <WandSparkles className="h-4 w-4" />}
          {isLoadingOutfit ? 'Building your outfit…' : 'Complete the look'}
        </Button>
        {outfitError && <p role="alert" className="text-sm text-red-600">{outfitError}</p>}
        {outfit && (
          <div className="space-y-3 rounded-lg bg-purple-50 p-3">
            <div className="flex items-center justify-between">
              <p className="font-semibold text-purple-900">Complete outfit</p>
              <Badge>{Math.round(outfit.outfit_score * 100)}% compatible</Badge>
            </div>
            {outfit.items.map((item) => (
              <div key={`${item.slot}-${item.product.id}`} className="flex gap-3 rounded-md bg-white p-2">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={item.product.image_url} alt="" className="h-16 w-12 rounded object-cover" />
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium uppercase text-purple-600">{item.slot}</p>
                  <p className="truncate text-sm font-medium">{item.product.title}</p>
                  <p className="text-xs text-gray-500">{item.product.brand} · ${item.product.price}</p>
                  <p className="mt-1 text-xs text-gray-500">{item.reasons[0]}</p>
                </div>
              </div>
            ))}
            <p className="text-right text-sm font-semibold">Total: ${outfit.total_price.toFixed(2)}</p>
          </div>
        )}
        <div>
          <h4 className="font-semibold text-gray-900 mb-1">Brand</h4>
          <p className="text-gray-600">{product.brand}</p>
        </div>

        <div>
          <h4 className="font-semibold text-gray-900 mb-1">Price</h4>
          <p className="text-xl font-bold text-gray-900">${product.price}</p>
        </div>

        <div>
          <h4 className="font-semibold text-gray-900 mb-1">Fit</h4>
          <p className="text-gray-600 capitalize">{product.fit}</p>
        </div>

        <div>
          <h4 className="font-semibold text-gray-900 mb-1">Available Colors</h4>
          <div className="flex flex-wrap gap-2">
            {product.colors.map((color) => (
              <Badge key={color} variant="outline" className="capitalize">
                {color}
              </Badge>
            ))}
          </div>
        </div>

        <div>
          <h4 className="font-semibold text-gray-900 mb-1">Available Sizes</h4>
          <div className="flex flex-wrap gap-2">
            {product.sizes.map((size) => (
              <Badge key={size} variant="outline">
                {size}
              </Badge>
            ))}
          </div>
        </div>

        <div>
          <h4 className="font-semibold text-gray-900 mb-1">Style Tags</h4>
          <div className="flex flex-wrap gap-2">
            {product.tags.map((tag) => (
              <Badge key={tag} variant="secondary" className="capitalize">
                {tag}
              </Badge>
            ))}
          </div>
        </div>

        {/* Match Details (if available) */}
        {isScored && (
          <>
            <div>
              <h4 className="font-semibold text-gray-900 mb-1">Match Score</h4>
              <div className="flex items-center gap-2">
                <div className="flex">
                  {Array.from({ length: 5 }, (_, i) => (
                    <Star
                      key={i}
                      className={`w-4 h-4 ${
                        i < Math.round(product.score / 20)
                          ? 'fill-yellow-400 text-yellow-400'
                          : 'text-gray-300'
                      }`}
                    />
                  ))}
                </div>
                <span className="text-sm text-gray-600">
                  {Math.round(product.score)}% match
                </span>
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-gray-900 mb-1">Why we picked this</h4>
              <ul className="space-y-1">
                {product.reason.map((reason, index) => (
                  <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                    <span className="text-green-500 mt-1">•</span>
                    {reason}
                  </li>
                ))}
              </ul>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function getColorHex(colorName: string): string {
  const colorMap: Record<string, string> = {
    black: '#000000',
    white: '#FFFFFF',
    navy: '#000080',
    grey: '#808080',
    gray: '#808080',
    beige: '#F5F5DC',
    cream: '#FFFDD0',
    pink: '#FFC0CB',
    red: '#FF0000',
    green: '#008000',
    blue: '#0000FF',
    purple: '#800080',
    yellow: '#FFFF00',
    orange: '#FFA500',
    brown: '#A52A2A',
    burgundy: '#800020',
    emerald: '#50C878',
    indigo: '#4B0082'
  }
  
  return colorMap[colorName.toLowerCase()] || '#808080'
}
