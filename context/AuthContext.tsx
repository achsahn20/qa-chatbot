import {
  createContext,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren,
} from 'react'
import { authService, type AuthResponse, type AuthUser } from '../services/authService'
import { storage } from '../utils/storage'

interface AuthContextValue {
  user: AuthUser | null
  token: string | null
  loading: boolean
  login: (payload: { email: string; password: string }) => Promise<void>
  signup: (payload: { full_name: string; email: string; password: string }) => Promise<void>
  logout: () => void
  refreshProfile: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)

const applyAuthResponse = (
  response: AuthResponse,
  setUser: (user: AuthUser | null) => void,
  setToken: (token: string | null) => void,
) => {
  storage.setToken(response.access_token)
  storage.setUser(response.user)
  setUser(response.user)
  setToken(response.access_token)
}

export const AuthProvider = ({ children }: PropsWithChildren) => {
  const [user, setUser] = useState<AuthUser | null>(storage.getUser())
  const [token, setToken] = useState<string | null>(storage.getToken())
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const hydrate = async () => {
      if (!storage.getToken()) {
        setLoading(false)
        return
      }

      try {
        const profile = await authService.me()
        storage.setUser(profile)
        setUser(profile)
      } catch {
        storage.clearAll()
        setUser(null)
        setToken(null)
      } finally {
        setLoading(false)
      }
    }

    void hydrate()
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      loading,
      login: async (payload) => {
        const response = await authService.login(payload)
        applyAuthResponse(response, setUser, setToken)
      },
      signup: async (payload) => {
        const response = await authService.signup(payload)
        applyAuthResponse(response, setUser, setToken)
      },
      logout: () => {
        storage.clearAll()
        setUser(null)
        setToken(null)
      },
      refreshProfile: async () => {
        const profile = await authService.me()
        storage.setUser(profile)
        setUser(profile)
      },
    }),
    [loading, token, user],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
