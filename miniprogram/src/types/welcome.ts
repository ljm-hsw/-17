export type WelcomeAgreementType = 'user' | 'privacy'

export interface WelcomeDemoUser {
  readonly nickname: string
  readonly accountLabel: string
  readonly avatar: string
  readonly verifiedIcon: string
}

export interface WelcomePageData {
  readonly heroImage: string
  readonly heroAlt: string
  readonly title: string
  readonly description: readonly string[]
  readonly user: WelcomeDemoUser
  readonly mockDisclosure: string
  readonly consentCheckedIcon: string
  readonly privacyShieldIcon: string
  readonly privacyNotice: string
}
