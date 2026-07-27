export const fmtCurrency = (amount, currency = 'USD') => {
  const sym = currency.toUpperCase() === 'USD' ? 'USD' : 'ZiG'
  return `${sym} ${Number(amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

export const fmtPhone = (phone) => {
  if (!phone) return ''
  const digits = phone.replace(/\D/g, '')
  if (digits.startsWith('263')) return `+${digits}`
  if (digits.startsWith('0')) return `+263${digits.slice(1)}`
  return phone
}