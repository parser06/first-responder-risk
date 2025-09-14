'use client'

import { OfficerState, RiskLevel } from '@/lib/types'
import { formatDistanceToNow } from 'date-fns'
import {
  Card,
  Elevation,
  Icon,
  Tag,
  Button,
  NonIdealState,
  ProgressBar,
  Intent,
  Divider,
} from '@blueprintjs/core'

interface OfficerListProps {
  officers: OfficerState[]
  selectedOfficer: OfficerState | null
  onOfficerSelect: (officer: OfficerState) => void
  onAlertNearby: (officer: OfficerState) => void
}

export default function OfficerList({ 
  officers, 
  selectedOfficer, 
  onOfficerSelect,
  onAlertNearby,
}: OfficerListProps) {
  const riskIntent = (riskLevel: RiskLevel): Intent => {
    switch (riskLevel) {
      case 'high': return Intent.DANGER
      case 'medium': return Intent.WARNING
      case 'low':
      default:
        return Intent.SUCCESS
    }
  }

  const formatLastSeen = (lastSeen: string) => {
    try {
      return formatDistanceToNow(new Date(lastSeen), { addSuffix: true })
    } catch {
      return 'Unknown'
    }
  }

  const batteryIntent = (batteryLevel?: number): Intent | undefined => {
    if (batteryLevel == null) return undefined
    if (batteryLevel > 0.5) return Intent.SUCCESS
    if (batteryLevel > 0.2) return Intent.WARNING
    return Intent.DANGER
  }

  const networkIcon = (networkStatus?: string) => {
    switch (networkStatus) {
      case 'wifi': return 'sensor'
      case 'cellular': return 'cell-tower'
      case 'offline': return 'offline'
      default: return 'signal-search'
    }
  }

  if (officers.length === 0) {
    return (
      <NonIdealState
        icon={<Icon icon="person" />}
        title="No Officers Active"
        description="Waiting for officer data..."
      />
    )
  }

  return (
    <div>
      {officers.map((officer) => (
        <Card
          key={officer.id}
          interactive
          elevation={selectedOfficer?.id === officer.id ? Elevation.TWO : Elevation.ONE}
          onClick={() => onOfficerSelect(officer)}
          style={{ marginBottom: 8 }}
        >
          {/* Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <Icon icon="person" />
              <div>
                <div style={{ fontWeight: 600 }}>{officer.name}</div>
                <div style={{ fontSize: 12, opacity: 0.8 }}>{officer.badgeNumber}</div>
              </div>
            </div>
          {officer.fallDetected && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Icon icon="warning-sign" intent={Intent.DANGER} />
              <span style={{ fontSize: 12, fontWeight: 600 }}>FALL DETECTED</span>
            </div>
          )}
            <Tag large intent={riskIntent(officer.riskLevel)}>
              {officer.riskLevel.toUpperCase()}
            </Tag>
          </div>

          <Divider></Divider>

          {/* Status Indicators */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginTop: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Icon icon="heart" />
              <span style={{ fontSize: 12 }}>
                {officer.heartRate ? `${officer.heartRate} BPM` : 'N/A'}
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Icon icon="pulse" />
              <span style={{ fontSize: 12 }}>
                {officer.activityType || 'Unknown'}
              </span>
            </div>
          </div>

          {/* Alerts */}

          {/* Footer */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 12, opacity: 0.8, marginTop: 8 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span>
                <Icon icon="time" style={{ marginRight: 4 }} />
                {formatLastSeen(officer.lastSeen)}
              </span>
              {officer.batteryLevel != null && (
                <span>
                  <Icon icon="power" intent={batteryIntent(officer.batteryLevel)} style={{ marginRight: 4 }} />
                  {Math.round(officer.batteryLevel * 100)}%
                </span>
              )}
            </div>
            <div>
              <Icon icon={networkIcon(officer.networkStatus)} style={{ marginRight: 6 }} />
              <span>{officer.networkStatus || 'Unknown'}</span>
            </div>
          </div>

          {/* Risk Score Bar */}
          <div style={{ marginTop: 8 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, opacity: 0.8, marginBottom: 4 }}>
              <span>Risk Score</span>
              <span>{Math.round(officer.riskScore * 100)}%</span>
            </div>
            <ProgressBar intent={riskIntent(officer.riskLevel)} value={Math.min(officer.riskScore, 1)} stripes={officer.riskLevel !== 'low'} animate={false} />
          </div>

          {/* Alert Nearby */}
          <div style={{ marginTop: 8, display: 'flex', gap: 8 }}>
            <Button small intent={Intent.DANGER} icon={<Icon icon="warning-sign" />} onClick={(e) => { e.stopPropagation(); onAlertNearby(officer) }}>
              Alert Nearby
            </Button>
          </div>
        </Card>
      ))}
    </div>
  )
}
