import { describe, expect, it } from 'vitest'
import { selectPoseChallenge } from '../checkin-success'

describe('selectPoseChallenge', () => {
  it('uses the supplied random value to select a pose', () => {
    expect(selectPoseChallenge(0).id).toBe('victory')
    expect(selectPoseChallenge(0.5).id).toBe('hands-on-hips')
    expect(selectPoseChallenge(0.999999).id).toBe('arms-crossed')
  })

  it('supports a fixed development pose', () => {
    expect(selectPoseChallenge(0, 'arms-crossed').id).toBe('arms-crossed')
  })
})
