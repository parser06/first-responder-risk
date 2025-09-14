'use client'

import { useState } from 'react'
import { formatDistanceToNow } from 'date-fns'
import { Callout, Button, Icon, Intent } from '@blueprintjs/core'

interface AlertBannerProps {
  alert: {
    id: string
    type: string
    title?: string
    message: string
    severity?: 'low' | 'medium' | 'high' | 'critical'
    timestamp?: string
    officerId?: string
    officerName?: string
  }
  onDismiss?: (alertId: string) => void
}

export default function AlertBanner({ alert, onDismiss }: AlertBannerProps) {
  const [isDismissed, setIsDismissed] = useState(false)

  const handleDismiss = () => {
    setIsDismissed(true)
    if (onDismiss) {
      onDismiss(alert.id)
    }
  }

  if (isDismissed) {
    return null
  }

  const intentFromSeverity = (severity?: string): Intent | undefined => {
    switch (severity) {
      case 'critical':
      case 'high':
        return Intent.DANGER
      case 'medium':
        return Intent.WARNING
      case 'low':
        return Intent.PRIMARY
      default:
        return undefined
    }
  }

  const formatTimestamp = (timestamp?: string) => {
    if (!timestamp) return 'Just now'
    try {
      return formatDistanceToNow(new Date(timestamp), { addSuffix: true })
    } catch {
      return 'Unknown time'
    }
  }

  return (
    <Callout
      icon="warning-sign"
      intent={intentFromSeverity(alert.severity)}
      title={alert.title || 'Risk Alert'}
      style={{ margin: '8px 0' }}
      rightElement={
        onDismiss ? (
          <Button minimal icon={<Icon icon="cross" />} onClick={handleDismiss} aria-label="Dismiss alert" />
        ) : undefined
      }
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span>{alert.message}</span>
        {alert.officerName && (
          <span style={{ opacity: 0.8 }}>
            <Icon icon="person" style={{ marginRight: 4 }} /> Officer: {alert.officerName}
          </span>
        )}
        {alert.timestamp && (
          <span style={{ marginLeft: 'auto', opacity: 0.8 }}>
            <Icon icon="time" style={{ marginRight: 4 }} /> {formatTimestamp(alert.timestamp)}
          </span>
        )}
      </div>
    </Callout>
  )
}
