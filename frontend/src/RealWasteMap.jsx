import React, { useEffect, useState } from 'react';
import {
  CircleMarker,
  MapContainer,
  Popup,
  TileLayer,
  useMap,
} from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const DEFAULT_CENTER = [12.9716, 77.5946];

function RecenterMap({ position }) {
  const map = useMap();

  useEffect(() => {
    if (position) {
      map.flyTo(position, 13, { duration: 1.2 });
    }
  }, [position, map]);

  return null;
}

function getPriority(fill) {
  if (fill >= 90) return 'CRITICAL';
  if (fill >= 70) return 'HIGH';
  if (fill >= 45) return 'MEDIUM';
  return 'LOW';
}

function getColor(fill) {
  if (fill >= 90) return '#ff6b6b';
  if (fill >= 70) return '#f3b35c';
  if (fill >= 45) return '#c6d763';
  return '#6fea93';
}

export default function RealWasteMap({ bins = [] }) {
  const [userLocation, setUserLocation] = useState(null);
  const [locationError, setLocationError] = useState('');
  const [locating, setLocating] = useState(false);

  function useMyLocation() {
    if (!navigator.geolocation) {
      setLocationError('Geolocation is not supported by this browser.');
      return;
    }

    setLocating(true);
    setLocationError('');

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setUserLocation([
          position.coords.latitude,
          position.coords.longitude,
        ]);
        setLocating(false);
      },
      (error) => {
        setLocationError(error.message || 'Location permission was denied.');
        setLocating(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    );
  }

  return (
    <div className="real-map-wrapper">
      <div className="map-toolbar">
        <div>
          <span className="eyebrow">LIVE GEOLOCATION</span>
          <strong>{bins.length} monitored assets</strong>
        </div>

        <button onClick={useMyLocation} disabled={locating}>
          {locating ? 'LOCATING...' : '⌖ USE MY LOCATION'}
        </button>
      </div>

      <MapContainer
        center={DEFAULT_CENTER}
        zoom={12}
        scrollWheelZoom
        className="real-waste-map"
      >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {userLocation && (
          <>
            <RecenterMap position={userLocation} />

            <CircleMarker
              center={userLocation}
              radius={9}
              pathOptions={{
                color: '#ffffff',
                fillColor: '#4da6ff',
                fillOpacity: 1,
                weight: 3,
              }}
            >
              <Popup>
                <strong>Your current location</strong>
                <br />
                Location shared by browser permission.
              </Popup>
            </CircleMarker>
          </>
        )}

        {bins.map((bin) => {
          const latitude = Number(bin.latitude);
          const longitude = Number(bin.longitude);

          if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
            return null;
          }

          const priority = getPriority(Number(bin.fill_level));
          const color = getColor(Number(bin.fill_level));

          return (
            <CircleMarker
              key={bin.id}
              center={[latitude, longitude]}
              radius={priority === 'CRITICAL' ? 11 : 8}
              pathOptions={{
                color,
                fillColor: color,
                fillOpacity: 0.82,
                weight: 2,
              }}
            >
              <Popup>
                <div className="map-popup">
                  <strong>{bin.code}</strong>
                  <span>{bin.ward}</span>

                  <hr />

                  <span>
                    Fill: <b>{bin.fill_level}%</b>
                  </span>

                  <span>
                    Priority: <b>{priority}</b>
                  </span>

                  <span>
                    Capacity: <b>{bin.capacity_kg} kg</b>
                  </span>

                  <span>
                    Coordinates:{' '}
                    <b>
                      {latitude.toFixed(5)}, {longitude.toFixed(5)}
                    </b>
                  </span>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>

      {locationError && (
        <div className="map-location-error">
          {locationError}
        </div>
      )}
    </div>
  );
}
