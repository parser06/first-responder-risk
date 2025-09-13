'use client'

import { AlertTriangle, X, Clock, User } from 'lucide-react'
import { useState } from 'react'
import { formatDistanceToNow } from 'date-fns'

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

  const getSeverityStyles = (severity?: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 border-red-400 text-red-800'
      case 'high':
        return 'bg-red-50 border-red-300 text-red-700'
      case 'medium':
        return 'bg-yellow-50 border-yellow-300 text-yellow-700'
      case 'low':
        return 'bg-blue-50 border-blue-300 text-blue-700'
      default:
        return 'bg-gray-50 border-gray-300 text-gray-700'
    }
  }

  const getSeverityIcon = (severity?: string) => {
    switch (severity) {
      case 'critical':
      case 'high':
        return <AlertTriangle className="h-5 w-5 text-red-600" />
      case 'medium':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />
      case 'low':
        return <AlertTriangle className="h-5 w-5 text-blue-600" />
      default:
        return <AlertTriangle className="h-5 w-5 text-gray-600" />
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
    <div className={`alert-banner ${getSeverityStyles(alert.severity)}`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          {getSeverityIcon(alert.severity)}
        </div>
        <div className="ml-3 flex-1">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium">
              {alert.title || 'Risk Alert'}
            </h3>
            <div className="flex items-center space-x-2">
              {alert.timestamp && (
                <div className="flex items-center text-xs opacity-75">
                  <Clock className="h-3 w-3 mr-1" />
                  {formatTimestamp(alert.timestamp)}
                </div>
              )}
              {onDismiss && (
                <button
                  onClick={handleDismiss}
                  className="flex-shrink-0 ml-2 text-current opacity-75 hover:opacity-100"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>
          <div className="mt-1">
            <p className="text-sm">
              {alert.message}
            </p>
            {alert.officerName && (
              <div className="flex items-center mt-1 text-xs opacity-75">
                <User className="h-3 w-3 mr-1" />
                Officer: {alert.officerName}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
