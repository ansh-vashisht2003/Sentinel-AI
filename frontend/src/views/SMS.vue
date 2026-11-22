
<script setup lang="ts">
import { ref, computed } from 'vue'

const message = ref('')
const mobile_number = ref('')
const country_code = ref('+91')

const isAnalyzing = ref(false)
const error = ref('')
const result = ref<any>(null)

const API_KEY = import.meta.env.VITE_OPENAI_API_KEY

const canAnalyze = computed(() => {
  return message.value.trim().length > 0 && !isAnalyzing.value
})

function clearResult() {
  result.value = null
  error.value = ''
}

function getRiskColor(verdict: string) {
  const value = verdict?.toLowerCase() || ''

  if (value.includes('critical') || value.includes('high')) {
    return 'bg-rose-500/10 text-rose-400 border-rose-500/20'
  }

  if (value.includes('medium')) {
    return 'bg-amber-500/10 text-amber-400 border-amber-500/20'
  }

  return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
}

function getScoreColor(score: number) {
  if (score >= 75) return 'text-rose-400'
  if (score >= 40) return 'text-amber-400'
  return 'text-emerald-400'
}

function getScoreBarColor(score: number) {
  if (score >= 75) return 'bg-rose-400'
  if (score >= 40) return 'bg-amber-400'
  return 'bg-emerald-400'
}

function normalizeScore(value: unknown) {
  const score = Number(value)
  if (!Number.isFinite(score)) return 0
  return Math.min(100, Math.max(0, score))
}

function normalizeList(value: unknown): string[] {
  if (Array.isArray(value)) {
    return value.map((item) =>
      typeof item === 'string' ? item : JSON.stringify(item)
    )
  }

  if (typeof value === 'string' && value.trim()) {
    return [value]
  }

  return []
}

function pretty(value: unknown) {
  return typeof value === 'string'
    ? value
    : JSON.stringify(value, null, 2)
}

async function analyzeMessage() {
  if (!message.value.trim()) {
    error.value = 'Please enter an SMS message.'
    return
  }

  if (!API_KEY) {
    error.value =
      'API key not found. Please configure VITE_OPENAI_API_KEY in your .env file.'
    return
  }

  isAnalyzing.value = true
  error.value = ''
  result.value = null

  const systemPrompt = `
You are SENTINEL AI, an advanced SMS spam, scam, fraud,
phishing and cybersecurity threat intelligence analyst.

Analyze the provided SMS independently.

You must examine:
- Phishing attempts
- OTP theft
- Banking and payment fraud
- UPI scams
- Impersonation
- Suspicious URLs
- Credential theft
- Urgency and fear tactics
- Rewards and fake prizes
- Threats and blackmail
- Requests for personal information
- Suspicious financial requests
- Social engineering
- Message anomalies
- Sender number context, only when information is available

Do not assume a message is malicious just because it contains a link,
phone number, financial words, or urgent language.

Do not invent sender reputation, phone number lookup results,
URL reputation, investigation history, or external intelligence.

Analyze the actual message content.

Calculate:
1. Overall threat percentage from 0 to 100.
2. AI/ML threat score from 0 to 100.
3. Cybersecurity threat score from 0 to 100.
4. Risk verdict: Low Risk, Medium Risk, High Risk, or Critical Risk.
5. Spam classification: Spam or Not Spam.
6. Detailed reasons behind your classification.
7. Security indicators with points and explanations.
8. Anomaly analysis.
9. Recommended actions.

The overall threat score must be calculated as:
( AI/ML threat score * 0.5 ) +
( Cybersecurity threat score * 0.5 )

Ensure the overall score is consistent with the two engine scores.

Risk levels:
0-24 = Low Risk
25-49 = Medium Risk
50-74 = High Risk
75-100 = Critical Risk

Use evidence from the message. Do not invent evidence.

Return ONLY valid JSON. Do not return markdown or text outside JSON.

Required JSON structure:

{
  "classification": "Spam or Not Spam",
  "is_spam": true,
  "threat_percentage": 0,
  "verdict": "Low Risk",
  "summary": "Short explanation of the analysis",
  "engine_scores": {
    "aiml_threat_score": 0,
    "cybersecurity_threat_score": 0
  },
  "aiml_engine": {
    "prediction": "Spam or Not Spam",
    "reasons": [
      "Reason based on language, context, patterns and intent"
    ]
  },
  "cybersecurity_engine": {
    "rule_score": 0,
    "is_unusual": false,
    "anomaly_explanation": "Explanation",
    "reasons": [
      "Security reason"
    ],
    "findings": [
      {
        "indicator": "Indicator name",
        "reason": "Evidence from the message",
        "points": 0
      }
    ]
  },
  "recommended_actions": [
    "Recommended action"
  ],
  "disclaimer": "Automated AI analysis. Verify suspicious messages independently."
}

Scoring guidelines:
- Scores must be between 0 and 100.
- Low-risk legitimate messages should receive low scores.
- Highly convincing fraud attempts should receive high scores.
- If evidence is weak or inconclusive, explain uncertainty.
- A normal message should not be falsely flagged.
- Do not claim external phone number reputation checks were performed.
- Do not claim external URL checks were performed.
- Do not claim this message was reported by other users.
- Do not invent information.
`

  const userPrompt = `
Analyze this SMS message.

Sender Country Code: ${country_code.value}
Sender Mobile Number: ${mobile_number.value || 'Not provided'}

SMS Message:
${message.value.trim()}

Return the complete JSON threat analysis report.
`

  try {
    const response = await fetch(
`https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key=${API_KEY}`,
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      contents: [
        {
          role: 'user',
          parts: [
            {
              text: `${systemPrompt}\n\n${userPrompt}`,
            },
          ],
        },
      ],
      generationConfig: {
        temperature: 0.2,
        responseMimeType: 'application/json',
      },
    }),
  }
)

const data = await response.json()

if (!response.ok) {
  throw new Error(
    data?.error?.message || 'Gemini AI analysis request failed.'
  )
}

const aiResponse =
  data?.candidates?.[0]?.content?.parts?.[0]?.text

if (!aiResponse) {
  throw new Error('Gemini AI did not return an analysis.')
}

const parsedResult = JSON.parse(aiResponse)
   
    const aiScore = normalizeScore(
      parsedResult.engine_scores?.aiml_threat_score
    )

    const cyberScore = normalizeScore(
      parsedResult.engine_scores?.cybersecurity_threat_score
    )

    // Calculate the final score from the two AI-generated scores.
    const finalScore = Math.round((aiScore + cyberScore) / 2)

    let verdict = 'Low Risk'

    if (finalScore >= 75) {
      verdict = 'Critical Risk'
    } else if (finalScore >= 50) {
      verdict = 'High Risk'
    } else if (finalScore >= 25) {
      verdict = 'Medium Risk'
    }

    result.value = {
      ...parsedResult,

      // Ensure consistent score and risk level.
      threat_percentage: finalScore,
      verdict,

      classification:
        parsedResult.classification ||
        (parsedResult.is_spam ? 'Spam' : 'Not Spam'),

      is_spam:
        typeof parsedResult.is_spam === 'boolean'
          ? parsedResult.is_spam
          : finalScore >= 50,

      engine_scores: {
        aiml_threat_score: aiScore,
        cybersecurity_threat_score: cyberScore,
      },

      aiml_engine: {
        ...parsedResult.aiml_engine,
        reasons: normalizeList(parsedResult.aiml_engine?.reasons),
      },

      cybersecurity_engine: {
        ...parsedResult.cybersecurity_engine,

        rule_score: normalizeScore(
          parsedResult.cybersecurity_engine?.rule_score
        ),

        is_unusual:
          parsedResult.cybersecurity_engine?.is_unusual ?? false,

        anomaly_explanation:
          parsedResult.cybersecurity_engine?.anomaly_explanation || '',

        reasons: normalizeList(
          parsedResult.cybersecurity_engine?.reasons
        ),

        findings: Array.isArray(
          parsedResult.cybersecurity_engine?.findings
        )
          ? parsedResult.cybersecurity_engine.findings
          : [],
      },

      recommended_actions: normalizeList(
        parsedResult.recommended_actions
      ),
    }
  } catch (err) {
    error.value =
      err instanceof Error
        ? err.message
        : 'Unable to analyze the SMS message.'
  } finally {
    isAnalyzing.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#08111f] px-6 py-8 text-slate-200">
    <div class="mx-auto max-w-6xl">

      <!-- HEADER -->
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
            AI-powered spam, fraud and cybersecurity threat detection.
          </p>
        </div>

        <div class="flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-4 py-2 text-xs font-semibold text-emerald-400">
          <span class="h-2 w-2 rounded-full bg-emerald-400"></span>
          AI ANALYSIS ACTIVE
        </div>
      </div>

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">

        <!-- INPUT SECTION -->
        <div class="space-y-6 lg:col-span-2">
          <div class="rounded-2xl border border-slate-800 bg-[#101d2d] p-6">

            <div class="mb-6">
              <h2 class="text-lg font-semibold text-white">
                SMS Investigation
              </h2>

              <p class="mt-1 text-xs text-slate-400">
                Enter sender information and the message to generate
                an AI security report.
              </p>
            </div>

            <!-- SENDER DETAILS -->
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
                  <option value="+1">USA / Canada (+1)</option>
                  <option value="+44">UK (+44)</option>
                  <option value="+971">UAE (+971)</option>
                  <option value="+61">Australia (+61)</option>
                  <option value="+65">Singapore (+65)</option>
                  <option value="+49">Germany (+49)</option>
                  <option value="+33">France (+33)</option>
                  <option value="+81">Japan (+81)</option>
                  <option value="+86">China (+86)</option>
                  <option value="+92">Pakistan (+92)</option>
                  <option value="+880">Bangladesh (+880)</option>
                  <option value="+94">Sri Lanka (+94)</option>
                  <option value="+977">Nepal (+977)</option>
                  <option value="+966">Saudi Arabia (+966)</option>
                  <option value="+7">Russia (+7)</option>
                  <option value="+55">Brazil (+55)</option>
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

            <!-- MESSAGE -->
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
                <span>Complete messages provide better analysis.</span>
                <span>{{ message.length }}/10000</span>
              </div>
            </div>

            <!-- ERROR -->
            <div
              v-if="error"
              class="mt-5 rounded-xl border border-rose-500/20 bg-rose-500/10 p-3 text-sm text-rose-400"
              role="alert"
            >
              {{ error }}
            </div>

            <!-- ANALYZE BUTTON -->
            <button
              @click="analyzeMessage"
              :disabled="!canAnalyze"
              class="mt-6 flex w-full items-center justify-center gap-3 rounded-xl bg-cyan-400 py-4 text-sm font-bold text-[#08111f] shadow-lg shadow-cyan-400/10 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <svg
                v-if="isAnalyzing"
                class="h-5 w-5 animate-spin"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                />

                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                />
              </svg>

              {{ isAnalyzing ? 'AI Investigating Message...' : 'Analyze SMS Message' }}
            </button>
          </div>
        </div>

        <!-- RIGHT INFORMATION PANEL -->
        <div class="space-y-6">

          <!-- OVERVIEW -->
          <div class="rounded-2xl border border-slate-800 bg-[#101d2d] p-5">
            <h3 class="font-semibold text-white">
              Analysis Overview
            </h3>

            <p class="mt-2 text-xs leading-5 text-slate-400">
              The AI independently examines the message, detects
              suspicious patterns, evaluates its intent and
              generates an explainable threat report.
            </p>

            <div class="mt-5 space-y-4">

              <div class="flex items-center gap-3">
                <div class="rounded-lg bg-cyan-400/10 p-2 text-cyan-400">
                  <span class="text-sm">01</span>
                </div>

                <div>
                  <p class="text-sm font-medium text-white">
                    AI Message Analysis
                  </p>
                  <p class="text-xs text-slate-500">
                    Context, intent and language
                  </p>
                </div>
              </div>

              <div class="flex items-center gap-3">
                <div class="rounded-lg bg-cyan-400/10 p-2 text-cyan-400">
                  <span class="text-sm">02</span>
                </div>

                <div>
                  <p class="text-sm font-medium text-white">
                    Cybersecurity Assessment
                  </p>
                  <p class="text-xs text-slate-500">
                    Phishing and fraud indicators
                  </p>
                </div>
              </div>

              <div class="flex items-center gap-3">
                <div class="rounded-lg bg-cyan-400/10 p-2 text-cyan-400">
                  <span class="text-sm">03</span>
                </div>

                <div>
                  <p class="text-sm font-medium text-white">
                    Risk Scoring
                  </p>
                  <p class="text-xs text-slate-500">
                    AI-generated threat percentage
                  </p>
                </div>
              </div>

              <div class="flex items-center gap-3">
                <div class="rounded-lg bg-cyan-400/10 p-2 text-cyan-400">
                  <span class="text-sm">04</span>
                </div>

                <div>
                  <p class="text-sm font-medium text-white">
                    Explainable Report
                  </p>
                  <p class="text-xs text-slate-500">
                    Reasons and safety recommendations
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- PRIVACY -->
          <div class="rounded-2xl border border-cyan-400/20 bg-cyan-400/5 p-5">
            <div class="mb-3 flex items-center gap-2 text-cyan-400">
              <span>ⓘ</span>
              <h3 class="text-sm font-semibold">
                Privacy Notice
              </h3>
            </div>

            <p class="text-xs leading-6 text-slate-400">
              SMS messages are sent to the configured AI provider
              for analysis. Avoid submitting real OTPs, passwords,
              PINs, banking credentials or confidential information.
            </p>
          </div>
        </div>
      </div>

      <!-- THREAT REPORT -->
      <div
        v-if="result"
        class="mt-6 space-y-6 rounded-2xl border border-slate-800 bg-[#101d2d] p-6"
      >

        <!-- REPORT HEADER -->
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 class="text-xl font-bold text-white">
              SMS Threat Analysis Report
            </h2>

            <p class="mt-1 text-xs text-slate-400">
              AI-generated spam and cybersecurity assessment
            </p>
          </div>

          <span
            class="rounded-full border px-4 py-2 text-xs font-bold"
            :class="getRiskColor(result.verdict)"
          >
            {{ result.verdict }}
          </span>
        </div>

        <!-- CLASSIFICATION -->
        <div class="flex flex-wrap gap-3">

          <div
            class="rounded-lg border px-4 py-2 text-sm font-semibold"
            :class="result.is_spam
              ? 'border-rose-500/20 bg-rose-500/10 text-rose-400'
              : 'border-emerald-500/20 bg-emerald-500/10 text-emerald-400'"
          >
            {{ result.is_spam ? 'SPAM DETECTED' : 'NOT SPAM' }}
          </div>

          <div class="rounded-lg border border-slate-700 bg-slate-800/60 px-4 py-2 text-sm text-slate-300">
            {{ result.classification }}
          </div>
        </div>

        <!-- AI SUMMARY -->
        <div class="rounded-xl border border-slate-800 bg-[#091422] p-5">
          <h3 class="font-semibold text-white">
            Executive Summary
          </h3>

          <p class="mt-3 text-sm leading-6 text-slate-300">
            {{ result.summary || 'No summary provided.' }}
          </p>
        </div>

        <!-- FINAL THREAT SCORE -->
        <div class="rounded-2xl border border-cyan-400/20 bg-cyan-400/5 p-6">
          <p class="text-sm text-slate-400">
            Overall Threat Percentage
          </p>

          <div class="mt-2 flex items-end gap-2">
            <span
              class="text-5xl font-bold"
              :class="getScoreColor(result.threat_percentage)"
            >
              {{ result.threat_percentage }}%
            </span>

            <span class="mb-2 text-xs text-slate-500">
              Calculated threat score
            </span>
          </div>

          <div class="mt-5 h-3 overflow-hidden rounded-full bg-slate-800">
            <div
              class="h-full rounded-full transition-all duration-700"
              :class="getScoreBarColor(result.threat_percentage)"
              :style="{ width: `${result.threat_percentage}%` }"
            ></div>
          </div>

          <p class="mt-3 text-xs text-slate-400">
            Final Score = (AI/ML Score × 50%) + (Cybersecurity Score × 50%)
          </p>
        </div>

        <!-- ENGINE SCORES -->
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">

          <!-- AI / ML -->
          <div class="rounded-xl border border-cyan-400/20 bg-[#091422] p-5">
            <div class="flex items-center justify-between">
              <h3 class="font-semibold text-cyan-400">
                AI/ML Engine
              </h3>

              <span class="text-xs text-slate-500">
                50% Weight
              </span>
            </div>

            <p
              class="mt-4 text-3xl font-bold"
              :class="getScoreColor(result.engine_scores.aiml_threat_score)"
            >
              {{ result.engine_scores.aiml_threat_score }}%
            </p>

            <div class="mt-3 h-2 overflow-hidden rounded-full bg-slate-800">
              <div
                class="h-full rounded-full transition-all"
                :class="getScoreBarColor(result.engine_scores.aiml_threat_score)"
                :style="{ width: `${result.engine_scores.aiml_threat_score}%` }"
              ></div>
            </div>

            <div class="mt-5">
              <p class="text-sm text-slate-400">
                Prediction:
                <span class="font-semibold text-white">
                  {{ result.aiml_engine?.prediction || 'Unknown' }}
                </span>
              </p>
            </div>

            <div class="mt-5">
              <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                AI/ML Analysis Reasons
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
                No AI reasons returned.
              </p>
            </div>
          </div>

          <!-- CYBERSECURITY -->
          <div class="rounded-xl border border-emerald-400/20 bg-[#091422] p-5">
            <div class="flex items-center justify-between">
              <h3 class="font-semibold text-emerald-400">
                Cybersecurity Engine
              </h3>

              <span class="text-xs text-slate-500">
                50% Weight
              </span>
            </div>

            <p
              class="mt-4 text-3xl font-bold"
              :class="getScoreColor(result.engine_scores.cybersecurity_threat_score)"
            >
              {{ result.engine_scores.cybersecurity_threat_score }}%
            </p>

            <div class="mt-3 h-2 overflow-hidden rounded-full bg-slate-800">
              <div
                class="h-full rounded-full transition-all"
                :class="getScoreBarColor(result.engine_scores.cybersecurity_threat_score)"
                :style="{ width: `${result.engine_scores.cybersecurity_threat_score}%` }"
              ></div>
            </div>

            <div class="mt-5 space-y-2 text-sm">
              <p class="text-slate-400">
                Security Assessment:
                <span class="text-white">
                  {{ result.cybersecurity_engine?.rule_score ?? 0 }}%
                </span>
              </p>

              <p class="text-slate-400">
                Unusual Message:
                <span class="text-white">
                  {{ result.cybersecurity_engine?.is_unusual ? 'Yes' : 'No' }}
                </span>
              </p>
            </div>

            <div class="mt-5">
              <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Cybersecurity Reasons
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
                No cybersecurity reasons returned.
              </p>
            </div>
          </div>
        </div>

        <!-- SECURITY FINDINGS -->
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
                  {{ finding.indicator || 'Security Indicator' }}
                </p>

                <p class="mt-1 text-xs leading-5 text-slate-400">
                  {{ finding.reason }}
                </p>
              </div>

              <span class="shrink-0 text-xs font-semibold text-amber-400">
                +{{ finding.points }} points
              </span>
            </div>
          </div>

          <p v-else class="mt-3 text-sm text-slate-500">
            No security indicators detected.
          </p>
        </div>

        <!-- ANOMALY DETECTION -->
        <div class="rounded-xl border border-slate-800 bg-[#091422] p-5">
          <h3 class="font-semibold text-white">
            Anomaly Detection
          </h3>

          <div class="mt-3 flex items-center gap-3">
            <span
              class="rounded-full px-3 py-1 text-xs font-semibold"
              :class="result.cybersecurity_engine?.is_unusual
                ? 'bg-amber-500/10 text-amber-400'
                : 'bg-emerald-500/10 text-emerald-400'"
            >
              {{ result.cybersecurity_engine?.is_unusual
                ? 'Unusual Pattern Detected'
                : 'No Significant Anomaly' }}
            </span>
          </div>

          <p class="mt-3 text-sm leading-6 text-slate-300">
            {{
              result.cybersecurity_engine?.anomaly_explanation ||
              'No anomaly explanation returned.'
            }}
          </p>

          <p class="mt-2 text-xs text-slate-500">
            An unusual message is not necessarily malicious.
          </p>
        </div>

        <!-- RECOMMENDATIONS -->
        <div class="rounded-xl border border-amber-400/20 bg-amber-400/5 p-5">
          <h3 class="font-semibold text-amber-400">
            Recommended Actions
          </h3>

          <ul
            v-if="result.recommended_actions?.length"
            class="mt-3 space-y-3"
          >
           <li
  v-for="(action, index) in result.recommended_actions"
  :key="index"
  class="flex items-start gap-3"
>
  <span class="text-amber-400">
    {{ Number(index) + 1 }}
  </span>

  <span>{{ action }}</span>
</li>
          </ul>

          <p v-else class="mt-3 text-sm text-slate-400">
            No recommendations returned.
          </p>
        </div>

        <!-- MESSAGE DETAILS -->
        <div class="rounded-xl border border-slate-800 bg-[#091422] p-5">
          <h3 class="font-semibold text-white">
            Investigation Input
          </h3>

          <div class="mt-4 space-y-3 text-sm">
            <p class="text-slate-400">
              Country Code:
              <span class="text-white">{{ country_code }}</span>
            </p>

            <p class="text-slate-400">
              Mobile Number:
              <span class="text-white">{{ mobile_number || 'Not provided' }}</span>
            </p>

            <div>
              <p class="mb-2 text-slate-400">Analyzed Message:</p>

              <div class="rounded-lg bg-slate-800/60 p-4 text-sm leading-6 text-slate-300">
                {{ message }}
              </div>
            </div>
          </div>
        </div>

        <!-- DISCLAIMER -->
        <p class="text-xs leading-5 text-slate-500">
          {{ result.disclaimer ||
            'This report is AI-generated and should not be treated as definitive proof of malicious activity. Verify suspicious messages through official channels.' }}
        </p>
      </div>
    </div>
  </div>
</template>
