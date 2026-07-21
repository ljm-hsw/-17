export interface ManagementUser {
  id: string
  username: string
  nickname: string
  is_superuser: boolean
  is_demo: boolean
  permissions: string[]
}

export interface TokenPair {
  access: string
  refresh: string
}

export interface LoginResult extends TokenPair {
  user: ManagementUser
}
