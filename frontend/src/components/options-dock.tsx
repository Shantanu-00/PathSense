"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { Place } from "@/lib/types"
import { toast } from "sonner"

interface Props {
  sessionId: string | null
  places: Place[]
  start: Place | null
  end: Place | null
  onPlacesUpdate: (newPlaces: Place[], start?: Place | null, end?: Place | null, replace?: boolean) => void
  onOptimize: (algo: "nn" | "nn2opt" | "ga", returnToStart: boolean) => void
  onClearResult: () => void
  resetStartEnd: (resetStart: boolean, resetEnd: boolean) => Promise<void>
}

export default function OptionsDock({
  sessionId,
  places,
  start,
  end,
  onPlacesUpdate,
  onOptimize,
  onClearResult,
  resetStartEnd,
}: Props) {
  const [open, setOpen] = useState<"add" | "find" | "remove" | null>(null)
  const [customName, setCustomName] = useState("")
  const [customAddress, setCustomAddress] = useState("")
  const [findType, setFindType] = useState("")
  const [findLocation, setFindLocation] = useState("")
  const [findCount, setFindCount] = useState(5)
  const [algo, setAlgo] = useState<"nn" | "nn2opt" | "ga">("nn")
  const [returnToStart, setReturnToStart] = useState(true)
  const [optimizing, setOptimizing] = useState(false)

  const isReturnToStartDisabled = !!end && start?.id !== end?.id

  async function addCustomPlace() {
  if (!sessionId || !customName || !customAddress) return

  try {
    // Step 1: Geocode the address using your backend
    const geoRes = await fetch(
      `/api/v1/geocode?address=${encodeURIComponent(customAddress)}`
    )

    if (!geoRes.ok) {
      const geoErr = await geoRes.text()
      throw new Error(`Geocoding failed: ${geoErr}`)
    }

    const { latitude, longitude } = await geoRes.json()

    // Step 2: Construct full place object
    const newPlace = {
      name: customName,
      address: customAddress,
      latitude,
      longitude,
    }

    // Step 3: Send to backend to add place
    const res = await fetch(
      `/api/v1/add-place?session_id=${encodeURIComponent(sessionId)}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newPlace),
      }
    )

    if (!res.ok) {
      const raw = await res.text()
      console.error("[Add Place Error Raw]", raw)

      let message = "Failed to add place"
      try {
        const parsed = JSON.parse(raw)
        message =
          typeof parsed.detail === "string"
            ? parsed.detail
            : typeof parsed.detail === "object"
            ? JSON.stringify(parsed.detail)
            : message
      } catch {
        message = raw || message
      }

      toast.error(message)
      throw new Error(message)
    }

    const data = await res.json()
    toast.success("Place added")
    onPlacesUpdate(data.places || [], data.start ?? null, data.end ?? null, false)
    setCustomName("")
    setCustomAddress("")
  } catch (err: any) {
    console.error("[Add Place Error]", err)
    toast.error(err.message || "Failed to add place")
  }
}

  async function findMore() {
  if (!sessionId || !findType || !findLocation || findCount < 1) return

  try {
    const res = await fetch(
      `/api/v1/find-places?session_id=${encodeURIComponent(sessionId)}&business_type=${encodeURIComponent(findType)}&location=${encodeURIComponent(findLocation)}&count=${findCount}`,
      { method: "GET" }
    )

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || "Failed to find places")
    }

    const data = await res.json()
    toast.success("Places found")
    
    // Fix: Pass the data in the correct format
    onPlacesUpdate(data.places || [], data.start ?? null, data.end ?? null, false)
  } catch (err: any) {
    console.error("[Find Places Error]", err)
    toast.error(err.message || "Failed to find places")
  }
}
  async function removePlace(id: string) {
    if (!sessionId || !id) return

    try {
      if (id === start?.id || id === end?.id) {
        await resetStartEnd(id === start?.id, id === end?.id)
      }

      const res = await fetch(`/api/v1/remove-place?session_id=${encodeURIComponent(sessionId)}`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ place_id: id }),
})

      if (!res.ok) {
  const raw = await res.text()
  console.error("[Remove Place Error Raw]", raw)

  let message = "Failed to remove place"
  try {
    const parsed = JSON.parse(raw)
    message =
      typeof parsed.detail === "string"
        ? parsed.detail
        : typeof parsed.detail === "object"
        ? JSON.stringify(parsed.detail)
        : message
  } catch {
    message = raw || message
  }

  toast.error(message)
  throw new Error(message)
}

      const data = await res.json()
      toast.success("Place removed")
      onPlacesUpdate(data.places || [], data.start ?? null, data.end ?? null, true)
    } catch (err: any) {
      console.error("[Remove Place Error]", err)
      toast.error(err.message || "Failed to remove place")
    }
  }

  function optimize() {
    setOptimizing(true)
    onOptimize(algo, returnToStart)
    setTimeout(() => setOptimizing(false), 1000)
  }

  return (
    <div className="flex h-full flex-col rounded-md border p-3 bg-gray-50 dark:bg-gray-900 overflow-hidden">
      <h2 className="text-lg font-semibold mb-4">Options</h2>

      <div className="flex-1 overflow-y-auto space-y-4">
        {/* Add Custom Place */}
        <div>
          <Button
            variant={open === "add" ? "default" : "outline"}
            className="w-full mb-2"
            onClick={() => setOpen(open === "add" ? null : "add")}
          >
            Add Custom Place
          </Button>
          {open === "add" && (
            <div className="space-y-2 p-2 border rounded-md bg-white dark:bg-gray-800">
              <Input placeholder="Place name" value={customName} onChange={(e) => setCustomName(e.target.value)} />
              <Input placeholder="Address" value={customAddress} onChange={(e) => setCustomAddress(e.target.value)} />
              <Button className="w-full" onClick={addCustomPlace}>
                Add Place
              </Button>
            </div>
          )}
        </div>

        {/* Find More Places */}
        <div>
          <Button
            variant={open === "find" ? "default" : "outline"}
            className="w-full mb-2"
            onClick={() => setOpen(open === "find" ? null : "find")}
          >
            Find More Places
          </Button>
          {open === "find" && (
            <div className="space-y-2 p-2 border rounded-md bg-white dark:bg-gray-800">
              <Input
                placeholder="Business type (e.g., restaurant, cafe)"
                value={findType}
                onChange={(e) => setFindType(e.target.value)}
              />
              <Input
                placeholder="Location"
                value={findLocation}
                onChange={(e) => setFindLocation(e.target.value)}
              />
              <div className="flex items-center gap-2">
                <Label>Count:</Label>
                <Input
                  type="number"
                  min="1"
                  max="20"
                  value={findCount}
                  onChange={(e) => setFindCount(Number(e.target.value))}
                  className="w-16"
                />
              </div>
              <Button className="w-full" onClick={findMore}>
                Find Places
              </Button>
            </div>
          )}
        </div>

        {/* Remove Places */}
        <div>
          <Button
            variant={open === "remove" ? "default" : "outline"}
            className="w-full mb-2"
            onClick={() => setOpen(open === "remove" ? null : "remove")}
          >
            Remove Places
          </Button>
          {open === "remove" && (
            <div className="space-y-2 p-2 border rounded-md bg-white dark:bg-gray-800 max-h-40 overflow-y-auto">
              {places.map((place, index) => (
                <div key={place.id || index} className="flex items-center justify-between p-2 border rounded">
                  <span className="text-sm truncate">{place.name}</span>
                  <Button variant="destructive" size="sm" onClick={() => place.id && removePlace(place.id)}>
                    Remove
                  </Button>
                </div>
              ))}
              {places.length === 0 && (
                <p className="text-sm text-gray-500 text-center">No places to remove</p>
              )}
            </div>
          )}
        </div>

        {/* Optimization Options */}
        <div className="bg-white dark:bg-gray-800 p-3 rounded-md border">
          <h3 className="font-semibold mb-3 text-center">Optimization</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
                            <Label className="flex-1">Algorithm:</Label>
              <Select value={algo} onValueChange={(value: "nn" | "nn2opt" | "ga") => setAlgo(value)}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="nn">Nearest Neighbor</SelectItem>
                  <SelectItem value="nn2opt">NN + 2-opt</SelectItem>
                  <SelectItem value="ga">Genetic Algorithm</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center justify-between">
              <Label className="flex-1">Return to start:</Label>
              <Switch
                checked={returnToStart}
                onCheckedChange={(checked) => setReturnToStart(checked)}
                disabled={isReturnToStartDisabled}
              />
            </div>

            {isReturnToStartDisabled && (
              <p className="text-xs text-gray-500 text-center">
                Return to start disabled when end point is set
              </p>
            )}

            <Button
              className="w-full mt-2"
              onClick={optimize}
              disabled={optimizing || places.length < 2}
            >
              {optimizing ? "Optimizing..." : "Optimize Route"}
            </Button>
          </div>
        </div>

        {/* Clear Result */}
        <div>
          <Button variant="outline" className="w-full" onClick={onClearResult}>
            Clear Result
          </Button>
        </div>
      </div>
    </div>
  )
}