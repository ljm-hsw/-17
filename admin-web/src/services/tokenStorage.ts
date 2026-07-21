const ACCESS_KEY = 'travelweave.management.access'
const REFRESH_KEY = 'travelweave.management.refresh'

export const tokenStorage = {
  get() {
    return {
      access: sessionStorage.getItem(ACCESS_KEY),
      refresh: sessionStorage.getItem(REFRESH_KEY),
    }
  },
  save(access: string, refresh: string) {
    sessionStorage.setItem(ACCESS_KEY, access)
    sessionStorage.setItem(REFRESH_KEY, refresh)
  },
  saveAccess(access: string) {
    sessionStorage.setItem(ACCESS_KEY, access)
  },
  clear() {
    sessionStorage.removeItem(ACCESS_KEY)
    sessionStorage.removeItem(REFRESH_KEY)
  },
}
