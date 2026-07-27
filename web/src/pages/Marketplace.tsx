import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { MARKETPLACE_HTML, initMarketplace } from './portal/marketplacePortal'

/**
 * Marketplace — exact mirror of the :8777 portal marketplace
 * (portal/marketplace.html): the public, login-gated-checkout index with its
 * full filter / sort / card engine.
 *
 * Same seam as Landing: markup via dangerouslySetInnerHTML, engine run once
 * (StrictMode-safe once-guard), stable `navigate` for internal anchors. The
 * engine's single document-level "outside click closes sort menu" listener is
 * self-removing (see marketplacePortal.ts), so nothing leaks on unmount.
 */
export default function Marketplace() {
  const navigate = useNavigate()
  const navRef = useRef(navigate)
  navRef.current = navigate
  const didInit = useRef(false)

  useEffect(() => {
    if (didInit.current) return
    didInit.current = true
    initMarketplace((to: string) => navRef.current(to))
  }, [])

  return <div dangerouslySetInnerHTML={{ __html: MARKETPLACE_HTML }} />
}
