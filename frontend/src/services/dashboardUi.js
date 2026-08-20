const listeners = new Set()

export function getApiErrorMessage(error, fallback = 'Something went wrong. Please try again.') {
  const detail = error?.response?.data?.detail ?? error?.detail ?? error

  if (typeof detail === 'string' && detail.trim()) return detail

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => (typeof item === 'string' ? item : item?.msg))
      .filter(Boolean)
    if (messages.length) return messages.join(' ')
  }

  if (detail && typeof detail === 'object' && typeof detail.msg === 'string') {
    return detail.msg
  }

  return fallback
}

export function subscribeDashboardUi(listener) {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

function publish(event) {
  listeners.forEach((listener) => listener(event))
}

export function showToast(message, tone = 'success') {
  publish({ type: 'toast', message, tone })
}

export function confirmDialog({ title, message, confirmLabel = 'Confirm', tone = 'danger' }) {
  return new Promise((resolve) => {
    publish({ type: 'confirm', title, message, confirmLabel, tone, resolve })
  })
}

export function promptDialog({ title, message, defaultValue = '', confirmLabel = 'Continue' }) {
  return new Promise((resolve) => {
    publish({ type: 'prompt', title, message, defaultValue, confirmLabel, resolve })
  })
}
