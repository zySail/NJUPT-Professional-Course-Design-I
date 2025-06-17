<template>
  <el-card shadow="hover" class="mb-20px" style="height: 400px;">
    <!-- <el-skeleton :loading="loading" animated :rows="4" style="height: 100%;"> -->
      <div ref="chartRef" style="width: 100%; height: 350px;"></div>
    <!-- </el-skeleton> -->
  </el-card>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

const loading = ref(true)
const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null
let timer: number | null = null  // 定时器句柄
const chartOptions = ref({})

async function fetchData() {
  loading.value = true
  try {
    const res = await axios.get('http://47.122.81.245:5050/api/device-data/history')

    const { times, temp, co2, pm25, light } = res.data
    console.log('接口返回数据:', res.data)
    const timesBeijing = times.map((t: string | number) => {
    const ts = Number(t)  // 转为数字
    const date = new Date(ts)
    return date.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })
    })
    chartOptions.value = {
      title: {
        text: '近10次传感器数据变化',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['温度', 'CO₂', 'PM2.5', '光照'],
        top: 40
      },
      grid: {
        left: 20,
        right: 20,
        bottom: 20,
        top: 80,
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: timesBeijing,
        boundaryGap: false
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '温度',
          type: 'line',
          smooth: true,
          data: temp
        },
        {
          name: 'CO₂',
          type: 'line',
          smooth: true,
          data: co2
        },
        {
          name: 'PM2.5',
          type: 'line',
          smooth: true,
          data: pm25
        },
        {
          name: '光照',
          type: 'line',
          smooth: true,
          data: light
        }
      ]
    }
  } catch (error) {
    console.error('获取图表数据失败', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
  }

  fetchData()

  // ⏱ 每隔30秒自动刷新
  timer = window.setInterval(() => {
    fetchData()
  }, 30000)
})

// 图表更新
watch(chartOptions, (newOptions) => {
  if (chartInstance && newOptions) {
    chartInstance.setOption(newOptions)
  }
}, { deep: true })

// 卸载清理
onUnmounted(() => {
  chartInstance?.dispose()
  if (timer !== null) clearInterval(timer)
})
</script>
