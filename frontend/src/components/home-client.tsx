"use client"

import { useEffect, useState } from "react"
import dynamic from "next/dynamic"

import { ChatPanel } from "@/components/chat-panel"
import { PlacesPanel } from "@/components/places-panel"
import type { Place, OptimizeResult, PlacesData } from "@/lib/types"
import OptionsDock from "@/components/options-dock"
import OptimizationResult from "@/components/optimization-result"
import * as api from "@/utils/api"

const MapView = dynamic(() => import("@/components/map-view").then((mod) => mod.MapView), { ssr: false })

export default function HomeClient() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [placesData, setPlacesData] = useState<PlacesData>({
    places: [],
    start: null,
    end: null,
  })
  const [result, setResult] = useState<OptimizeResult | null>(null)

  useEffect(() => {
    const saved = localStorage.getItem("sessionId")
    if (saved) setSessionId(saved)
  }, [])

  const handleSession = (id: string) => {
    setSessionId(id)
    localStorage.setItem("sessionId", id)
    console.log("[Session] Initialized:", id)
  }

  const replacePlacesData = (data: PlacesData) => {
    console.log("[Places] Replacing places data:", data)
    setPlacesData({
      places: data.places || [],
      start: data.start ?? null,
      end: data.end ?? null,
    })
  }

  const appendPlacesData = (newPlaces: Place[], start?: Place | null, end?: Place | null) => {
    setPlacesData(prev => {
      const deduped = (newPlaces || []).filter(np => {
        if (!np) return false
        return !prev.places.some(p =>
          p.latitude === np.latitude && p.longitude === np.longitude
        )
      })
      console.log("[Deduped] New places to append:", deduped)
      const updated = {
        places: [...(prev.places || []), ...deduped],
        start: start ?? prev.start ?? null,
        end: end ?? prev.end ?? null,
      }

      console.log("[Places] Appending places:", updated)
      return updated
    })
  }

  const handlePlacesUpdate = (data: (PlacesData & { replace?: boolean })) => {
    if (data.replace) {
      replacePlacesData({
        places: data.places || [],
        start: data.start ?? null,
        end: data.end ?? null,
      })
    } else {
      appendPlacesData(data.places || [], data.start ?? null, data.end ?? null)
    }
  }

  const handlePlacesUpdateForOptionsDock = (
    newPlaces: Place[],
    start?: Place | null,
    end?: Place | null,
    replace?: boolean
  ) => {
    handlePlacesUpdate({
      places: newPlaces,
      start: start ?? null,
      end: end ?? null,
      replace: replace || false,
    })
  }

  const handleIncomingPlaces = async (newPlaces: Place[], start?: Place, end?: Place) => {
    appendPlacesData(newPlaces || [], start ?? null, end ?? null)
  }

  const updateBackendPlaces = async (updatedPlaces: Place[]) => {
    if (!sessionId) return

    setPlacesData(prev => ({ ...prev, places: updatedPlaces }))
    console.log("[Backend] Updating places:", updatedPlaces)

    try {
      const currentStart = placesData.start ?? null
      const currentEnd = placesData.end ?? null

      const data = await api.confirmPlaces(sessionId, updatedPlaces, currentStart, currentEnd)
      console.log("[Backend] Confirmed places:", data)

      replacePlacesData({
        places: data.places || [],
        start: data.start ?? currentStart ?? null,
        end: data.end ?? currentEnd ?? null,
      })
    } catch (err: unknown) {
      if (err instanceof Error) console.error("[Backend Error] Failed to update places:", err.message)
  else console.error("[Backend Error] Failed to update places:", err)
    }
  }

  const setStartEndPoints = async (start: Place | null, end: Place | null) => {
    if (!sessionId) return

    try {
      const data = await api.setStartEnd(sessionId, start, end)
      console.log("[Backend] Set start/end:", data)

      setPlacesData(prev => ({
        places: data.places || prev.places || [],
        start: data.start ?? prev.start ?? null,
        end: data.end ?? prev.end ?? null,
      }))
    } catch (err: unknown) {
      console.error("[Backend Error] Failed to set start/end:", err)
    }
  }

  const resetStartEnd = async (resetStart: boolean, resetEnd: boolean) => {
    if (!sessionId) return

    try {
      const data = await api.resetStartEnd(sessionId, resetStart, resetEnd)
      console.log("[Backend] Reset start/end:", data)

      setPlacesData({
        places: data.places || [],
        start: data.start ?? null,
        end: data.end ?? null,
      })
    } catch (err:unknown) {
      console.error("[Backend Error] Failed to reset start/end:", err)
    }
  }

  const handleTogglePoint = async (place: Place, type: "start" | "end", checked: boolean) => {
    if (!sessionId) return
    console.log(`[Toggle] ${type} for ${place.name} → ${checked}`)

    try {
      if (checked) {
        const newStart: Place | null = type === "start" ? place : placesData.start ?? null
        const newEnd: Place | null = type === "end" ? place : placesData.end ?? null
        await setStartEndPoints(newStart, newEnd)
      } else {
        await resetStartEnd(type === "start", type === "end")
      }
    } catch (err:unknown) {
      console.error(`[Toggle Error] ${type}:`, err)
    }
  }

  const onOptimize = async (algo: "nn" | "nn2opt" | "ga", returnToStart: boolean) => {
    if (!sessionId || (placesData.places?.length ?? 0) < 2) return

    try {
      const data = await api.optimizeRoute(sessionId, algo, returnToStart)
      console.log("[Optimization] Result:", data)

      setResult({
        orderedPlaces: data.optimized_places || [],
        stats: {
          distanceKm: data.total_distance ? data.total_distance / 1000 : undefined,
          durationMin: data.total_time ? data.total_time / 60 : undefined,
          stops: data.optimized_places?.length || 0,
        },
        start: data.start ?? null,
        end: data.end ?? null,
      })
    } catch (err:unknown ) {
      console.error("[Optimization Error]:", err)
  if (err instanceof Error) alert(`Optimization failed: ${err.message}`)
  else alert("Optimization failed: unknown error")
}
  }

  const handleClearResult = () => {
    if (!result) return
    if (!confirm("This will replace your places with the optimized route. Continue?")) return

    replacePlacesData({
      places: result.orderedPlaces || [],
      start: result.start ?? null,
      end: result.end ?? null,
    })
    setResult(null)
  }

  const allPlacesForDisplay = [
    ...(placesData.start ? [placesData.start] : []),
    ...(placesData.places || []),
    ...(placesData.end && placesData.end !== placesData.start ? [placesData.end] : []),
  ]

  return (
    <div className="h-full w-full bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <OptimizationResult result={result} onClose={() => setResult(null)} />

      <div className="grid h-full w-full grid-cols-1 lg:grid-cols-2">
        <section className="h-full min-h-0 p-3">
          <ChatPanel
            sessionId={sessionId}
            onSessionId={handleSession}
            onIncomingPlaces={handleIncomingPlaces}
            className="h-full"
          />
        </section>

        <section className="h-full min-h-0 p-3">
          <div className="grid h-full min-h-0 grid-rows-2 gap-3">
            <div className="min-h-0">
              <PlacesPanel
                sessionId={sessionId ?? ""}
                places={placesData.places || []}
                start={placesData.start ?? null}
                end={placesData.end ?? null}
                setPlaces={(newPlaces) =>
                  setPlacesData((prev) => ({ ...prev, places: newPlaces || [] }))
                }
                onUpdate={updateBackendPlaces}
                onSetStartEnd={setStartEndPoints}
                onTogglePoint={handleTogglePoint}
              />
            </div>

            <div className="grid min-h-0 grid-cols-2 gap-3">
              <div className="min-h-0">
                <OptionsDock
                  sessionId={sessionId}
                  places={placesData.places || []}
                  start={placesData.start ?? null}
                  end={placesData.end ?? null}
                  onPlacesUpdate={handlePlacesUpdateForOptionsDock}
                  onOptimize={onOptimize}
                  onClearResult={handleClearResult}
                  resetStartEnd={resetStartEnd}
                />
              </div>

              <div className="min-h-0 relative rounded-lg border bg-white dark:bg-gray-800">
                <MapView allPlaces={allPlacesForDisplay} />
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}