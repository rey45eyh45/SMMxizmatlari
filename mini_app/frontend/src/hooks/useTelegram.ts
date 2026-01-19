import { useCallback, useMemo } from 'react'
import type { TelegramWebApp, TelegramUser } from '../types'

export function useTelegram() {
  const tg: TelegramWebApp | undefined = useMemo(() => {
    if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
      return window.Telegram.WebApp
    }
    return undefined
  }, [])

  const user: TelegramUser | undefined = useMemo(() => {
    return tg?.initDataUnsafe?.user
  }, [tg])

  const initData = useMemo(() => {
    return tg?.initData || ''
  }, [tg])

  const colorScheme = useMemo(() => {
    return tg?.colorScheme || 'light'
  }, [tg])

  const ready = useCallback(() => {
    tg?.ready()
  }, [tg])

  const close = useCallback(() => {
    tg?.close()
  }, [tg])

  const expand = useCallback(() => {
    tg?.expand()
  }, [tg])

  const showAlert = useCallback((message: string) => {
    if (tg) {
      tg.showAlert(message)
    } else {
      alert(message)
    }
  }, [tg])

  const showConfirm = useCallback((message: string): Promise<boolean> => {
    return new Promise((resolve) => {
      if (tg) {
        tg.showConfirm(message, (confirmed) => {
          resolve(confirmed)
        })
      } else {
        resolve(confirm(message))
      }
    })
  }, [tg])

  const hapticFeedback = useMemo(() => ({
    impact: (style: 'light' | 'medium' | 'heavy' = 'medium') => {
      tg?.HapticFeedback?.impactOccurred(style)
    },
    notification: (type: 'error' | 'success' | 'warning') => {
      tg?.HapticFeedback?.notificationOccurred(type)
    },
    selection: () => {
      tg?.HapticFeedback?.selectionChanged()
    }
  }), [tg])

  const mainButton = useMemo(() => ({
    show: (text: string, onClick: () => void) => {
      if (tg?.MainButton) {
        tg.MainButton.setText(text)
        tg.MainButton.onClick(onClick)
        tg.MainButton.show()
      }
    },
    hide: () => {
      tg?.MainButton?.hide()
    },
    showProgress: () => {
      tg?.MainButton?.showProgress()
    },
    hideProgress: () => {
      tg?.MainButton?.hideProgress()
    },
    enable: () => {
      tg?.MainButton?.enable()
    },
    disable: () => {
      tg?.MainButton?.disable()
    }
  }), [tg])

  const backButton = useMemo(() => ({
    show: (onClick: () => void) => {
      if (tg?.BackButton) {
        tg.BackButton.onClick(onClick)
        tg.BackButton.show()
      }
    },
    hide: () => {
      tg?.BackButton?.hide()
    }
  }), [tg])

  // Tashqi havolani ochish (Click, Payme va h.k. uchun)
  const openLink = useCallback((url: string, options?: { try_instant_view?: boolean }) => {
    if (tg?.openLink) {
      tg.openLink(url, options)
    } else {
      window.open(url, '_blank')
    }
  }, [tg])

  // Telegram havolasini ochish (t.me/...)
  const openTelegramLink = useCallback((url: string) => {
    if (tg?.openTelegramLink) {
      tg.openTelegramLink(url)
    } else {
      window.open(url, '_blank')
    }
  }, [tg])

  return {
    tg,
    user,
    initData,
    colorScheme,
    ready,
    close,
    expand,
    showAlert,
    showConfirm,
    hapticFeedback,
    mainButton,
    backButton,
    openLink,
    openTelegramLink,
    isInTelegram: !!tg
  }
}
