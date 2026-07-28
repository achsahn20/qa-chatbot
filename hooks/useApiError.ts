import axios from 'axios'

export const useApiError = () => {
  return (error: unknown) => {
    if (axios.isAxiosError(error)) {
      return error.response?.data?.detail || error.message
    }
    if (error instanceof Error) {
      return error.message
    }
    return 'Something went wrong.'
  }
}
