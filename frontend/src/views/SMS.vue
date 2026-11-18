<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from 'vue'

type InputMode = 'text' | 'screenshot'

const mode = ref<InputMode>('text')
const message = ref('')
const selectedFile = ref<File | null>(null)
const mobile_number = ref('')
const country_code = ref('+91')
const previewUrl = ref('')
const extractedText = ref('')
const isExtracting = ref(false)
const isAnalyzing = ref(false)
const error = ref('')
const result = ref<any>(null)
const fileInput = ref<HTMLInputElement | null>(null)

const canAnalyze = computed(() => {
  return message.value.trim().length > 0 && !isAnalyzing.value
})

function clearResult() {
  result.value = null
  error.value = ''
}

function changeMode(newMode: InputMode) {
  mode.value = newMode
  error.value = ''
  result.value = null
}

function selectFile(file?: File) {
  if (!file) return

  error.value = ''
  result.value = null
  extractedText.value = ''

  if (!['image/png', 'image/jpeg', 'image/webp'].includes(file.type)) {
    error.value = 'Please upload a PNG, JPG or WEBP image.'
    return
  }

  if (file.size > 10 * 1024 * 1024) {
    error.value = 'Image size must be less than 10 MB.'
    return
  }

  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }

  selectedFile.value = file
  previewUrl.value = URL.createObjectURL(file)
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  selectFile(target.files?.[0])
}

function handleDrop(event: DragEvent) {
  selectFile(event.dataTransfer?.files?.[0])
}

function removeImage() {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }

  previewUrl.value = ''
  selectedFile.value = null
  extractedText.value = ''

  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

async function extractText() {
  if (!selectedFile.value) return

  isExtracting.value = true
  error.value = ''

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    // Reuses the existing OCR endpoint because screenshot text extraction
    // is channel-independent. Change this only if you create /api/sms/extract.
    const response = await fetch(
      'http://localhost:8000/api/whatsapp/extract',
      {
        method: 'POST',
        body: formData,
      }
    )

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Unable to extract text from screenshot.')
    }

    extractedText.value = data.extracted_text || ''
    message.value = extractedText.value

    if (!extractedText.value) {
      error.value = 'No readable text was found. Try another screenshot.'
    }
  } catch (err) {
    error.value =
      err instanceof Error ? err.message : 'OCR extraction failed.'
  } finally {
    isExtracting.value = false
  }
}

async function analyzeMessage() {
  if (!message.value.trim()) {
    error.value = 'Please enter or extract an SMS message.'
    return
  }

  isAnalyzing.value = true
  error.value = ''
  result.value = null

  try {
    const response = await fetch(
      'http://localhost:8000/api/sms/analyze',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message.value.trim(),
          mobile_number: mobile_number.value.trim(),
          country_code: country_code.value,
          source: 'sms',
        }),
      }
    )

    const data = await response.json()

    if (!response.ok || data.success === false) {
      throw new Error(data.error || 'SMS analysis failed.')
    }

    // Supports either the same flattened response as WhatsApp
    // or an API response wrapped as { success: true, report: {...} }.
    result.value = data.report ?? data
  } catch (err) {
    error.value =
      err instanceof Error
        ? err.message
        : 'Unable to connect to the Python backend.'
  } finally {
    isAnalyzing.value = false
  }
}

onBeforeUnmount(() => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
})
</script>

<template>
  <div class="min-h-screen bg-[#08111f] px-6 py-8 text-slate-200">
    <div class="mx-auto max-w-6xl">

      <!-- Page Header -->
      <div class="mb-8 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div class="mb-2 flex items-center gap-2 text-sm text-cyan-400">
            <span class="h-2 w-2 rounded-full bg-cyan-400"></span>
            CHANNEL ANALYSIS / SMS
          </div>

          <h1 class="text-3xl font-bold tracking-tight text-white">
            SMS Intelligence
          </h1>

          <p class="mt-2 text-sm text-slate-400">
            Analyze suspicious SMS messages using AI-powered threat detection.
          </p>
        </div>

        <div class="flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-4 py-2 text-xs font-semibold text-emerald-400">
          <span class="h-2 w-2 rounded-full bg-emerald-400"></span>
          ANALYSIS MODULE
        </div>
      </div>

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">

        <!-- Main Input Section -->
        <div class="space-y-6 lg:col-span-2">
          <div class="rounded-2xl border border-slate-800 bg-[#101d2d] p-6">

            <div class="mb-6">
              <h2 class="text-lg font-semibold text-white">
                SMS Investigation
              </h2>
              <p class="mt-1 text-xs text-slate-400">
                Enter the sender details and choose how you want to provide the SMS.
              </p>
            </div>

            <!-- SMS Sender Details -->
            <div class="mb-6 grid grid-cols-1 gap-5 md:grid-cols-2">

              <div>
                <label class="mb-2 block text-sm font-medium text-slate-300">
                  Country Code
                </label>

                <select
                  v-model="country_code"
                  @change="clearResult"
                  class="w-full rounded-xl border border-slate-700 bg-[#091422] p-3 text-sm text-white outline-none focus:border-cyan-400"
                >
                  <option value="+91">India (+91)</option>
                  <option value="+1">USA (+1)</option>
                  <option value="+44">UK (+44)</option>
                  <option value="+971">UAE (+971)</option>
                  <option value="+61">Australia (+61)</option>
                </select>
              </div>

              <div>
                <label class="mb-2 block text-sm font-medium text-slate-300">
                  Sender Mobile Number
                </label>

                <input
                  v-model="mobile_number"
                  @input="clearResult"
                  type="tel"
                  inputmode="tel"
                  autocomplete="off"
                  placeholder="Enter sender mobile number"
                  class="w-full rounded-xl border border-slate-700 bg-[#091422] p-3 text-sm text-white outline-none focus:border-cyan-400"
                />
              </div>
            </div>

            <!-- Input Mode Selector -->
            <div class="mb-6 grid grid-cols-2 gap-3">

              <button
                @click="changeMode('text')"
                class="flex items-center gap-3 rounded-xl border p-4 text-left transition"
                :class="mode === 'text'
                  ? 'border-cyan-400 bg-cyan-400/10'
                  : 'border-slate-700 bg-[#0b1625] hover:border-slate-500'"
              >
                <div class="rounded-lg bg-cyan-400/10 p-2">
                  <svg class="h-6 w-6 text-cyan-400" fill="none"
                    stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round"
                      stroke-width="1.8"
                      d="M8 10h8M8 14h5m-8 6l-2 1v-4a8 8 0 1116 0v3a2 2 0 01-2 2H5z"/>
                  </svg>
                </div>

                <div>
                  <p class="text-sm font-semibold text-white">
                    Paste SMS
                  </p>
                  <p class="mt-1 text-xs text-slate-400">
                    Manual text input
                  </p>
                </div>
              </button>

              <button
                @click="changeMode('screenshot')"
                class="flex items-center gap-3 rounded-xl border p-4 text-left transition"
                :class="mode === 'screenshot'
                  ? 'border-cyan-400 bg-cyan-400/10'
                  : 'border-slate-700 bg-[#0b1625] hover:border-slate-500'"
              >
                <div class="rounded-lg bg-cyan-400/10 p-2">
                  <svg class="h-6 w-6 text-cyan-400" fill="none"
                    stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round"
                      stroke-width="1.8"
                      d="M3 7a2 2 0 012-2h3l2-2h4l2 2h3a2 2 0 012 2v11a2 2 0 01-2 2H5a2 2 0 01-2-2V7z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                </div>

                <div>
                  <p class="text-sm font-semibold text-white">
                    Upload Screenshot
                  </p>
                  <p class="mt-1 text-xs text-slate-400">
                    OCR text extraction
                  </p>
                </div>
              </button>
            </div>

            <!-- Text Input -->
            <div v-if="mode === 'text'" class="space-y-3">
              <label class="text-sm font-medium text-slate-300">
                SMS Message Content
              </label>

              <textarea
                v-model="message"
                @input="clearResult"
                rows="9"
                maxlength="10000"
                placeholder="Paste the SMS message you want to investigate..."
                class="w-full resize-y rounded-xl border border-slate-700 bg-[#091422] p-4 text-sm leading-6 text-slate-200 outline-none transition placeholder:text-slate-600 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/10"
              ></textarea>

              <div class="flex justify-between text-xs text-slate-500">
                <span>Enter the complete SMS for better analysis.</span>
                <span>{{ message.length }}/10000</span>
              </div>
            </div>

            <!-- Screenshot Input -->
            <div v-else class="space-y-4">
              <label class="text-sm font-medium text-slate-300">
                Upload SMS Screenshot
              </label>

              <div
                @dragover.prevent
                @drop.prevent="handleDrop"
                @click="!selectedFile && fileInput?.click()"
                class="cursor-pointer rounded-xl border-2 border-dashed border-slate-700 bg-[#091422] p-8 text-center transition hover:border-cyan-400/60 hover:bg-cyan-400/5"
              >
                <input
                  ref="fileInput"
                  type="file"
                  accept=".png,.jpg,.jpeg,.webp,image/png,image/jpeg,image/webp"
                  class="hidden"
                  @change="handleFileChange"
                />

                <div v-if="!selectedFile">
                  <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-cyan-400/10">
                    <svg class="h-7 w-7 text-cyan-400" fill="none"
                      stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round"
                        stroke-width="1.8"
                        d="M12 16V4m0 0L7 9m5-5l5 5M4 16v3a1 1 0 001 1h14a1 1 0 001-1v-3"/>
                    </svg>
                  </div>

                  <p class="font-semibold text-white">
                    Click to upload or drag and drop
                  </p>

                  <p class="mt-2 text-xs text-slate-500">
                    PNG, JPG or WEBP · Maximum 10 MB
                  </p>
                </div>

                <div v-else class="space-y-3">
                  <img
                    :src="previewUrl"
                    alt="SMS screenshot preview"
                    class="mx-auto max-h-72 rounded-lg border border-slate-700 object-contain"
                  />

                  <p class="text-sm font-medium text-white">
                    {{ selectedFile.name }}
                  </p>

                  <p class="text-xs text-slate-400">
                    {{ (selectedFile.size / 1024 / 1024).toFixed(2) }} MB
                  </p>

                  <button
                    @click.stop="removeImage"
                    class="text-xs font-semibold text-rose-400 hover:text-rose-300"
                  >
                    Remove screenshot
                  </button>
                </div>
              </div>

              <button
                v-if="selectedFile"
                @click="extractText"
                :disabled="isExtracting"
                class="flex w-full items-center justify-center gap-2 rounded-xl border border-cyan-400/30 bg-cyan-400/10 py-3 text-sm font-semibold text-cyan-400 transition hover:bg-cyan-400/20 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <svg v-if="isExtracting" class="h-5 w-5 animate-spin"
                  fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10"
                    stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor"
                    d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
                </svg>

                {{ isExtracting ? 'Extracting Text...' : 'Extract Text Using OCR' }}
              </button>

              <!-- OCR Result -->
              <div v-if="extractedText" class="space-y-3">
                <div class="flex items-center justify-between">
                  <label class="text-sm font-semibold text-white">
                    Extracted Text
                  </label>

                  <span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs text-emerald-400">
                    OCR Complete
                  </span>
                </div>

                <textarea
                  v-model="message"
                  @input="clearResult"
                  rows="7"
                  maxlength="10000"
                  class="w-full rounded-xl border border-slate-700 bg-[#091422] p-4 text-sm leading-6 text-slate-200 outline-none focus:border-cyan-400"
                ></textarea>

                <p class="text-xs text-slate-500">
                  Verify and correct the extracted text before analysis.
                </p>
              </div>
            </div>

            <!-- Error -->
            <div
              v-if="error"
              class="mt-5 rounded-xl border border-rose-500/20 bg-rose-500/10 p-3 text-sm text-rose-400"
              role="alert"
            >
              {{ error }}
            </div>

            <!-- Analyze Button -->
            <button
              @click="analyzeMessage"
              :disabled="!canAnalyze"
              class="mt-6 flex w-full items-center justify-center gap-3 rounded-xl bg-cyan-400 py-4 text-sm font-bold text-[#08111f] shadow-lg shadow-cyan-400/10 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <svg v-if="isAnalyzing" class="h-5 w-5 animate-spin"
                fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10"
                  stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
              </svg>

              {{ isAnalyzing ? 'Analyzing SMS...' : 'Analyze SMS Message' }}
            </button>
          </div>
        </div>

        <!-- Right Side Information -->
        <div class="space-y-6">
          <div class="rounded-2xl border border-slate-800 bg-[#101d2d] p-5">
            <h3 class="font-semibold text-white">
              Analysis Overview
            </h3>

            <p class="mt-2 text-xs leading-5 text-slate-400">
              Your SMS will be examined by the AI detection engine and available cybersecurity intelligence sources.
            </p>

            <div class="mt-5 space-y-4">
              <div class="flex items-center gap-3">
                <div class="rounded-lg bg-cyan-400/10 p-2 text-cyan-400">
                  <span class="text-sm">01</span>
                </div>
                <div>
                  <p class="text-sm font-medium text-white">Text Analysis</p>
                  <p class="text-xs text-slate-500">Message classification</p>
                </div>
              </div>

              <div class="flex items-center gap-3">
                <div class="rounded-lg bg-cyan-400/10 p-2 text-cyan-400">
                  <span class="text-sm">02</span>
                </div>
                <div>
                  <p class="text-sm font-medium text-white">Threat Intelligence</p>
                  <p class="text-xs text-slate-500">Available indicators lookup</p>
                </div>
              </div>

              <div class="flex items-center gap-3">
                <div class="rounded-lg bg-cyan-400/10 p-2 text-cyan-400">
                  <span class="text-sm">03</span>
                </div>
                <div>
                  <p class="text-sm font-medium text-white">Risk Assessment</p>
                  <p class="text-xs text-slate-500">Explainable risk score</p>
                </div>
              </div>
            </div>
          </div>

          <div class="rounded-2xl border border-cyan-400/20 bg-cyan-400/5 p-5">
            <div class="mb-3 flex items-center gap-2 text-cyan-400">
              <span>ⓘ</span>
              <h3 class="text-sm font-semibold">Privacy Notice</h3>
            </div>

            <p class="text-xs leading-6 text-slate-400">
              SMS screenshots and sender details may contain personal information. Upload only content you are authorized to analyze. Do not use real OTPs, PINs or passwords as test data.
            </p>
          </div>
        </div>
      </div>

      <!-- Threat Analysis Report -->
      <div
        v-if="result"
        class="mt-6 space-y-6 rounded-2xl border border-slate-800 bg-[#101d2d] p-6"
      >
        <!-- Report Header -->
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 class="text-xl font-bold text-white">
              SMS Threat Analysis Report
            </h2>
            <p class="mt-1 text-xs text-slate-400">
              AI/ML and Cybersecurity Engine Assessment
            </p>
          </div>

          <span
            class="rounded-full px-4 py-2 text-xs font-bold"
            :class="result.verdict === 'High Risk'
              ? 'bg-rose-500/10 text-rose-400'
              : result.verdict === 'Medium Risk'
                ? 'bg-amber-500/10 text-amber-400'
                : 'bg-emerald-500/10 text-emerald-400'"
          >
            {{ result.verdict || 'Assessment returned' }}
          </span>
        </div>

        <!-- Final Threat Score -->
        <div class="rounded-2xl border border-cyan-400/20 bg-cyan-400/5 p-6">
          <p class="text-sm text-slate-400">
            Overall Threat Percentage
          </p>

          <div class="mt-2 flex items-end gap-2">
            <span class="text-5xl font-bold text-cyan-400">
              {{ result.threat_percentage ?? 'N/A' }}<span v-if="result.threat_percentage !== undefined">%</span>
            </span>
            <span class="mb-2 text-xs text-slate-500">
              Estimated threat score
            </span>
          </div>

          <div class="mt-5 h-3 overflow-hidden rounded-full bg-slate-800">
            <div
              class="h-full rounded-full bg-cyan-400 transition-all duration-700"
              :style="{
                width: `${Math.min(100, Math.max(0, Number(result.threat_percentage) || 0))}%`
              }"
            ></div>
          </div>

          <p class="mt-3 text-xs text-slate-400">
            Calculation: 50% AI/ML + 50% Cybersecurity
          </p>
        </div>

        <!-- Individual Engine Scores -->
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">

          <!-- AI/ML -->
          <div class="rounded-xl border border-cyan-400/20 bg-[#091422] p-5">
            <div class="flex items-center justify-between">
              <h3 class="font-semibold text-cyan-400">
                AI/ML Engine
              </h3>
              <span class="text-xs text-slate-500">50% Weight</span>
            </div>

            <p class="mt-4 text-3xl font-bold text-white">
              {{ result.engine_scores?.aiml_threat_score ?? 'N/A' }}<span v-if="result.engine_scores?.aiml_threat_score !== undefined">%</span>
            </p>

            <div class="mt-3 h-2 overflow-hidden rounded-full bg-slate-800">
              <div
                class="h-full rounded-full bg-cyan-400"
                :style="{
                  width: `${Math.min(100, Math.max(0, Number(result.engine_scores?.aiml_threat_score) || 0))}%`
                }"
              ></div>
            </div>

            <div class="mt-5 space-y-2 text-sm">
              <p class="text-slate-400">
                Prediction:
                <span class="font-semibold text-white">
                  {{ result.aiml_engine?.prediction ?? 'N/A' }}
                </span>
              </p>

              <p class="text-slate-400">
                Selected Model:
                <span class="text-white">
                  {{ result.aiml_engine?.selected_model ?? 'N/A' }}
                </span>
              </p>
            </div>

            <div class="mt-5">
              <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Why AI/ML flagged this message
              </p>

              <ul
                v-if="result.aiml_engine?.reasons?.length"
                class="space-y-2"
              >
                <li
                  v-for="(reason, index) in result.aiml_engine.reasons"
                  :key="index"
                  class="rounded-lg bg-slate-800/60 p-3 text-xs leading-5 text-slate-300"
                >
                  {{ reason }}
                </li>
              </ul>

              <p v-else class="text-xs text-slate-500">
                No AI/ML explanation was returned.
              </p>
            </div>
          </div>

          <!-- Cybersecurity -->
          <div class="rounded-xl border border-emerald-400/20 bg-[#091422] p-5">
            <div class="flex items-center justify-between">
              <h3 class="font-semibold text-emerald-400">
                Cybersecurity Engine
              </h3>
              <span class="text-xs text-slate-500">50% Weight</span>
            </div>

            <p class="mt-4 text-3xl font-bold text-white">
              {{ result.engine_scores?.cybersecurity_threat_score ?? 'N/A' }}<span v-if="result.engine_scores?.cybersecurity_threat_score !== undefined">%</span>
            </p>

            <div class="mt-3 h-2 overflow-hidden rounded-full bg-slate-800">
              <div
                class="h-full rounded-full bg-emerald-400"
                :style="{
                  width: `${Math.min(100, Math.max(0, Number(result.engine_scores?.cybersecurity_threat_score) || 0))}%`
                }"
              ></div>
            </div>

            <div class="mt-5 space-y-2 text-sm">
              <p class="text-slate-400">
                Rule Score:
                <span class="text-white">
                  {{ result.cybersecurity_engine?.rule_score ?? 'N/A' }}<span v-if="result.cybersecurity_engine?.rule_score !== undefined">%</span>
                </span>
              </p>

              <p class="text-slate-400">
                Unusual Message:
                <span class="text-white">
                  {{ result.cybersecurity_engine?.anomaly?.is_unusual === undefined ? 'N/A' : result.cybersecurity_engine.anomaly.is_unusual ? 'Yes' : 'No' }}
                </span>
              </p>
            </div>

            <div class="mt-5">
              <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Why Cybersecurity flagged this message
              </p>

              <ul
                v-if="result.cybersecurity_engine?.reasons?.length"
                class="space-y-2"
              >
                <li
                  v-for="(reason, index) in result.cybersecurity_engine.reasons"
                  :key="index"
                  class="rounded-lg bg-slate-800/60 p-3 text-xs leading-5 text-slate-300"
                >
                  {{ reason }}
                </li>
              </ul>

              <p v-else class="text-xs text-slate-500">
                No configured cybersecurity rule was triggered.
              </p>
            </div>
          </div>
        </div>

        <!-- Detailed Security Findings -->
        <div class="rounded-xl border border-slate-800 bg-[#091422] p-5">
          <h3 class="font-semibold text-white">
            Detected Security Indicators
          </h3>

          <div
            v-if="result.cybersecurity_engine?.findings?.length"
            class="mt-4 space-y-3"
          >
            <div
              v-for="(finding, index) in result.cybersecurity_engine.findings"
              :key="index"
              class="flex items-start justify-between gap-4 rounded-lg border border-slate-800 bg-[#101d2d] p-3"
            >
              <div>
                <p class="text-sm font-medium text-white">
                  {{ (finding.indicator || 'Security indicator').replaceAll('_', ' ') }}
                </p>
                <p class="mt-1 text-xs text-slate-400">
                  {{ finding.reason }}
                </p>
              </div>

              <span class="shrink-0 text-xs font-semibold text-amber-400">
                +{{ finding.points }} points
              </span>
            </div>
          </div>

          <p v-else class="mt-3 text-sm text-slate-500">
            No rule-based security indicators detected.
          </p>
        </div>

        <!-- Anomaly Information -->
        <div class="rounded-xl border border-slate-800 bg-[#091422] p-5">
          <h3 class="font-semibold text-white">
            Anomaly Detection
          </h3>

          <p class="mt-3 text-sm text-slate-300">
            {{ result.cybersecurity_engine?.anomaly?.explanation ?? 'No anomaly information returned.' }}
          </p>

          <p class="mt-2 text-xs text-slate-500">
            Unusual messages are not automatically malicious.
          </p>
        </div>

        <!-- Recommended Actions -->
        <div class="rounded-xl border border-amber-400/20 bg-amber-400/5 p-5">
          <h3 class="font-semibold text-amber-400">
            Recommended Actions
          </h3>

          <ul
            v-if="result.recommended_actions?.length"
            class="mt-3 space-y-2"
          >
            <li
              v-for="(action, index) in result.recommended_actions"
              :key="index"
              class="flex gap-2 text-sm text-slate-300"
            >
              <span class="text-amber-400">•</span>
              {{ action }}
            </li>
          </ul>

          <p v-else class="mt-3 text-sm text-slate-400">
            No recommended actions were returned.
          </p>
        </div>

        <!-- Disclaimer -->
        <p v-if="result.disclaimer" class="text-xs leading-5 text-slate-500">
          {{ result.disclaimer }}
        </p>
      </div>
    </div>
  </div>
</template>
