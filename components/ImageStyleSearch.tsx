'use client'

import { ChangeEvent, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { ImageUp, Loader2, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  convertRecommendationToProduct,
  getRecommendationsFromUploadedImage,
} from '@/lib/fashion-api'
import { useRecommendationStore } from '@/lib/store'

const MAX_IMAGE_BYTES = 5 * 1024 * 1024
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp']

interface ImageStyleSearchProps {
  userId: string
}

export function ImageStyleSearch({ userId }: ImageStyleSearchProps) {
  const router = useRouter()
  const { setRecommendations, setLoading, setError: setRecommendationError } =
    useRecommendationStore()
  const [file, setFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isSearching, setIsSearching] = useState(false)

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
    }
  }, [previewUrl])

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selected = event.target.files?.[0]
    setError(null)

    if (!selected) return
    if (!ALLOWED_TYPES.includes(selected.type)) {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
      setFile(null)
      setPreviewUrl(null)
      setError('Choose a JPEG, PNG, or WebP image.')
      event.target.value = ''
      return
    }
    if (selected.size > MAX_IMAGE_BYTES) {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
      setFile(null)
      setPreviewUrl(null)
      setError('Choose an image that is 5 MB or smaller.')
      event.target.value = ''
      return
    }

    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setFile(selected)
    setPreviewUrl(URL.createObjectURL(selected))
  }

  const handleSearch = async () => {
    if (!file) return

    setIsSearching(true)
    setLoading(true)
    setError(null)
    setRecommendationError(null)
    try {
      const results = await getRecommendationsFromUploadedImage(userId, file, 0.6, 10)
      setRecommendations(results.map(convertRecommendationToProduct))
      router.push('/recommendations')
    } catch (searchError) {
      const message = searchError instanceof Error ? searchError.message : 'Image search failed.'
      setError(message)
      setRecommendationError(null)
    } finally {
      setIsSearching(false)
      setLoading(false)
    }
  }

  return (
    <Card className="border-0 shadow-lg">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ImageUp className="h-5 w-5 text-purple-600" />
          Find a similar style from a photo
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-gray-600">
          Upload a fashion photo. CLIP compares its visual embedding with the catalog and
          blends the ranking with your feedback profile.
        </p>
        <label className="flex cursor-pointer items-center justify-center rounded-lg border-2 border-dashed border-purple-200 bg-purple-50 p-4 text-sm font-medium text-purple-700 hover:bg-purple-100">
          <input
            className="sr-only"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleFileChange}
          />
          {file ? file.name : 'Choose a JPEG, PNG, or WebP (max 5 MB)'}
        </label>
        {previewUrl && (
          // A local object URL is required here; Next Image cannot optimize browser-only blobs.
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={previewUrl}
            alt="Selected style"
            className="mx-auto max-h-64 rounded-lg object-contain"
          />
        )}
        {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
        <Button className="w-full gap-2" onClick={handleSearch} disabled={!file || isSearching}>
          {isSearching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
          {isSearching ? 'Finding similar styles…' : 'Search by photo'}
        </Button>
      </CardContent>
    </Card>
  )
}
