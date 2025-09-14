'use client'

import { useState, useEffect, useRef } from 'react'
import dynamic from 'next/dynamic'
import { useLiveFeed } from '@/lib/useLiveFeed'
import OfficerList from '@/components/OfficerList'
import { OfficerState, RiskLevel } from '@/lib/types'
import {
  Navbar,
  NavbarGroup,
  NavbarHeading,
  Alignment,
  Tag,
  Icon,
  Card,
  H5,
  H3,
  Divider,
  Callout,
  Intent,
  Position,
  OverlayToaster,
  Button,
} from '@blueprintjs/core'

// Dynamically import the map to avoid SSR issues
const MapView = dynamic(() => import('@/components/MapView'), { ssr: false })

export default function Dashboard() {
  const [officers, setOfficers] = useState<OfficerState[]>([])
  const [selectedOfficer, setSelectedOfficer] = useState<OfficerState | null>(null)
  const [alerts, setAlerts] = useState<any[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [alertMode, setAlertMode] = useState(false)
  const [alertRadius, setAlertRadius] = useState<number>(300)
  const [highlightedIds, setHighlightedIds] = useState<string[]>([])
  const toasterRef = useRef<any>(null)

  const {
    officers: liveOfficers,
    alerts: liveAlerts,
    connectionStatus,
  } = useLiveFeed()

  useEffect(() => {
    setOfficers(liveOfficers)
    setIsConnected(connectionStatus === 'connected')
  }, [liveOfficers, connectionStatus])

  useEffect(() => {
    setAlerts(liveAlerts)
  }, [liveAlerts])

  const getRiskCounts = () => {
    const counts = { high: 0, medium: 0, low: 0 }
    officers.forEach((officer) => {
      counts[officer.riskLevel]++
    })
    return counts
  }

  const riskCounts = getRiskCounts()

  return (
    <div>
      {/* Header */}
      <Navbar>
        <NavbarGroup align={Alignment.LEFT}>
          <Icon icon="pulse" style={{ marginRight: 8 }} />
          <NavbarHeading>First Responder Risk Monitoring</NavbarHeading>
        </NavbarGroup>
        <NavbarGroup align={Alignment.RIGHT}>
          <Tag intent={isConnected ? Intent.SUCCESS : Intent.DANGER} round>
            <Icon icon={isConnected ? 'confirm' : 'offline'} style={{ marginRight: 6 }} />
            {isConnected ? 'Connected' : 'Disconnected'}
          </Tag>
        </NavbarGroup>
      </Navbar>

      {/* Alerts */}
      <div style={{ padding: 12 }}>
        <OverlayToaster position={Position.TOP} ref={toasterRef} />
        {alerts.map((alert, index) => (
          <Callout key={index} intent={Intent.DANGER} icon="warning-sign" title={alert.title || 'Alert'} style={{ marginBottom: 8 }}>
            {alert.message}
          </Callout>
        ))}
      </div>

      {/* Main Content */}
      <div style={{ padding: 16 }}>
        {/* Stats */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 12, marginBottom: 16 }}>
          <Card>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <Icon icon="people" />
              <div>
                <div style={{ fontSize: 12, opacity: 0.8 }}>Total Officers</div>
                <H3 style={{ margin: 0 }}>{officers.length}</H3>
              </div>
            </div>
          </Card>
          <Card>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <Tag large intent={Intent.DANGER} round>H</Tag>
              <div>
                <div style={{ fontSize: 12, opacity: 0.8 }}>High Risk</div>
                <H3 style={{ margin: 0, color: '#f55656' }}>{riskCounts.high}</H3>
              </div>
            </div>
          </Card>
          <Card>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <Tag large intent={Intent.WARNING} round>M</Tag>
              <div>
                <div style={{ fontSize: 12, opacity: 0.8 }}>Medium Risk</div>
                <H3 style={{ margin: 0, color: '#f2b824' }}>{riskCounts.medium}</H3>
              </div>
            </div>
          </Card>
          <Card>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <Tag large intent={Intent.SUCCESS} round>L</Tag>
              <div>
                <div style={{ fontSize: 12, opacity: 0.8 }}>Low Risk</div>
                <H3 style={{ margin: 0, color: '#4dc27d' }}>{riskCounts.low}</H3>
              </div>
            </div>
          </Card>
        </div>

        {/* Main Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16 }}>
          {/* Map Card */}
          <Card style={{ height: 680 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <H5 style={{ display: 'flex', alignItems: 'center', gap: 8, margin: 0 }}>
                <Icon icon="map-marker" /> Officer Locations
              </H5>
              <div style={{ fontSize: 12, opacity: 0.8 }}>{officers.length} officers active</div>
            </div>
            {alertMode && selectedOfficer && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
                <Icon icon="warning-sign" />
                <span style={{ fontSize: 12, opacity: 0.9 }}>Alert officers within radius (meters):</span>
                <input
                  type="range"
                  min={50}
                  max={2000}
                  step={50}
                  value={alertRadius}
                  onChange={(e) => setAlertRadius(parseInt(e.target.value, 10))}
                  style={{ width: 240 }}
                />
                <Tag minimal>{alertRadius} m</Tag>
                <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
                  <Button minimal onClick={() => setAlertMode(false)}>Cancel</Button>
                  <Button
                    intent={Intent.DANGER}
                    onClick={async () => {
                      try {
                        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001'
                        const res = await fetch(`${apiUrl}/api/alerts/nearby`, {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({
                            sourceOfficerId: selectedOfficer.id,
                            radiusMeters: alertRadius,
                            title: 'Officer Down',
                            message: `Assist ${selectedOfficer.name}`,
                          })
                        })
                        if (res.ok) {
                          const data = await res.json()
                          const targets: string[] = data.targets || []
                          setHighlightedIds(targets)
                          toasterRef.current?.show({ message: `${targets.length} officer(s) alerted`, intent: Intent.WARNING, timeout: 3000 })
                          setTimeout(() => setHighlightedIds([]), 10000)
                        }
                        setAlertMode(false)
                      } catch (e) {
                        console.error('Alert create error', e)
                      }
                    }}
                  >
                    Send Alert
                  </Button>
                </div>
              </div>
            )}
            <div style={{ height: 600 }}>
              <MapView
                officers={officers}
                selectedOfficer={selectedOfficer}
                onOfficerSelect={setSelectedOfficer}
                alertCircle={alertMode && selectedOfficer && selectedOfficer.latitude && selectedOfficer.longitude ? {
                  center: [selectedOfficer.latitude, selectedOfficer.longitude],
                  radiusMeters: alertRadius,
                } : null}
                highlightedIds={highlightedIds}
                onStartAlert={(officer) => { setSelectedOfficer(officer); setAlertMode(true) }}
              />
            </div>
          </Card>

          {/* Officer List */}
          <Card style={{ height: 680, display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <H5 style={{ display: 'flex', alignItems: 'center', gap: 8, margin: 0 }}>
                <Icon icon="pulse" /> Officer Status
              </H5>
              <div style={{ fontSize: 12, opacity: 0.8 }}>Real-time updates</div>
            </div>
            <div style={{ overflowY: 'auto' }}>
              <OfficerList
                officers={officers}
                selectedOfficer={selectedOfficer}
                onOfficerSelect={setSelectedOfficer}
                onAlertNearby={(officer) => { setSelectedOfficer(officer); setAlertMode(true) }}
              />
            </div>
          </Card>
        </div>

        {/* Officer Details */}
        {selectedOfficer && (
          <Card style={{ marginTop: 16 }}>
            <H5 style={{ marginTop: 0 }}>Officer Details: {selectedOfficer.name}</H5>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
              <div>
                <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 6 }}>Basic Info</div>
                <div>
                  <div><strong>Badge:</strong> {selectedOfficer.badgeNumber}</div>
                  <div><strong>Department:</strong> {selectedOfficer.department}</div>
                  <div>
                    <strong>Status:</strong>
                    <Tag minimal intent={selectedOfficer.riskLevel === 'high' ? Intent.DANGER : selectedOfficer.riskLevel === 'medium' ? Intent.WARNING : Intent.SUCCESS} style={{ marginLeft: 8 }}>
                      {selectedOfficer.riskLevel.toUpperCase()}
                    </Tag>
                  </div>
                </div>
              </div>
              <div>
                <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 6 }}>Health Data</div>
                <div>
                  <div><strong>Heart Rate:</strong> {selectedOfficer.heartRate || 'N/A'} BPM</div>
                  <div><strong>Activity:</strong> {selectedOfficer.activityType || 'Unknown'}</div>
                  <div>
                    <strong>Fall Detected:</strong>
                    <span style={{ marginLeft: 6, color: selectedOfficer.fallDetected ? '#f55656' : '#4dc27d', fontWeight: 600 }}>
                      {selectedOfficer.fallDetected ? 'YES' : 'NO'}
                    </span>
                  </div>
                </div>
              </div>
              <div>
                <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 6 }}>Location</div>
                <div>
                  <div><strong>Latitude:</strong> {selectedOfficer.latitude?.toFixed(6) || 'N/A'}</div>
                  <div><strong>Longitude:</strong> {selectedOfficer.longitude?.toFixed(6) || 'N/A'}</div>
                  <div><strong>Accuracy:</strong> {selectedOfficer.accuracy ? `${selectedOfficer.accuracy.toFixed(0)}m` : 'N/A'}</div>
                  <div><strong>Last Update:</strong> {selectedOfficer.lastSeen}</div>
                </div>
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}
