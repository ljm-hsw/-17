<script setup lang="ts">
import type { WelcomeAgreementType, WelcomePageData } from '../../types/welcome'

defineProps<{
  data: WelcomePageData
  agreed: boolean
  binding: boolean
}>()

defineEmits<{
  toggleConsent: []
  bind: []
  browse: []
  agreement: [type: WelcomeAgreementType]
}>()
</script>

<template>
  <view class="binding-card">
    <view class="binding-card__welcome">
      <text class="binding-card__title">{{ data.title }}</text>
      <view class="binding-card__description">
        <text v-for="line in data.description" :key="line" class="binding-card__description-line">
          {{ line }}
        </text>
      </view>
    </view>

    <view class="binding-card__divider" />

    <view class="binding-card__user">
      <image
        class="binding-card__avatar"
        :src="data.user.avatar"
        :alt="`${data.user.nickname}演示头像`"
        mode="aspectFill"
      />
      <view class="binding-card__user-copy">
        <text class="binding-card__nickname">{{ data.user.nickname }}</text>
        <text class="binding-card__account-label">{{ data.user.accountLabel }}</text>
      </view>
      <image
        class="binding-card__verified"
        :src="data.user.verifiedIcon"
        alt="演示验证状态"
        mode="aspectFit"
      />
    </view>

    <text class="binding-card__mock-disclosure">{{ data.mockDisclosure }}</text>

    <view class="binding-card__divider" />

    <view class="binding-card__actions">
      <view
        class="binding-card__button binding-card__button--primary"
        :class="{ 'binding-card__button--disabled': binding }"
        hover-class="binding-card__button--pressed"
        @tap="$emit('bind')"
      >
        <text>{{ binding ? '演示绑定中…' : '微信一键绑定' }}</text>
      </view>
      <view
        class="binding-card__button binding-card__button--secondary"
        hover-class="binding-card__button--pressed"
        @tap="$emit('browse')"
      >
        <text>暂不绑定，先浏览</text>
      </view>
    </view>

    <view class="binding-card__consent">
      <view
        class="binding-card__checkbox"
        :class="{ 'binding-card__checkbox--empty': !agreed }"
        @tap="$emit('toggleConsent')"
      >
        <image
          v-if="agreed"
          class="binding-card__checkbox-icon"
          :src="data.consentCheckedIcon"
          alt="已同意"
          mode="aspectFit"
        />
      </view>
      <view class="binding-card__agreement-copy">
        <text>我已阅读并同意</text>
        <text class="binding-card__agreement-link" @tap.stop="$emit('agreement', 'user')">
          《用户协议》
        </text>
        <text>和</text>
        <text class="binding-card__agreement-link" @tap.stop="$emit('agreement', 'privacy')">
          《隐私政策》
        </text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.binding-card {
  box-sizing: border-box;
  display: flex;
  width: 610rpx;
  min-height: 930rpx;
  flex-direction: column;
  padding: 44rpx 53rpx 33rpx;
  border-radius: 50rpx;
  background: #fffefc;
  box-shadow: 0 11rpx 31rpx rgba(122, 107, 87, 0.18);
}

.binding-card__welcome {
  display: flex;
  align-items: center;
  flex-direction: column;
  min-height: 208rpx;
  text-align: center;
}

.binding-card__title {
  color: #171816;
  font-size: 44rpx;
  font-weight: 700;
  line-height: 75rpx;
}

.binding-card__description {
  display: flex;
  flex-direction: column;
  margin-top: 9rpx;
}

.binding-card__description-line {
  color: #585550;
  font-size: 31rpx;
  font-weight: 400;
  line-height: 55rpx;
}

.binding-card__divider {
  flex: none;
  width: 100%;
  height: 2rpx;
  background: #efeae4;
}

.binding-card__user {
  display: flex;
  align-items: center;
  min-height: 196rpx;
}

.binding-card__avatar {
  flex: none;
  width: 127rpx;
  height: 127rpx;
  overflow: hidden;
  border-radius: 50%;
}

.binding-card__user-copy {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
  justify-content: center;
  margin-left: 22rpx;
}

.binding-card__nickname {
  color: #292825;
  font-size: 37rpx;
  font-weight: 700;
  line-height: 66rpx;
  white-space: nowrap;
}

.binding-card__account-label {
  color: #8e8a84;
  font-size: 22rpx;
  font-weight: 400;
  line-height: 44rpx;
  white-space: nowrap;
}

.binding-card__verified {
  flex: none;
  width: 48rpx;
  height: 48rpx;
  margin-left: 13rpx;
}

.binding-card__mock-disclosure {
  display: block;
  margin: -13rpx 0 20rpx;
  color: #9a958e;
  font-size: 20rpx;
  line-height: 33rpx;
  text-align: center;
}

.binding-card__actions {
  display: flex;
  flex-direction: column;
  gap: 31rpx;
  padding: 31rpx 0 26rpx;
}

.binding-card__button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 101rpx;
  overflow: hidden;
  border-radius: 51rpx;
  font-size: 33rpx;
  font-weight: 500;
}

.binding-card__button--primary {
  background: #47ac99;
  color: #fff;
}

.binding-card__button--secondary {
  box-sizing: border-box;
  border: 2rpx solid #d8d4ce;
  background: #fffefc;
  color: #3a3936;
}

.binding-card__button--pressed {
  opacity: 0.72;
}

.binding-card__button--disabled {
  opacity: 0.68;
}

.binding-card__consent {
  display: flex;
  align-items: flex-start;
  min-height: 87rpx;
  padding-top: 7rpx;
}

.binding-card__checkbox {
  box-sizing: border-box;
  flex: none;
  width: 37rpx;
  height: 37rpx;
  margin-top: 2rpx;
}

.binding-card__checkbox--empty {
  border: 2rpx solid #47ac99;
  border-radius: 2rpx;
  background: #fffefc;
}

.binding-card__checkbox-icon {
  display: block;
  width: 100%;
  height: 100%;
}

.binding-card__agreement-copy {
  display: flex;
  flex: 1;
  flex-wrap: wrap;
  margin-left: 18rpx;
  color: #78736e;
  font-size: 22rpx;
  font-weight: 400;
  line-height: 35rpx;
}

.binding-card__agreement-link {
  color: #409e87;
}
</style>
