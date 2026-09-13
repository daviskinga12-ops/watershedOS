import { useMemo } from 'react'
import Map, { Layer, Source } from 'react-map-gl'

const TOKEN = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN || ''

function scoreColorExpr() {
  return [
    'case',
    ['==', ['get', 'health_score'], null],
    '#9ca3af',
    ['<=', ['get', 'health_score'], 40],
    '#dc2626',
    ['<=', ['get', 'health_score'], 70],
    '#ea580c',
    '#16a34a',
  ]
}

export default function MapView({ zones = [], selectedId, onSelect }) {
  const geojson = useMemo(
    () => ({
      type: 'FeatureCollection',
      features: zones.map((z) => ({
        type: 'Feature',
        id: z.id,
        properties: {
          id: z.id,
          name: z.name,
          zone_type: z.zone_type,
          health_score: z.latest_health_score,
        },
        geometry: z.geojson,
      })),
    }),
    [zones],
  )

  if (!TOKEN) {
    return (
      <div className="flex h-full min-h-[320px] items-center justify-center rounded-lg border border-dashed border-watershed-deep/20 bg-white p-6 text-sm text-watershed-deep/70">
        Set VITE_MAPBOX_ACCESS_TOKEN to render the map.
      </div>
    )
  }

  return (
    <div className="h-full min-h-[320px] overflow-hidden rounded-lg border border-watershed-deep/10">
      <Map
        mapboxAccessToken={TOKEN}
        initialViewState={{ longitude: 37.0, latitude: -0.5, zoom: 7 }}
        style={{ width: '100%', height: '100%' }}
        mapStyle="mapbox://styles/mapbox/outdoors-v12"
        interactiveLayerIds={['zones-fill']}
        onClick={(e) => {
          const f = e.features?.[0]
          if (f?.properties?.id != null) onSelect?.(Number(f.properties.id))
        }}
      >
        <Source id="zones" type="geojson" data={geojson}>
          <Layer
            id="zones-fill"
            type="fill"
            paint={{
              'fill-color': scoreColorExpr(),
              'fill-opacity': [
                'case',
                ['==', ['get', 'id'], selectedId ?? -1],
                0.75,
                0.45,
              ],
            }}
          />
          <Layer
            id="zones-outline"
            type="line"
            paint={{
              'line-color': '#0c3b2e',
              'line-width': 1.2,
            }}
          />
        </Source>
      </Map>
    </div>
  )
}
