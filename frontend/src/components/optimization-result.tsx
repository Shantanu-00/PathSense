"use client"

import { useState } from "react"
import type { OptimizeResult, Place } from "@/lib/types"

export default function OptimizationResult({
  result,
  onClose,
}: {
  result: OptimizeResult | null
  onClose: () => void
}) {
  const [position, setPosition] = useState({ x: 100, y: 100 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })

  if (!result) return null

  const steps = Array.isArray(result?.orderedPlaces) ? result.orderedPlaces : []
  const stats = result?.stats

  // Filter out duplicates - only show unique places in the ordered list
  const uniqueSteps = steps.filter((step, index, array) => 
    array.findIndex(s => s.id === step.id) === index
  )

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true)
    setDragStart({
      x: e.clientX - position.x,
      y: e.clientY - position.y
    })
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return
    setPosition({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y
    })
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  return (
    <div 
      className="fixed z-50 bg-white dark:bg-gray-800 shadow-2xl rounded-lg border border-gray-200 dark:border-gray-700"
      style={{
        left: position.x,
        top: position.y,
        width: '500px',
        height: '600px',
        cursor: isDragging ? 'grabbing' : 'grab'
      }}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      <div className="flex flex-col h-full">
        {/* Header with drag handle */}
        <div 
          className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 rounded-t-lg"
          onMouseDown={handleMouseDown}
        >
          <h4 className="font-semibold text-lg">Optimized Route Result</h4>
          <button 
            onClick={onClose} 
            className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 text-2xl"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-6 space-y-6">
          {/* Statistics */}
          {stats && (
            <div className="grid grid-cols-3 gap-4 text-center">
              {typeof stats.distanceKm === "number" && (
                <div className="rounded-lg bg-blue-50 dark:bg-blue-900/20 p-4">
                  <div className="text-sm text-blue-600 dark:text-blue-400 font-medium">Distance</div>
                  <div className="text-2xl font-bold text-blue-700 dark:text-blue-300">{stats.distanceKm.toFixed(1)} km</div>
                </div>
              )}
              {typeof stats.durationMin === "number" && (
                <div className="rounded-lg bg-green-50 dark:bg-green-900/20 p-4">
                  <div className="text-sm text-green-600 dark:text-green-400 font-medium">Duration</div>
                  <div className="text-2xl font-bold text-green-700 dark:text-green-300">{Math.round(stats.durationMin)} min</div>
                </div>
              )}
              <div className="rounded-lg bg-purple-50 dark:bg-purple-900/20 p-4">
                <div className="text-sm text-purple-600 dark:text-purple-400 font-medium">Stops</div>
                <div className="text-2xl font-bold text-purple-700 dark:text-purple-300">{uniqueSteps.length}</div>
              </div>
            </div>
          )}

          {/* Route Visualization */}
          <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
            <h5 className="font-semibold mb-3 text-gray-900 dark:text-gray-100">Route Visualization</h5>
            <div className="space-y-2">
              {uniqueSteps.map((step: Place, index: number) => (
                <div key={index} className="flex items-center gap-3 p-2 bg-white dark:bg-gray-800 rounded">
                  <div className="w-6 h-6 rounded-full bg-blue-500 text-white text-xs flex items-center justify-center font-bold">
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {step.name ?? step.address ?? `Stop ${index + 1}`}
                    </div>
                    {step.address && (
                      <div className="text-xs text-gray-500 dark:text-gray-400">{step.address}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Detailed Information */}
          <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
            <h5 className="font-semibold mb-3 text-gray-900 dark:text-gray-100">Route Details</h5>
            <div className="grid grid-cols-1 gap-3 text-sm">
              <div>
                <span className="text-gray-600 dark:text-gray-400">Start Point:</span>
                <span className="ml-2 font-medium">{result.start?.name || uniqueSteps[0]?.name || "Not specified"}</span>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400">End Point:</span>
                <span className="ml-2 font-medium">{result.end?.name || uniqueSteps[uniqueSteps.length - 1]?.name || "Not specified"}</span>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400">Total Distance:</span>
                <span className="ml-2 font-medium">{stats?.distanceKm?.toFixed(1) || "N/A"} km</span>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400">Estimated Time:</span>
                <span className="ml-2 font-medium">{stats?.durationMin ? Math.round(stats.durationMin) + " min" : "N/A"}</span>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400">Total Stops:</span>
                <span className="ml-2 font-medium">{uniqueSteps.length}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer with actions */}
        <div className="border-t border-gray-200 dark:border-gray-700 px-6 py-4 bg-gray-50 dark:bg-gray-900 rounded-b-lg">
          <div className="flex items-center justify-end gap-3">
            <button
              onClick={() => {
                const text = uniqueSteps.map((s: Place, i: number) => `${i + 1}. ${s.name ?? s.address ?? "Stop"}`).join("\n")
                navigator.clipboard?.writeText(text)
              }}
              className="px-4 py-2 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            >
              Copy Route
            </button>
            <button
              onClick={() => window.print()}
              className="px-4 py-2 text-sm bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
            >
              Print
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}