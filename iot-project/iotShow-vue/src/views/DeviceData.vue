<template>
  <div class="device-data">
    <h2 class="title">设备传感器数据</h2>

    <el-alert
      v-if="error"
      title="错误"
      type="error"
      :description="error"
      show-icon
      class="mb-4"
    />

    <el-row :gutter="20">
      <el-col
        v-for="item in deviceData"
        :key="item.identifier"
        :xl="6"
        :lg="6"
        :md="12"
        :sm="24"
        :xs="24"
      >
        <el-card shadow="hover" class="mb-20px sensor-card">
          <div class="card-header">
            <img
              class="sensor-icon"
              :src="getIconByIdentifier(item.identifier)"
              alt="传感器图标"
            />
            <div class="text-content">
              <span class="name">{{ item.name }}</span>
              <span class="identifier">({{ item.identifier }})</span>
            </div>
          </div>
          <div class="value" :class="{ alert: isOverThreshold(item) }">
            {{ item.value }}
          </div>
        </el-card>
      </el-col>
    </el-row>

    <div v-if="!loading && !deviceData.length">暂无数据</div>
  </div>
  <SensorLineChart />
</template>

<script lang="ts" setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { ElMessageBox, ElMessage } from 'element-plus'
import SensorLineChart from '../components/SensorLineChart.vue'


interface DeviceItem {
  identifier: string
  name: string
  value: string | number
}

const deviceData = ref<DeviceItem[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
let timerId: number | undefined
let alertAcknowledged = true
let lastAlertSnapshot = ''

const thresholdMap: Record<string, number> = {
  temperature: 50,
  light: 800,
  co2: 4000,
  pm25: 400,
}

const iconMap: Record<string, string> = {
  temperature:
    'https://cdn-icons-png.flaticon.com/512/1146/1146869.png', // 温度计
  light:
    'https://cdn-icons-png.flaticon.com/512/869/869869.png', // 太阳光
  co2:
    'https://cdn-icons-png.flaticon.com/512/414/414927.png', // CO2分子
  pm25:
    'https://cdn-icons-png.flaticon.com/512/1163/1163624.png', // 粉尘颗粒
}

const alertAudio = new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg')

function shouldAlert(): boolean {
  return alertAcknowledged
}

function isSameAlert(currentItems: DeviceItem[]): boolean {
  const sorted = currentItems.map(i => ({ id: i.identifier, val: i.value })).sort((a, b) => a.id.localeCompare(b.id))
  return JSON.stringify(sorted) === lastAlertSnapshot
}

function updateDeviceData(newData: DeviceItem[]) {
  newData.forEach((newItem) => {
    const existing = deviceData.value.find(d => d.identifier === newItem.identifier)
    if (existing) {
      existing.value = newItem.value
    } else {
      deviceData.value.push({ ...newItem })
    }
  })
}

function isOverThreshold(item: DeviceItem): boolean {
  const val = Number(item.value)
  const threshold = thresholdMap[item.identifier]
  return !isNaN(val) && threshold !== undefined && val > threshold
}

function getIconByIdentifier(id: string): string {
  return iconMap[id] || 'https://cdn-icons-png.flaticon.com/512/709/709496.png' // 默认图标
}

async function fetchData() {
  loading.value = true
  error.value = null

  try {
    const res = await axios.get<{ code: number; data: DeviceItem[]; msg?: string }>(
      'http://47.122.81.245:5050/api/device-data'
    )

    if (res.data.code === 0) {
      updateDeviceData(res.data.data)

      const alertItems = res.data.data.filter(isOverThreshold)

      if (alertItems.length > 0 && shouldAlert() && !isSameAlert(alertItems)) {
        const sorted = alertItems.map(i => ({ id: i.identifier, val: i.value })).sort((a, b) => a.id.localeCompare(b.id))
        lastAlertSnapshot = JSON.stringify(sorted)

        alertAcknowledged = false
        alertAudio.play()

        const msg = alertItems
          .map(i => `${i.name} (${i.identifier}): ${i.value}（阈值 ${thresholdMap[i.identifier]}）`)
          .join('\n')

        await ElMessageBox.alert(`⚠️ 以下传感器数值超过阈值：\n${msg}`, '报警提醒', {
          confirmButtonText: '知道了',
          type: 'warning',
        })


      } else if (alertItems.length === 0) {
        lastAlertSnapshot = ''
      }
    } else {
      error.value = res.data.msg || '接口错误'
      ElMessage.error(error.value)
    }
  }  finally {
    loading.value = false
    alertAcknowledged = true
  }
}

onMounted(() => {
  fetchData()
  timerId = window.setInterval(fetchData, 10000)
})
onUnmounted(() => {
  if (timerId) clearInterval(timerId)
})
</script>

<style scoped>
.device-data {
   background-color: #f0f2f5; /* 浅灰蓝色，推荐页面背景色 */
  padding: 20px;
}

.title {
  text-align: center;
  margin-bottom: 24px;
  font-weight: 700;
  font-size: 24px;
  color: #333;
}

.mb-4 {
  margin-bottom: 16px;
}
.mb-20px {
  margin-bottom: 20px;
}

.sensor-card .card-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.sensor-icon {
  width: 40px;
  height: 40px;
  margin-right: 12px;
}

.text-content {
  display: flex;
  flex-direction: column;
}

.sensor-card .name {
  font-size: 16px;
  font-weight: bold;
}

.sensor-card .identifier {
  font-size: 12px;
  color: #888;
  margin-top: 4px;
}

.sensor-card .value {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
  text-align: center;
}

.sensor-card .value.alert {
  color: #F56C6C;
}
</style>
