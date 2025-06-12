<template>
  <div class="device-data">
    <h2>设备传感器数据</h2>

    <el-alert
      v-if="error"
      title="错误"
      type="error"
      :description="error"
      show-icon
      class="mb-4"
    />

    <el-table
      v-if="deviceData.length"
      :data="deviceData"
      style="width: 100%"
      :loading="loading"
      height="300"
      row-key="identifier"
    >
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="identifier" label="标识符" />
      <el-table-column prop="value" label="数值" />
    </el-table>

    <div v-else-if="!loading">暂无数据</div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { ElMessageBox, ElMessage } from 'element-plus'

// 类型定义
interface DeviceItem {
  identifier: string
  name: string
  value: string | number
}

// 响应式数据
const deviceData = ref<DeviceItem[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
let timerId: number | undefined
let alertAcknowledged = true // 是否已确认上一轮报警

// 阈值配置（可根据实际情况修改）
const thresholdMap: Record<string, number> = {
  temperature: 50,
  light: 800,
  co2: 4000,
  pm25: 400,
}

// 报警音频
const alertAudio = new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg')

// 保存上一次报警的超限数据的快照，格式为 JSON 字符串，方便比较
let lastAlertSnapshot = ''

// 判断是否可报警（必须确认过弹窗）
function shouldAlert(): boolean {
  return alertAcknowledged
}

// 比较两个报警内容是否相同
function isSameAlert(currentItems: DeviceItem[]): boolean {
  // 先把当前报警项根据 identifier 排序，转成字符串
  const sortedCurrent = currentItems
    .map(i => ({ id: i.identifier, val: i.value }))
    .sort((a, b) => a.id.localeCompare(b.id))
  const currentStr = JSON.stringify(sortedCurrent)
  return currentStr === lastAlertSnapshot
}

// 平滑更新数据
function updateDeviceData(newData: DeviceItem[]) {
  newData.forEach((newItem) => {
    const existing = deviceData.value.find((d) => d.identifier === newItem.identifier)
    if (existing) {
      existing.value = newItem.value
    } else {
      deviceData.value.push({ ...newItem })
    }
  })
}

// 获取数据 + 报警检测
async function fetchData() {
  loading.value = true
  error.value = null

  try {
    const res = await axios.get<{ code: number; data: DeviceItem[]; msg?: string }>(
      'http://47.122.81.245:5000/api/device-data'
    )

    if (res.data.code === 0) {
      updateDeviceData(res.data.data)

      const alertItems = res.data.data.filter((item) => {
        const val = Number(item.value)
        const threshold = thresholdMap[item.identifier]
        return !isNaN(val) && threshold !== undefined && val > threshold
      })

      if (alertItems.length > 0 && shouldAlert()) {
        // 如果和上次报警内容相同，则不重复报警
        if (isSameAlert(alertItems)) {
          // 不报警，直接跳过
          loading.value = false
          return
        }

        // 记录这次报警内容快照
        const sortedCurrent = alertItems
          .map(i => ({ id: i.identifier, val: i.value }))
          .sort((a, b) => a.id.localeCompare(b.id))
        lastAlertSnapshot = JSON.stringify(sortedCurrent)

        alertAcknowledged = false
        alertAudio.play()

        const names = alertItems
          .map((i) => {
            const threshold = thresholdMap[i.identifier]
            return `${i.name} (${i.identifier}): ${i.value}（阈值 ${threshold}）`
          })
          .join('\n')

        await ElMessageBox.alert(
          `⚠️ 以下传感器数值超过阈值：\n${names}`,
          '报警提醒',
          {
            confirmButtonText: '知道了',
            type: 'warning',
          }
        )

        // 确认后允许下一次报警
        alertAcknowledged = true
      } else if (alertItems.length === 0) {
        // 如果当前无报警，清空快照，避免永远不报警
        lastAlertSnapshot = ''
      }
    } else {
      error.value = res.data.msg || '接口错误'
      ElMessage.error(error.value)
    }
  } catch (err: any) {
    error.value = '请求失败: ' + (err.message || '未知错误')
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

// 生命周期：定时刷新
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
  padding: 20px;
}
.mb-4 {
  margin-bottom: 16px;
}
</style>
