import { useAuthContext } from '../context/AuthContext'

export const useAuth = () => {
  // Directly consumes the safe context hook wrapper we created
  const context = useAuthContext()
  
  return context
}