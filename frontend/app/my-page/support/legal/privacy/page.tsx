"use client"

import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ChevronLeft } from "lucide-react"
import { PRIVACY_POLICY } from "@/lib/data/legal-data"

export default function PrivacyPage() {
  const router = useRouter()

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-4 flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ChevronLeft className="w-5 h-5 text-gray-700" />
        </Button>
        <h1 className="text-lg font-medium text-gray-900">개인 정보 처리 방침</h1>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Sections */}
        <div className="space-y-8">
          {PRIVACY_POLICY.map((section, sectionIndex) => (
            <div key={section.id}>
              <h3 className={`font-bold text-gray-900 mb-3 ${sectionIndex === 0 ? "text-2xl" : "text-lg"}`}>
                {section.title}
              </h3>
              <p className="text-gray-700 leading-relaxed mb-3">{section.content}</p>

              {section.items && (
                <ol className="list-decimal list-inside space-y-2 text-gray-700 pl-2 mb-4">
                  {section.items.map((item, index) => (
                    <li key={index} className="leading-relaxed">
                      {item}
                    </li>
                  ))}
                </ol>
              )}

              {section.table && (
                <div className="overflow-x-auto mt-4">
                  <table className="w-full border-collapse border border-gray-300 text-sm">
                    <thead>
                      <tr className="bg-gray-50">
                        {section.table.headers.map((header, index) => (
                          <th
                            key={index}
                            className="border border-gray-300 px-3 py-2 text-center font-medium text-gray-900"
                          >
                            {header}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {section.table.rows.map((row, rowIndex) => (
                        <tr key={rowIndex}>
                          {row.map((cell, cellIndex) => (
                            <td key={cellIndex} className="border border-gray-300 px-3 py-2 text-gray-700">
                              {cell}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
