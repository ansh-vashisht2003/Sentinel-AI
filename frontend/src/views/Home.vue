
<script setup lang="ts">
const capabilities = [
  {
    number: '01',
    title: 'AI Threat Detection',
    description: 'Identify suspicious communication and social engineering patterns using AI-driven analysis.',
    tag: 'INTELLIGENT DETECTION'
  },
  {
    number: '02',
    title: 'Explainable Intelligence',
    description: 'Understand why a message is suspicious with clear evidence and contextual explanations.',
    tag: 'TRANSPARENT ANALYSIS'
  },
  {
    number: '03',
    title: 'Risk Assessment',
    description: 'Evaluate potential threats through risk scoring and severity classification.',
    tag: 'CONTEXTUAL SCORING'
  }
]

const threats = [
  { name: 'Phishing', description: 'Deceptive messages designed to steal sensitive information.', code: 'THREAT 01' },
  { name: 'Impersonation', description: 'Fraudulent identities pretending to be trusted people or organisations.', code: 'THREAT 02' },
  { name: 'Financial Fraud', description: 'Fraudulent payment requests and financial manipulation.', code: 'THREAT 03' },
  { name: 'Credential Theft', description: 'Attempts to obtain passwords, OTPs and account credentials.', code: 'THREAT 04' },
  { name: 'Social Manipulation', description: 'Exploitation of trust, fear, urgency and authority.', code: 'THREAT 05' },
  { name: 'Malicious Links', description: 'Suspicious URLs and deceptive web destinations.', code: 'THREAT 06' }
]

const workflow = [
  { number: '01', title: 'Submit', description: 'Provide suspicious communication.' },
  { number: '02', title: 'Process', description: 'Extract relevant message indicators.' },
  { number: '03', title: 'Detect', description: 'Evaluate potential attack patterns.' },
  { number: '04', title: 'Assess', description: 'Generate contextual risk assessment.' },
  { number: '05', title: 'Report', description: 'Review findings and recommendations.' }
]

const insights = [
  {
    category: 'THREAT RESEARCH',
    title: 'Understanding Modern Phishing Attacks',
    description: 'Explore how deceptive communications are designed to manipulate users.'
  },
  {
    category: 'SECURITY AWARENESS',
    title: 'The Psychology Behind Social Engineering',
    description: 'Understand how urgency, trust and authority are exploited.'
  },
  {
    category: 'THREAT INTELLIGENCE',
    title: 'Recognising Digital Impersonation',
    description: 'Learn to identify suspicious identities and fraudulent communication.'
  }
]
</script>

<template>
  <div class="min-h-screen overflow-hidden bg-[#080F1C] text-slate-200">

    <!-- HERO -->
    <section class="relative px-6 py-24 md:px-14 lg:py-32">
      <div class="pointer-events-none absolute -right-40 -top-20 h-[500px] w-[500px] rounded-full bg-cyan-500/10 blur-[130px]"></div>
      <div class="pointer-events-none absolute -left-40 bottom-0 h-[350px] w-[350px] rounded-full bg-blue-600/10 blur-[120px]"></div>

      <div class="relative mx-auto grid max-w-7xl items-center gap-16 lg:grid-cols-2">

        <div>
          <div class="mb-7 inline-flex items-center gap-2 rounded-full border border-cyan-500/20 bg-cyan-500/5 px-4 py-2">
            <span class="h-2 w-2 rounded-full bg-cyan-400"></span>
            <span class="text-[11px] font-semibold tracking-[2px] text-cyan-300">
              AI-POWERED THREAT INTELLIGENCE
            </span>
          </div>

          <h1 class="max-w-2xl text-5xl font-bold leading-[1.12] tracking-tight text-white md:text-6xl xl:text-7xl">
            See the Threat.
            <span class="block text-cyan-400">Understand the Risk.</span>
          </h1>

          <p class="mt-7 max-w-xl text-base leading-8 text-slate-400 md:text-lg">
            An intelligent approach to detecting and analysing social engineering
            threats across digital communication channels.
          </p>

          <div class="mt-10 flex flex-wrap gap-4">
            <button
              @click="$router.push('/whatsapp')"
              class="rounded-lg bg-cyan-400 px-7 py-3.5 text-sm font-bold text-slate-950 transition hover:bg-cyan-300"
            >
              Start Investigation
              <span class="ml-2">→</span>
            </button>

            <a
              href="#platform"
              class="rounded-lg border border-slate-700 px-7 py-3.5 text-sm font-semibold text-white transition hover:border-cyan-400 hover:text-cyan-300"
            >
              Explore Platform
            </a>
          </div>

          <div class="mt-12 flex flex-wrap gap-x-8 gap-y-3 text-xs text-slate-500">
            <span>AI-ASSISTED DETECTION</span>
            <span>EXPLAINABLE ANALYSIS</span>
            <span>MULTI-CHANNEL INTELLIGENCE</span>
          </div>
        </div>

        <!-- Hero intelligence preview -->
        <div class="relative">
          <div class="absolute inset-0 rounded-3xl bg-cyan-400/10 blur-3xl"></div>

          <div class="relative rounded-2xl border border-slate-700/80 bg-[#101C2D] p-5 shadow-2xl shadow-black/40 md:p-7">

            <div class="flex items-center justify-between border-b border-slate-700 pb-5">
              <div>
                <p class="text-xs font-semibold tracking-widest text-slate-500">INTELLIGENCE OVERVIEW</p>
                <h3 class="mt-1 text-lg font-bold text-white">Threat Analysis</h3>
              </div>
              <span class="rounded-md border border-cyan-500/20 bg-cyan-500/10 px-3 py-1.5 text-xs text-cyan-300">
                DEMO PREVIEW
              </span>
            </div>

            <div class="mt-7 grid grid-cols-2 gap-4">
              <div class="rounded-xl border border-slate-700 bg-[#0B1524] p-5">
                <p class="text-xs text-slate-500">RISK SCORE</p>
                <div class="mt-3 flex items-end gap-2">
                  <span class="text-4xl font-bold text-red-400">92</span>
                  <span class="mb-1 text-sm text-slate-500">/100</span>
                </div>
                <p class="mt-2 text-xs text-red-300">Illustrative demo value</p>
              </div>

              <div class="rounded-xl border border-slate-700 bg-[#0B1524] p-5">
                <p class="text-xs text-slate-500">CLASSIFICATION</p>
                <p class="mt-4 text-2xl font-bold text-white">Phishing</p>
                <p class="mt-2 text-xs text-slate-500">Example classification</p>
              </div>
            </div>

            <div class="mt-5 rounded-xl border border-slate-700 bg-[#0B1524] p-5">
              <div class="flex items-center justify-between">
                <p class="text-sm font-semibold text-white">Detected indicators</p>
                <span class="text-xs text-cyan-400">DEMO</span>
              </div>

              <div class="mt-5 space-y-4">
                <div>
                  <div class="mb-2 flex justify-between text-xs">
                    <span class="text-slate-400">Urgency indicators</span>
                    <span class="text-cyan-300">High</span>
                  </div>
                  <div class="h-1.5 rounded-full bg-slate-800">
                    <div class="h-1.5 w-[85%] rounded-full bg-cyan-400"></div>
                  </div>
                </div>

                <div>
                  <div class="mb-2 flex justify-between text-xs">
                    <span class="text-slate-400">Credential request</span>
                    <span class="text-cyan-300">Detected</span>
                  </div>
                  <div class="h-1.5 rounded-full bg-slate-800">
                    <div class="h-1.5 w-[72%] rounded-full bg-blue-400"></div>
                  </div>
                </div>

                <div>
                  <div class="mb-2 flex justify-between text-xs">
                    <span class="text-slate-400">Suspicious language</span>
                    <span class="text-cyan-300">Detected</span>
                  </div>
                  <div class="h-1.5 rounded-full bg-slate-800">
                    <div class="h-1.5 w-[90%] rounded-full bg-indigo-400"></div>
                  </div>
                </div>
              </div>
            </div>

            <div class="mt-5 rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-4">
              <p class="text-xs font-semibold tracking-wider text-cyan-300">AI INSIGHT</p>
              <p class="mt-2 text-sm leading-6 text-slate-300">
                This sample message demonstrates how suspicious indicators
                can be presented with contextual explanations.
              </p>
            </div>

          </div>
        </div>
      </div>
    </section>

    <!-- CAPABILITIES -->
    <section id="platform" class="border-y border-slate-800 bg-[#0C1626] px-6 py-20 md:px-14">
      <div class="mx-auto max-w-7xl">
        <div class="mb-12">
          <p class="text-xs font-bold tracking-[3px] text-cyan-400">THE PLATFORM</p>
          <h2 class="mt-3 text-3xl font-bold text-white md:text-4xl">
            Intelligence built for modern threats.
          </h2>
        </div>

        <div class="grid gap-5 md:grid-cols-3">
          <article
            v-for="item in capabilities"
            :key="item.number"
            class="group rounded-xl border border-slate-800 bg-[#101C2D] p-7 transition duration-300 hover:-translate-y-1 hover:border-cyan-500/40"
          >
            <p class="text-sm font-bold text-cyan-400">{{ item.number }}</p>
            <h3 class="mt-6 text-xl font-bold text-white">{{ item.title }}</h3>
            <p class="mt-4 text-sm leading-7 text-slate-400">{{ item.description }}</p>
            <p class="mt-7 text-[10px] font-semibold tracking-[2px] text-slate-600">{{ item.tag }}</p>
          </article>
        </div>
      </div>
    </section>

    <!-- THREAT CATEGORIES -->
    <section class="px-6 py-20 md:px-14">
      <div class="mx-auto max-w-7xl">
        <div class="mb-12 flex flex-wrap items-end justify-between gap-5">
          <div>
            <p class="text-xs font-bold tracking-[3px] text-cyan-400">THREAT LANDSCAPE</p>
            <h2 class="mt-3 text-3xl font-bold text-white md:text-4xl">
              Threats we aim to identify.
            </h2>
          </div>
          <p class="max-w-md text-sm leading-7 text-slate-400">
            Explore common attack patterns across digital communication.
          </p>
        </div>

        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <article
            v-for="threat in threats"
            :key="threat.code"
            class="rounded-xl border border-slate-800 bg-[#0D1929] p-6 transition hover:border-cyan-500/40 hover:bg-[#111F32]"
          >
            <p class="text-[10px] font-bold tracking-[2px] text-cyan-400">{{ threat.code }}</p>
            <h3 class="mt-5 text-lg font-bold text-white">{{ threat.name }}</h3>
            <p class="mt-3 text-sm leading-6 text-slate-400">{{ threat.description }}</p>
          </article>
        </div>
      </div>
    </section>

    <!-- WORKFLOW -->
    <section class="border-y border-slate-800 bg-[#0C1626] px-6 py-20 md:px-14">
      <div class="mx-auto max-w-7xl">
        <p class="text-xs font-bold tracking-[3px] text-cyan-400">WORKFLOW</p>
        <h2 class="mt-3 text-3xl font-bold text-white md:text-4xl">
          From communication to intelligence.
        </h2>

        <div class="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <div
            v-for="step in workflow"
            :key="step.number"
            class="rounded-xl border border-slate-800 bg-[#101C2D] p-5"
          >
            <span class="text-2xl font-bold text-cyan-400">{{ step.number }}</span>
            <h3 class="mt-5 font-bold text-white">{{ step.title }}</h3>
            <p class="mt-2 text-sm leading-6 text-slate-400">{{ step.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- INSIGHTS -->
    <section id="insights" class="px-6 py-20 md:px-14">
      <div class="mx-auto max-w-7xl">
        <div class="flex flex-wrap items-end justify-between gap-5">
          <div>
            <p class="text-xs font-bold tracking-[3px] text-cyan-400">RESEARCH & INSIGHTS</p>
            <h2 class="mt-3 text-3xl font-bold text-white md:text-4xl">
              Explore the threat landscape.
            </h2>
          </div>
          <button class="text-sm font-semibold text-cyan-400 transition hover:text-cyan-300">
            View all insights →
          </button>
        </div>

        <div class="mt-10 grid gap-5 md:grid-cols-3">
          <article
            v-for="article in insights"
            :key="article.title"
            class="rounded-xl border border-slate-800 bg-[#0D1929] p-6 transition hover:border-cyan-500/40"
          >
            <p class="text-[10px] font-bold tracking-[2px] text-cyan-400">
              {{ article.category }}
            </p>
            <h3 class="mt-5 text-lg font-bold leading-7 text-white">{{ article.title }}</h3>
            <p class="mt-3 text-sm leading-6 text-slate-400">{{ article.description }}</p>
            <button class="mt-6 text-sm font-semibold text-slate-300 hover:text-cyan-400">
              Read article →
            </button>
          </article>
        </div>
      </div>
    </section>

    <!-- FINAL CTA -->
    <section class="px-6 pb-20 md:px-14">
      <div class="mx-auto max-w-7xl rounded-2xl border border-cyan-500/20 bg-gradient-to-r from-cyan-500/10 via-[#10243A] to-blue-500/10 px-8 py-14 text-center md:px-16">
        <p class="text-xs font-bold tracking-[3px] text-cyan-400">SENTINEL AI</p>
        <h2 class="mt-4 text-3xl font-bold text-white md:text-4xl">
          Turn suspicious communication into actionable intelligence.
        </h2>
        <p class="mx-auto mt-5 max-w-2xl text-sm leading-7 text-slate-400">
          Begin an investigation and explore the intelligence behind a suspicious message.
        </p>
        <button
          @click="$router.push('/whatsapp')"
          class="mt-8 rounded-lg bg-cyan-400 px-8 py-3.5 text-sm font-bold text-slate-950 transition hover:bg-cyan-300"
        >
          Start Investigation →
        </button>
      </div>
    </section>

    <!-- FOOTER -->
    <footer class="border-t border-slate-800 bg-[#060C15] px-6 py-8 md:px-14">
      <div class="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4">
        <div>
          <p class="font-extrabold tracking-wider text-white">
            SENTINEL <span class="text-cyan-400">AI</span>
          </p>
          <p class="mt-1 text-xs text-slate-600">AI-POWERED THREAT INTELLIGENCE</p>
        </div>
        <p class="text-xs text-slate-600">
          © 2026 SENTINEL AI. All rights reserved.
        </p>
      </div>
    </footer>

  </div>
</template>
