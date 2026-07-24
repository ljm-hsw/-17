export type BindingStatus = 'bound' | 'unbound'

export type BindingMethod = 'nfc' | 'manual'

export type BindingOperationStatus = 'idle' | 'binding' | 'success' | 'error'

export type BindingMockScenario = 'success' | 'failure'

export interface BoundProduct {
  productCode: string
  productName: string
  productType: string
  alias: string
  maskedUid: string
  boundAtLabel: string
  lastUsedLabel?: string
  lastSyncLabel: string
  isPrimary: boolean
  isDemo: true
}

export interface BindingFormValue {
  uid: string
}

export interface BindingFormErrors {
  uid?: string
}

export interface BindingPageState {
  status: BindingStatus
  method: BindingMethod
  operationStatus: BindingOperationStatus
  product: BoundProduct
}

export interface BindingPageData {
  readonly initialStatus: BindingStatus
  readonly defaultMethod: BindingMethod
  readonly productImage: string
  readonly productImageAlt: string
  readonly purposes: readonly string[]
  readonly bindingNotes: readonly string[]
  readonly product: Readonly<BoundProduct>
}
