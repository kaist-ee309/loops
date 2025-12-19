"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronDown } from "lucide-react"
import { FONT_LICENSES } from "@/lib/data/legal-data"

export default function FontsPage() {
  const router = useRouter()
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id)
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-4 flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ChevronLeft className="w-5 h-5 text-gray-700" />
        </Button>
        <h1 className="text-lg font-medium text-gray-900">글꼴 저작권</h1>
      </div>

      {/* Content */}
      <div className="p-4">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">글꼴 저작권</h2>

        <div className="border-t-2 border-violet-500">
          {FONT_LICENSES.map((font) => (
            <div key={font.id} className="border-b border-gray-200">
              <button
                onClick={() => toggleExpand(font.id)}
                className="w-full flex items-center justify-between py-4 hover:bg-gray-50 transition-colors"
              >
                <span className="text-base text-gray-700">• {font.name}</span>
                <ChevronDown
                  className={`w-5 h-5 text-gray-400 transition-transform ${expandedId === font.id ? "rotate-180" : ""}`}
                />
              </button>

              {expandedId === font.id && (
                <div className="pb-4 px-4 text-sm text-gray-600 space-y-2">
                  <p>
                    <span className="font-medium">라이선스:</span> {font.license}
                  </p>
                  <p>
                    <span className="font-medium">저작권:</span> {font.copyright}
                  </p>
                  {font.url && (
                    <p>
                      <span className="font-medium">URL:</span>{" "}
                      <a
                        href={font.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-violet-600 hover:underline"
                      >
                        {font.url}
                      </a>
                    </p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
