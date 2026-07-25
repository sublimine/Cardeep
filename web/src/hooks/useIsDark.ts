import { useEffect, useState } from 'react'

/** Tracks the `.light` class on <html>, set by Shell's theme toggle. */
export function useIsDark(): boolean {
  const [dark, setDark] = useState(() => !document.documentElement.classList.contains('light'))
  useEffect(() => {
    const obs = new MutationObserver(() => setDark(!document.documentElement.classList.contains('light')))
    obs.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
    return () => obs.disconnect()
  }, [])
  return dark
}
