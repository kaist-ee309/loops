"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { ChevronLeft, Plus, ChevronDown, ChevronUp, Clock, CheckCircle, AlertCircle, Loader2, X } from "lucide-react"
import {
  REPORT_CATEGORIES,
  SAMPLE_REPORTS,
  REPORT_STATUS_CONFIG,
  type ReportItem,
  type ReportStatus,
} from "@/lib/data/report-data"

const STATUS_ICONS: Record<ReportStatus, typeof Clock> = {
  pending: Clock,
  "in-progress": Loader2,
  resolved: CheckCircle,
  closed: AlertCircle,
}

export default function ReportPage() {
  const router = useRouter()
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [reports, setReports] = useState<ReportItem[]>([])
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [newReport, setNewReport] = useState({
    category: "bug",
    title: "",
    description: "",
  })
  const [showConfirm, setShowConfirm] = useState(false)

  useEffect(() => {
    const savedReports = localStorage.getItem("userReports")
    if (savedReports) {
      setReports([...JSON.parse(savedReports), ...SAMPLE_REPORTS])
    } else {
      setReports(SAMPLE_REPORTS)
    }

    // TODO: 백엔드 연동 시 아래 코드로 대체
    // const fetchReports = async () => {
    //   const response = await fetch('/api/reports')
    //   const data = await response.json()
    //   setReports(data)
    // }
    // fetchReports()
  }, [])

  const filteredReports = reports.filter((report) => {
    return selectedCategory === "all" || report.category === selectedCategory
  })

  const handleSubmitReport = () => {
    if (newReport.title.trim() === "" || newReport.description.trim() === "") return

    const report: ReportItem = {
      id: Date.now().toString(),
      category: newReport.category,
      title: newReport.title.trim(),
      description: newReport.description.trim(),
      status: "pending",
      createdAt: new Date().toISOString(),
    }

    const userReports = reports.filter((r) => !SAMPLE_REPORTS.find((s) => s.id === r.id))
    const updatedUserReports = [report, ...userReports]
    localStorage.setItem("userReports", JSON.stringify(updatedUserReports))

    setReports([report, ...reports])
    setNewReport({ category: "bug", title: "", description: "" })
    setShowForm(false)
    setShowConfirm(true)
    setTimeout(() => setShowConfirm(false), 3000)

    // TODO: 백엔드 연동 시 API 호출
    // await fetch('/api/reports', {
    //   method: 'POST',
    //   body: JSON.stringify(report)
    // })
  }

  const handleDeleteReport = (id: string) => {
    const updated = reports.filter((r) => r.id !== id)
    const userReports = updated.filter((r) => !SAMPLE_REPORTS.find((s) => s.id === r.id))
    localStorage.setItem("userReports", JSON.stringify(userReports))
    setReports(updated)

    // TODO: 백엔드 연동 시 API 호출
    // await fetch(`/api/reports/${id}`, { method: 'DELETE' })
  }

  const getStatusInfo = (status: ReportStatus) => {
    const config = REPORT_STATUS_CONFIG[status]
    return {
      ...config,
      icon: STATUS_ICONS[status],
    }
  }

  const pendingCount = reports.filter((r) => r.status === "pending").length
  const inProgressCount = reports.filter((r) => r.status === "in-progress").length
  const resolvedCount = reports.filter((r) => r.status === "resolved" || r.status === "closed").length

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ChevronLeft className="w-5 h-5 text-gray-700" />
          </Button>
          <h1 className="text-lg font-medium text-gray-900">문제 보고</h1>
        </div>
        <Button variant="ghost" size="icon" onClick={() => setShowForm(true)} className="text-violet-600">
          <Plus className="w-5 h-5" />
        </Button>
      </div>

      {/* Hero Section */}
      <div className="bg-gradient-to-b from-gray-50 to-white px-4 py-8 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">문제 보고</h2>
        <p className="text-gray-600 mb-4">버그나 개선사항을 알려주세요!</p>
        <Button onClick={() => setShowForm(true)} className="bg-violet-600 hover:bg-violet-700 text-white">
          <Plus className="w-4 h-4 mr-2" />
          문제 보고하기
        </Button>
      </div>

      {/* Confirm Toast */}
      {showConfirm && (
        <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50">
          문제가 성공적으로 접수되었습니다!
        </div>
      )}

      {/* New Report Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-end sm:items-center justify-center">
          <div className="bg-white w-full sm:w-[480px] sm:rounded-xl rounded-t-xl p-6 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-medium">새 문제 보고</h3>
              <Button variant="ghost" size="icon" onClick={() => setShowForm(false)}>
                <X className="w-5 h-5" />
              </Button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-700 mb-2 block">카테고리</label>
                <div className="flex flex-wrap gap-2">
                  {REPORT_CATEGORIES.filter((c) => c.id !== "all").map((cat) => (
                    <button
                      key={cat.id}
                      onClick={() => setNewReport({ ...newReport, category: cat.id })}
                      className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
                        newReport.category === cat.id
                          ? "bg-violet-600 text-white"
                          : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                      }`}
                    >
                      {cat.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm text-gray-700 mb-2 block">제목</label>
                <Input
                  placeholder="문제를 간단히 요약해주세요"
                  value={newReport.title}
                  onChange={(e) => setNewReport({ ...newReport, title: e.target.value })}
                />
              </div>

              <div>
                <label className="text-sm text-gray-700 mb-2 block">상세 설명</label>
                <Textarea
                  placeholder="문제 상황을 자세히 설명해주세요"
                  rows={5}
                  value={newReport.description}
                  onChange={(e) => setNewReport({ ...newReport, description: e.target.value })}
                />
              </div>

              <Button
                className="w-full bg-violet-600 hover:bg-violet-700 text-white"
                onClick={handleSubmitReport}
                disabled={newReport.title.trim() === "" || newReport.description.trim() === ""}
              >
                제출하기
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Status Summary */}
      <div className="px-4 py-3 flex justify-center gap-4 text-xs border-b border-gray-100">
        <span className="flex items-center gap-1 text-amber-600">
          <Clock className="w-3 h-3" /> 대기중 {pendingCount}
        </span>
        <span className="flex items-center gap-1 text-blue-600">
          <Loader2 className="w-3 h-3" /> 처리중 {inProgressCount}
        </span>
        <span className="flex items-center gap-1 text-green-600">
          <CheckCircle className="w-3 h-3" /> 완료 {resolvedCount}
        </span>
      </div>

      {/* Category Filter */}
      <div className="px-4 py-3 flex gap-2 overflow-x-auto scrollbar-hide">
        {REPORT_CATEGORIES.map((category) => (
          <button
            key={category.id}
            onClick={() => setSelectedCategory(category.id)}
            className={`px-4 py-2 rounded-full text-sm whitespace-nowrap transition-colors ${
              selectedCategory === category.id
                ? "bg-violet-600 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            {category.label}
          </button>
        ))}
      </div>

      {/* Reports List */}
      <div className="px-4 py-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-medium text-gray-900">내 문제 보고</h3>
          <p className="text-sm text-gray-500">{filteredReports.length}개</p>
        </div>

        {filteredReports.length === 0 ? (
          <div className="text-center py-12">
            <AlertCircle className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">등록된 문제 보고가 없습니다</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredReports.map((report) => {
              const statusInfo = getStatusInfo(report.status)
              const StatusIcon = statusInfo.icon
              const isExpanded = expandedId === report.id
              const canDelete = report.status === "pending" && !SAMPLE_REPORTS.find((s) => s.id === report.id)

              return (
                <div
                  key={report.id}
                  className={`border rounded-xl overflow-hidden ${statusInfo.borderColor} ${statusInfo.cardBg}`}
                >
                  <button
                    onClick={() => setExpandedId(isExpanded ? null : report.id)}
                    className="w-full flex items-start justify-between p-4 text-left"
                  >
                    <div className="flex-1 pr-4">
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <span className="text-xs text-gray-500">
                          {REPORT_CATEGORIES.find((c) => c.id === report.category)?.label}
                        </span>
                        <span
                          className={`flex items-center gap-1 text-xs ${statusInfo.textColor} ${statusInfo.bgColor} px-2 py-0.5 rounded-full`}
                        >
                          <StatusIcon className="w-3 h-3" /> {statusInfo.label}
                        </span>
                      </div>
                      <p className="text-sm font-medium text-gray-900">{report.title}</p>
                      <p className="text-xs text-gray-400 mt-1">
                        {new Date(report.createdAt).toLocaleDateString("ko-KR")}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      {canDelete && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDeleteReport(report.id)
                          }}
                          className="text-xs text-gray-400 hover:text-red-500"
                        >
                          삭제
                        </button>
                      )}
                      {isExpanded ? (
                        <ChevronUp className="w-5 h-5 text-gray-400 flex-shrink-0" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
                      )}
                    </div>
                  </button>

                  {isExpanded && (
                    <div className="px-4 pb-4 pt-0 space-y-3">
                      <div className="bg-white/80 p-3 rounded-lg">
                        <p className="text-xs text-gray-500 mb-1">상세 설명</p>
                        <p className="text-sm text-gray-700 leading-relaxed">{report.description}</p>
                      </div>

                      {report.response && (
                        <div className="bg-white border border-green-200 p-3 rounded-lg">
                          <p className="text-xs text-green-600 mb-1">
                            답변 ({report.updatedAt && new Date(report.updatedAt).toLocaleDateString("ko-KR")})
                          </p>
                          <p className="text-sm text-gray-700 leading-relaxed">{report.response}</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
