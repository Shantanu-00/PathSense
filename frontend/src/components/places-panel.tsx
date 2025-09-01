"use client"

import React, { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import type { Place } from "@/lib/types"

interface PlacesPanelProps {
  sessionId: string
  places: Place[]
  start: Place | null
  end: Place | null
  setPlaces: (places: Place[]) => void
  onUpdate: (places: Place[]) => void
  onSetStartEnd: (start: Place | null, end: Place | null) => void
  onTogglePoint: (place: Place, type: "start" | "end", checked: boolean) => void
}

export function PlacesPanel({
  sessionId,
  places,
  start,
  end,
  setPlaces,
  onUpdate,
  onSetStartEnd,
  onTogglePoint,
}: PlacesPanelProps) {
  const [dragIndex, setDragIndex] = useState<number | null>(null)

  useEffect(() => {
    console.log("[PlacesPanel] Start:", start?.name, "End:", end?.name)
  }, [start, end])

  function onDragStart(e: React.DragEvent<HTMLLIElement>, index: number) {
    setDragIndex(index)
    e.dataTransfer.effectAllowed = "move"
  }

  function onDragOver(e: React.DragEvent<HTMLLIElement>) {
    e.preventDefault()
    e.dataTransfer.dropEffect = "move"
  }

  function onDrop(e: React.DragEvent<HTMLLIElement>, index: number) {
    e.preventDefault()
    if (dragIndex === null || dragIndex === index) return
    const next = [...places]
    const [moved] = next.splice(dragIndex, 1)
    next.splice(index, 0, moved)
    setPlaces(next)
    onUpdate(next)
    setDragIndex(null)
  }

  const isStart = (p: Place):boolean => start?.id === p.id
  const isEnd = (p: Place):boolean => end?.id === p.id
useEffect(() => {
  console.log("[PlacesPanel] Rendering places:", places)
}, [places])
  return (
    <Card className="flex h-full min-h-0 flex-col">
      <CardHeader className="pb-2">
        <CardTitle className="text-base">Places (drag to reorder)</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 min-h-0 overflow-hidden">
        <div className="h-full overflow-auto rounded-md border">
          <ul className="overflow-auto">
            {places.length === 0 && (
              <li className="px-3 py-6 text-center text-sm text-gray-500 dark:text-gray-400">
                No places yet. Ask the assistant or use options below.
              </li>
            )}

            {places.map((p: Place, idx: number) => (
              <li
                key={`${p.id}-${idx}-${p.latitude}-${p.longitude}`}
                draggable
                onDragStart={(e) => onDragStart(e, idx)}
                onDragOver={onDragOver}
                onDrop={(e) => onDrop(e, idx)}
                className="relative flex items-center gap-3 border-b px-3 py-2 last:border-b-0 hover:bg-muted/50 group"
                aria-grabbed={dragIndex === idx}
              >
                {/* Visual indicators */}
                {isStart(p) && (
                  <div className="absolute left-0 top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-green-500" />
                )}
                {isEnd(p) && (
                  <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-red-500" />
                )}

                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-gray-900 dark:text-gray-100">
                    {p.name}{" "}
                    {p.type ? <span className="text-gray-500 dark:text-gray-400">({p.type})</span> : null}
                  </p>
                  <p className="truncate text-xs text-gray-500 dark:text-gray-400">
                    {p.address ?? "Address unknown"}
                  </p>
                </div>

                <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <div className="flex items-center gap-1">
                    <Switch
                      id={`start-${p.id}`}
                      checked={isStart(p)}
                      onCheckedChange={(checked) => onTogglePoint(p, "start", checked)}
                    />
                    <Label htmlFor={`start-${p.id}`} className="text-xs">
                      Start
                    </Label>
                  </div>

                  <div className="flex items-center gap-1">
                    <Switch
                      id={`end-${p.id}`}
                      checked={isEnd(p)}
                      onCheckedChange={(checked) => onTogglePoint(p, "end", checked)}
                    />
                    <Label htmlFor={`end-${p.id}`} className="text-xs">
                      End
                    </Label>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  )
}