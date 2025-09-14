'use client'

import { useEffect } from 'react'
import { FocusStyleManager } from '@blueprintjs/core'

export default function BlueprintSetup() {
  useEffect(() => {
    // Show focus styles only when using keyboard (accessibility best practice)
    FocusStyleManager.onlyShowFocusOnTabs()
  }, [])

  return null
}
