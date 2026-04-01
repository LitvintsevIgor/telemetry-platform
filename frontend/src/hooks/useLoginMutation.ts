import { useMutation } from '@tanstack/react-query'
import { postLogin, type LoginPayload } from '../api/login'

export function useLoginMutation() {
  return useMutation({
    mutationFn: (body: LoginPayload) => postLogin(body),
  })
}
