<script setup lang="ts">
import { ref, computed } from 'vue'

const message = ref('')
const mobile_number = ref('')
const country_code = ref('+91')
const isAnalyzing = ref(false)
const error = ref('')
const result = ref<any>(null)

const canAnalyze = computed(() => {
  return message.value.trim().length > 0 && !isAnalyzing.value
})

function clearResult() {
  result.value = null
  error.value = ''
}

async function analyzeMessage() {
  if (!message.value.trim()) {
    error.value = 'Please enter an SMS message.'
    return
  }

  isAnalyzing.value = true
  error.value = ''
  result.value = null

  try {
    const response = await fetch('http://localhost:8000/api/sms/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message.value.trim(),
        mobile_number: mobile_number.value.trim(),
        country_code: country_code.value,
        source: 'sms',
      }),
    })

    const data = await response.json()
    if (!response.ok || data.success === false) {
      throw new Error(data.error || 'SMS analysis failed.')
    }

    result.value = data.report ?? data
  } catch (err) {
    error.value = err instanceof Error
      ? err.message
      : 'Unable to connect to the Python backend.'
  } finally {
    isAnalyzing.value = false
  }
}
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
                Enter the sender details and paste the SMS message you want to investigate.
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

            <!-- SMS Message Input -->
            <div class="space-y-3">
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
              SMS messages and sender details may contain personal information. Submit only content you are authorized to analyze. Do not enter real OTPs, PINs or passwords as test data.
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
