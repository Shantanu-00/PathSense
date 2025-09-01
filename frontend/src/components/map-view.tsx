"use client"

import { useEffect, useRef, useState } from "react"
import type { Place } from "@/lib/types"
import L from "leaflet"
import "leaflet/dist/leaflet.css"

const markerIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

export function MapView({ allPlaces }: { allPlaces: Place[] }) {  // CHANGED prop name
  const mapRef = useRef<L.Map | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const markersRef = useRef<L.Marker[]>([])
  const [isFullscreen, setIsFullscreen] = useState(false)

  // Initialize map
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return

    mapRef.current = L.map(containerRef.current).setView([19.076, 72.8777], 12)

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(mapRef.current)
  }, [])

  // Update markers
  useEffect(() => {
    const map = mapRef.current
    if (!map) return

    // Remove old markers
    markersRef.current.forEach((m) => m.remove())
    markersRef.current = []

    const newMarkers: L.Marker[] = []
    allPlaces.forEach((p) => {
      if (p.latitude != null && p.longitude != null) {
        const marker = L.marker([p.latitude, p.longitude], { icon: markerIcon }).bindPopup(
          `<b>${p.name}</b><br/><span style="color:black">${p.address ?? ""}</span>`,
        )
        marker.addTo(map)
        newMarkers.push(marker)
      }
    })

    markersRef.current = newMarkers

    if (newMarkers.length > 0) {
      const group = L.featureGroup(newMarkers)
      map.fitBounds(group.getBounds().pad(0.2))
    }
  }, [allPlaces])

  // Toggle fullscreen
  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen)
  }

  // Handle map resize when fullscreen changes
  useEffect(() => {
    const map = mapRef.current
    if (!map) return

    // Use a timeout to ensure the DOM has updated before resizing the map
    const timer = setTimeout(() => {
      map.invalidateSize()
    }, 100)

    return () => clearTimeout(timer)
  }, [isFullscreen])

  // Handle ESC key to exit fullscreen
  useEffect(() => {
    const handleEscKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isFullscreen) {
        setIsFullscreen(false)
      }
    }

    document.addEventListener("keydown", handleEscKey)
    return () => document.removeEventListener("keydown", handleEscKey)
  }, [isFullscreen])

  return (
    <div className={isFullscreen ? "fixed inset-0 z-40 bg-white" : "relative h-full w-full rounded-lg"}>
      {/* Fullscreen button inside map container with proper z-index */}
      <div className={`absolute ${isFullscreen ? 'top-4 right-4' : 'top-2 right-2'} z-[1000]`}>
        <button
          onClick={toggleFullscreen}
          className="rounded-md border bg-white dark:bg-gray-800 px-3 py-1 text-sm shadow-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          {isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
        </button>
      </div>

      <div
        ref={containerRef}
        className="h-full w-full"
      />
    </div>
  )
}