"use client"

import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ChevronLeft } from "lucide-react"
import { TERMS_OF_SERVICE } from "@/lib/data/legal-data"

export default function TermsPage() {
  const router = useRouter()

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-4 flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ChevronLeft className="w-5 h-5 text-gray-700" />
        </Button>
        <h1 className="text-lg font-medium text-gray-900">이용 약관</h1>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Title */}
        <h2 className="text-2xl font-bold text-gray-900 mb-6">이용 약관</h2>

        {/* Articles */}
        <div className="space-y-8">
          {TERMS_OF_SERVICE.map((article) => (
            <div key={article.id}>
              <h3 className="text-lg font-bold text-gray-900 mb-3">{article.title}</h3>
              <p className="text-gray-700 leading-relaxed mb-3">{article.content}</p>
              {article.items && (
                <ol className="list-decimal list-inside space-y-2 text-gray-700 pl-2">
                  {article.items.map((item, index) => (
                    <li key={index} className="leading-relaxed">
                      {item}
                    </li>
                  ))}
                </ol>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
