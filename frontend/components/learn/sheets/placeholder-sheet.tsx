"use client"

import { X, Construction } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet"

interface PlaceholderSheetProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
}

export function PlaceholderSheet({ open, onOpenChange, title }: PlaceholderSheetProps) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="bottom" className="h-[50vh] rounded-t-2xl">
        <SheetHeader className="flex flex-row items-center justify-between pb-4 border-b">
          <SheetTitle className="text-lg font-bold">{title}</SheetTitle>
          <Button variant="ghost" size="icon" onClick={() => onOpenChange(false)}>
            <X className="w-5 h-5" />
          </Button>
        </SheetHeader>

        <div className="flex flex-col items-center justify-center h-[calc(100%-60px)] text-gray-400">
          <Construction className="w-16 h-16 mb-4" />
          <p className="text-lg font-medium">준비 중</p>
          <p className="text-sm mt-1">곧 만나볼 수 있어요!</p>
        </div>
      </SheetContent>
    </Sheet>
  )
}
