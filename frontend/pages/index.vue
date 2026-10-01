<template>
  <v-app>
    <!-- App Bar -->
    <v-app-bar flat class="app-bar-glass" height="68">
      <div class="d-flex align-center ml-3">
        <div
          class="brand-avatar mr-3"
          :class="{ 'brand-avatar--pulse': loading }"
        >
          <v-icon size="20" color="white">mdi-brain</v-icon>
          <div class="brand-avatar__ring"></div>
        </div>
        <div>
          <div
            class="text-subtitle-1 font-weight-bold lh-tight d-flex align-center"
          >
            Knowledge Extractor
            <v-chip size="x-small" class="ml-2 beta-chip" variant="flat"
              >BETA</v-chip
            >
          </div>
          <div class="text-caption text-medium-emphasis lh-tight">
            <span class="live-dot"></span> Powered by Claude
          </div>
        </div>
      </div>

      <v-spacer></v-spacer>

      <div class="d-none d-sm-flex align-center mr-3 stat-pill">
        <v-icon size="14" class="mr-1">mdi-database</v-icon>
        <span class="stat-pill__num">{{ animatedCount }}</span>
        <span class="ml-1 opacity-70">records</span>
      </div>

      <v-btn icon variant="text" @click="toggleTheme" class="theme-btn mr-3">
        <v-icon class="theme-icon">
          {{ isDark ? "mdi-weather-sunny" : "mdi-weather-night" }}
        </v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <v-container fluid class="pa-4 pa-md-6" style="max-width: 1600px">
        <v-row class="mb-3">
          <!-- INPUT -->
          <v-col cols="12" lg="7">
            <div
              class="glass-card tilt-card pa-1"
              :class="{ extracting: loading }"
              @mousemove="onTilt($event, 'input')"
              @mouseleave="resetTilt('input')"
              :style="tiltStyles.input"
            >
              <div class="pa-5">
                <div class="d-flex align-center mb-4">
                  <div class="section-icon mr-3">
                    <v-icon size="18" color="white">mdi-text-box-plus</v-icon>
                  </div>
                  <div class="mr-auto">
                    <div class="text-h6 font-weight-bold">
                      Extract Knowledge
                    </div>
                    <div class="text-caption text-medium-emphasis">
                      Paste text — Claude does the rest
                    </div>
                  </div>
                  <v-chip
                    v-if="loading"
                    size="small"
                    color="primary"
                    variant="tonal"
                    class="pulse-chip"
                  >
                    <v-icon start size="12">mdi-loading mdi-spin</v-icon>
                    Analyzing
                  </v-chip>
                </div>

                <div
                  class="textarea-wrap"
                  :class="{ 'textarea-wrap--focus': inputFocused }"
                >
                  <div class="textarea-glow"></div>
                  <v-textarea
                    v-model="inputText"
                    placeholder="Paste your text here..."
                    variant="solo-filled"
                    flat
                    rows="8"
                    hide-details
                    :disabled="loading"
                    class="sleek-textarea"
                    auto-grow
                    max-rows="14"
                    @focus="inputFocused = true"
                    @blur="inputFocused = false"
                  >
                    <template v-slot:prepend-inner>
                      <v-icon
                        color="medium-emphasis"
                        size="18"
                        class="mt-3"
                        :class="{ 'quote-bounce': inputText.length > 0 }"
                        >mdi-format-quote-open</v-icon
                      >
                    </template>
                  </v-textarea>
                  <div class="textarea-meta">
                    <span
                      class="char-count"
                      :class="{ 'char-count--active': inputText.length > 0 }"
                    >
                      {{ inputText.length }} chars
                    </span>
                    <span class="word-count">· {{ wordCount }} words</span>
                    <span
                      v-if="inputText.length > 0"
                      class="clear-link"
                      @click="inputText = ''"
                    >
                      <v-icon size="12">mdi-close</v-icon> clear
                    </span>
                  </div>
                </div>

                <div class="d-flex align-center gap-2 mt-4">
                  <v-btn
                    @click="extractKnowledge"
                    color="primary"
                    size="large"
                    rounded="lg"
                    :loading="loading"
                    :disabled="!inputText.trim()"
                    class="flex-grow-1 extract-btn"
                    @click.capture="spawnSparkles($event)"
                  >
                    <template v-if="!loading">
                      <v-icon start class="sparkle-icon">mdi-sparkles</v-icon>
                      Extract with Claude
                    </template>
                    <template v-else>
                      <v-icon start class="mdi-spin">mdi-atom</v-icon>
                      Thinking...
                    </template>
                  </v-btn>
                </div>
              </div>
            </div>
          </v-col>

          <!-- RESULTS -->
          <v-col cols="12" lg="5">
            <div
              class="glass-card tilt-card pa-1 h-100"
              :class="{ 'results-empty': !currentExtraction }"
              @mousemove="onTilt($event, 'output')"
              @mouseleave="resetTilt('output')"
              :style="tiltStyles.output"
            >
              <div class="pa-5 h-100 d-flex flex-column">
                <div class="d-flex align-center mb-4">
                  <div class="section-icon section-icon--alt mr-3">
                    <v-icon size="18" color="white">mdi-lightbulb-on</v-icon>
                  </div>
                  <div class="mr-auto">
                    <div class="text-h6 font-weight-bold">Analysis</div>
                    <div class="text-caption text-medium-emphasis">
                      {{
                        currentExtraction ? "Latest result" : "Awaiting input"
                      }}
                    </div>
                  </div>
                  <v-chip
                    v-if="currentExtraction"
                    size="small"
                    variant="tonal"
                    color="success"
                    class="pop-in"
                  >
                    <v-icon start size="12">mdi-check</v-icon>
                    Ready
                  </v-chip>
                </div>

                <transition name="slide-up" mode="out-in">
                  <div
                    v-if="!currentExtraction"
                    key="empty"
                    class="empty-state flex-grow-1 d-flex flex-column align-center justify-center text-center"
                  >
                    <div class="orbital-loader mb-4">
                      <div class="orbital-loader__ring"></div>
                      <div
                        class="orbital-loader__ring orbital-loader__ring--2"
                      ></div>
                      <v-icon size="32" color="primary">mdi-auto-fix</v-icon>
                    </div>
                    <div class="text-body-2 text-medium-emphasis">
                      Run an extraction to see<br />summary & structured data
                    </div>
                    <div class="mt-4 d-flex gap-1">
                      <v-chip size="x-small" variant="tonal">summary</v-chip>
                      <v-chip size="x-small" variant="tonal">entities</v-chip>
                      <v-chip size="x-small" variant="tonal">sentiment</v-chip>
                    </div>
                  </div>

                  <div v-else key="result" class="flex-grow-1">
                    <v-expansion-panels
                      variant="accordion"
                      class="sleek-panels"
                      :model-value="[0]"
                    >
                      <v-expansion-panel>
                        <v-expansion-panel-title>
                          <v-icon start size="18" color="primary"
                            >mdi-text-short</v-icon
                          >
                          <span class="font-weight-medium">Summary</span>
                          <v-spacer></v-spacer>
                          <v-chip size="x-small" variant="tonal" class="mr-2">
                            {{ currentExtraction.summary.length }} chars
                          </v-chip>
                        </v-expansion-panel-title>
                        <v-expansion-panel-text>
                          <div
                            class="text-body-2 summary-text"
                            style="line-height: 1.75"
                          >
                            {{ currentExtraction.summary }}
                          </div>
                        </v-expansion-panel-text>
                      </v-expansion-panel>

                      <v-expansion-panel>
                        <v-expansion-panel-title>
                          <v-icon start size="18" color="primary"
                            >mdi-database-outline</v-icon
                          >
                          <span class="font-weight-medium"
                            >Structured Data</span
                          >
                          <v-spacer></v-spacer>
                          <v-chip size="x-small" variant="tonal" class="mr-2">
                            {{
                              Object.keys(currentExtraction.structured_data)
                                .length
                            }}
                            fields
                          </v-chip>
                        </v-expansion-panel-title>
                        <v-expansion-panel-text>
                          <div
                            v-for="(
                              value, key
                            ) in currentExtraction.structured_data"
                            :key="key"
                            class="mb-4 data-row"
                          >
                            <div class="data-key mb-2">
                              <v-icon size="12" class="mr-1"
                                >mdi-tag-outline</v-icon
                              >
                              {{ formatKey(key) }}
                            </div>
                            <div
                              v-if="Array.isArray(value)"
                              class="d-flex flex-wrap gap-1"
                            >
                              <v-chip
                                v-for="(item, i) in value"
                                :key="item"
                                size="small"
                                variant="tonal"
                                color="primary"
                                class="pop-in"
                                :style="{ animationDelay: i * 40 + 'ms' }"
                              >
                                {{ item }}
                              </v-chip>
                            </div>
                            <div v-else class="data-value text-body-2">
                              {{ value }}
                            </div>
                          </div>
                        </v-expansion-panel-text>
                      </v-expansion-panel>
                    </v-expansion-panels>
                  </div>
                </transition>
              </div>
            </div>
          </v-col>
        </v-row>

        <!-- HISTORY -->
        <v-row>
          <v-col cols="12">
            <div class="glass-card pa-1">
              <div class="pa-5">
                <div class="d-flex align-center flex-wrap gap-2 mb-4">
                  <div class="section-icon section-icon--violet mr-3">
                    <v-icon size="18" color="white">mdi-history</v-icon>
                  </div>
                  <div class="mr-auto">
                    <div class="text-h6 font-weight-bold">History</div>
                    <div class="text-caption text-medium-emphasis">
                      Browse, filter, and manage past extractions
                    </div>
                  </div>

                  <v-btn-toggle
                    v-model="useBackendFilter"
                    mandatory
                    density="compact"
                    variant="outlined"
                    rounded="lg"
                    class="mr-1 mode-toggle"
                  >
                    <v-btn :value="true" size="small" class="px-3">
                      <v-icon size="16" start>mdi-server</v-icon>
                      <span class="text-caption">Backend</span>
                    </v-btn>
                    <v-btn :value="false" size="small" class="px-3">
                      <v-icon size="16" start>mdi-laptop</v-icon>
                      <span class="text-caption">Frontend</span>
                    </v-btn>
                  </v-btn-toggle>

                  <v-btn
                    @click="loadExtractions"
                    icon
                    variant="tonal"
                    size="small"
                    rounded="lg"
                    class="refresh-btn"
                    :class="{ 'refresh-btn--spin': loadingHistory }"
                  >
                    <v-icon size="18">mdi-refresh</v-icon>
                  </v-btn>
                </div>

                <v-row dense class="mb-2">
                  <v-col cols="12" sm="6" md="5">
                    <v-text-field
                      v-model="searchQuery"
                      placeholder="Search text, entities..."
                      prepend-inner-icon="mdi-magnify"
                      clearable
                      variant="solo-filled"
                      flat
                      density="comfortable"
                      hide-details
                      rounded="lg"
                      @keyup.enter="useBackendFilter ? loadExtractions() : null"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="6" sm="3" md="3">
                    <v-select
                      v-model="sentimentFilter"
                      :items="availableSentiments"
                      placeholder="Sentiment"
                      prepend-inner-icon="mdi-emoticon-outline"
                      clearable
                      variant="solo-filled"
                      flat
                      density="comfortable"
                      hide-details
                      rounded="lg"
                      @update:model-value="
                        useBackendFilter ? loadExtractions() : null
                      "
                    ></v-select>
                  </v-col>
                  <v-col cols="6" sm="3" md="3">
                    <v-select
                      v-model="categoryFilter"
                      :items="availableCategories"
                      placeholder="Category"
                      prepend-inner-icon="mdi-tag-outline"
                      clearable
                      variant="solo-filled"
                      flat
                      density="comfortable"
                      hide-details
                      rounded="lg"
                      @update:model-value="
                        useBackendFilter ? loadExtractions() : null
                      "
                    ></v-select>
                  </v-col>
                  <v-col cols="12" md="1" class="d-flex">
                    <v-btn
                      v-if="useBackendFilter"
                      @click="performAdvancedSearch"
                      color="primary"
                      rounded="lg"
                      block
                      :loading="loadingHistory"
                      height="48"
                    >
                      <v-icon>mdi-magnify</v-icon>
                    </v-btn>
                    <v-btn
                      v-else
                      @click="clearFilters"
                      variant="tonal"
                      rounded="lg"
                      block
                      height="48"
                    >
                      <v-icon>mdi-filter-remove-outline</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>

                <transition name="fade">
                  <div
                    v-if="searchQuery || sentimentFilter || categoryFilter"
                    class="d-flex align-center flex-wrap gap-2 mb-3 mt-1"
                  >
                    <v-icon size="14" color="primary"
                      >mdi-filter-variant</v-icon
                    >
                    <span class="text-caption text-medium-emphasis">
                      {{ extractions.length }} result{{
                        extractions.length === 1 ? "" : "s"
                      }}
                    </span>
                    <v-chip
                      v-if="searchQuery"
                      size="x-small"
                      closable
                      variant="tonal"
                      @click:close="
                        searchQuery = '';
                        useBackendFilter ? loadExtractions() : null;
                      "
                    >
                      "{{ searchQuery }}"
                    </v-chip>
                    <v-chip
                      v-if="sentimentFilter"
                      size="x-small"
                      closable
                      variant="tonal"
                      color="primary"
                      @click:close="
                        sentimentFilter = '';
                        useBackendFilter ? loadExtractions() : null;
                      "
                    >
                      {{ sentimentFilter }}
                    </v-chip>
                    <v-chip
                      v-if="categoryFilter"
                      size="x-small"
                      closable
                      variant="tonal"
                      color="secondary"
                      @click:close="
                        categoryFilter = '';
                        useBackendFilter ? loadExtractions() : null;
                      "
                    >
                      {{ categoryFilter }}
                    </v-chip>
                  </div>
                </transition>

                <v-data-table
                  :headers="headers"
                  :items="extractions"
                  :loading="loadingHistory"
                  class="sleek-table"
                  hover
                  density="comfortable"
                  items-per-page="10"
                >
                  <!-- <template v-slot:loading>
                    <v-skeleton-loader type="table-row@5"></v-skeleton-loader>
                  </template> -->

                  <template v-slot:no-data>
                    <div class="empty-state py-10 text-center">
                      <v-icon size="48" color="medium-emphasis" class="mb-2">
                        mdi-inbox-outline
                      </v-icon>
                      <div class="text-body-2 text-medium-emphasis">
                        No extractions found
                      </div>
                    </div>
                  </template>

                  <template v-slot:item.created_at="{ item }">
                    <div class="text-caption">
                      <div class="font-weight-medium">
                        {{ formatDate(item.created_at).split(",")[0] }}
                      </div>
                      <div class="text-medium-emphasis">
                        {{ formatDate(item.created_at).split(",")[1] }}
                      </div>
                    </div>
                  </template>

                  <template v-slot:item.original_text="{ item }">
                    <span class="text-body-2">{{
                      truncateText(item.original_text, 80)
                    }}</span>
                  </template>

                  <template v-slot:item.summary="{ item }">
                    <span class="text-body-2 text-medium-emphasis">{{
                      truncateText(item.summary, 100)
                    }}</span>
                  </template>

                  <template v-slot:item.actions="{ item }">
                    <div class="d-flex gap-1 justify-end">
                      <v-btn
                        @click="viewExtraction(item)"
                        icon
                        size="small"
                        variant="text"
                        color="primary"
                        class="row-action"
                      >
                        <v-icon size="18">mdi-eye-outline</v-icon>
                      </v-btn>
                      <v-btn
                        @click="deleteExtraction(item.id)"
                        icon
                        size="small"
                        variant="text"
                        color="error"
                        class="row-action row-action--danger"
                      >
                        <v-icon size="18">mdi-delete-outline</v-icon>
                      </v-btn>
                    </div>
                  </template>
                </v-data-table>
              </div>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-main>

    <!-- Sparkle layer -->
    <div class="sparkle-layer" ref="sparkleLayer"></div>

    <!-- Snackbar -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="4000"
      location="bottom right"
      rounded="lg"
      elevation="12"
      class="toast-snack"
    >
      <div class="d-flex align-center">
        <v-icon start size="18">
          {{
            snackbar.color === "success"
              ? "mdi-check-circle"
              : snackbar.color === "error"
              ? "mdi-alert-circle"
              : "mdi-information"
          }}
        </v-icon>
        {{ snackbar.message }}
      </div>
      <template v-slot:actions>
        <v-btn variant="text" size="small" @click="snackbar.show = false"
          >Close</v-btn
        >
      </template>
    </v-snackbar>

    <!-- Dialog -->
    <v-dialog v-model="viewDialog" max-width="820px" scrollable>
      <div v-if="selectedExtraction" class="glass-card dialog-card">
        <div class="d-flex align-center pa-5">
          <div class="section-icon mr-3">
            <v-icon size="18" color="white">mdi-file-document-outline</v-icon>
          </div>
          <div class="mr-auto">
            <div class="text-h6 font-weight-bold">Extraction Details</div>
            <div class="text-caption text-medium-emphasis">
              {{ formatDate(selectedExtraction.created_at) }}
            </div>
          </div>
          <v-btn @click="viewDialog = false" icon variant="text">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </div>

        <v-divider></v-divider>

        <v-tabs v-model="tab" class="px-5" align-tabs="start">
          <v-tab value="summary">
            <v-icon start size="18">mdi-text-short</v-icon> Summary
          </v-tab>
          <v-tab value="structured">
            <v-icon start size="18">mdi-database-outline</v-icon> Structured
          </v-tab>
          <v-tab value="original">
            <v-icon start size="18">mdi-text-box-outline</v-icon> Original
          </v-tab>
        </v-tabs>

        <v-divider></v-divider>

        <v-card-text style="max-height: 60vh">
          <v-tabs-window v-model="tab">
            <v-tabs-window-item value="summary">
              <div class="pa-3 text-body-1" style="line-height: 1.8">
                {{ selectedExtraction.summary }}
              </div>
            </v-tabs-window-item>
            <v-tabs-window-item value="structured">
              <pre class="code-block">{{
                JSON.stringify(selectedExtraction.structured_data, null, 2)
              }}</pre>
            </v-tabs-window-item>
            <v-tabs-window-item value="original">
              <div class="pa-3 text-body-2" style="line-height: 1.8">
                {{ selectedExtraction.original_text }}
              </div>
            </v-tabs-window-item>
          </v-tabs-window>
        </v-card-text>
      </div>
    </v-dialog>
  </v-app>
</template>

<script setup>
import { ref, onMounted, watch, computed, reactive } from "vue";
import { useTheme } from "vuetify";

const theme = useTheme();
const isDark = ref(false);

/* State */
const inputText = ref("");
const inputFocused = ref(false);
const loading = ref(false);
const loadingHistory = ref(false);
const currentExtraction = ref(null);
const extractions = ref([]);
const allExtractions = ref([]);
const viewDialog = ref(false);
const selectedExtraction = ref(null);
const tab = ref("summary");

const searchQuery = ref("");
const sentimentFilter = ref("");
const categoryFilter = ref("");
const availableSentiments = ref([]);
const availableCategories = ref([]);
const useBackendFilter = ref(true);

const snackbar = ref({ show: false, message: "", color: "info" });

const headers = [
  { title: "Date", key: "created_at", width: "15%" },
  { title: "Original Text", key: "original_text", width: "35%" },
  { title: "Summary", key: "summary", width: "35%" },
  {
    title: "Actions",
    key: "actions",
    sortable: false,
    width: "15%",
    align: "end",
  },
];

const config = useRuntimeConfig();
const sparkleLayer = ref(null);

/* Tilt */
const tilts = reactive({
  input: { rx: 0, ry: 0 },
  output: { rx: 0, ry: 0 },
});
const tiltStyles = computed(() => ({
  input: {
    transform: `perspective(1200px) rotateX(${tilts.input.rx}deg) rotateY(${tilts.input.ry}deg)`,
    transition: "transform 0.4s cubic-bezier(0.2, 0.8, 0.2, 1)",
  },
  output: {
    transform: `perspective(1200px) rotateX(${tilts.output.rx}deg) rotateY(${tilts.output.ry}deg)`,
    transition: "transform 0.4s cubic-bezier(0.2, 0.8, 0.2, 1)",
  },
}));

const onTilt = (e, key) => {
  const rect = e.currentTarget.getBoundingClientRect();
  const x = (e.clientX - rect.left) / rect.width - 0.5;
  const y = (e.clientY - rect.top) / rect.height - 0.5;
  tilts[key].ry = x * 3;
  tilts[key].rx = -y * 3;
};
const resetTilt = (key) => {
  tilts[key].rx = 0;
  tilts[key].ry = 0;
};

/* Count-up animation */
const animatedCount = ref(0);
watch(
  () => extractions.value.length,
  (n) => {
    const start = animatedCount.value;
    const duration = 500;
    const t0 = performance.now();
    const tick = (t) => {
      const p = Math.min((t - t0) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      animatedCount.value = Math.round(start + (n - start) * eased);
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }
);

const wordCount = computed(() => {
  const t = inputText.value.trim();
  return t ? t.split(/\s+/).length : 0;
});

/* Sparkle effect */
const spawnSparkles = (e) => {
  const layer = sparkleLayer.value;
  if (!layer) return;
  const rect = e.currentTarget.getBoundingClientRect();
  for (let i = 0; i < 14; i++) {
    const s = document.createElement("div");
    s.className = "sparkle";
    const angle = (Math.PI * 2 * i) / 14 + Math.random() * 0.5;
    const dist = 40 + Math.random() * 60;
    s.style.left = rect.left + rect.width / 2 + "px";
    s.style.top = rect.top + rect.height / 2 + "px";
    s.style.setProperty("--tx", Math.cos(angle) * dist + "px");
    s.style.setProperty("--ty", Math.sin(angle) * dist + "px");
    s.style.background = i % 2 ? "#a855f7" : "#6366f1";
    s.style.animationDelay = i * 15 + "ms";
    layer.appendChild(s);
    setTimeout(() => s.remove(), 900);
  }
};

/* Methods */
const toggleTheme = () => {
  isDark.value = !isDark.value;
  theme.global.name.value = isDark.value ? "dark" : "light";
};

const showSnackbar = (message, color = "info") => {
  snackbar.value = { show: true, message, color };
};

const extractKnowledge = async () => {
  if (!inputText.value.trim()) return;
  loading.value = true;
  try {
    const response = await $fetch(`${config.public.apiBase}/api/extract`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: { text: inputText.value },
    });
    currentExtraction.value = response;
    inputText.value = "";
    showSnackbar("Knowledge extracted successfully!", "success");
    await loadExtractions();
  } catch (error) {
    console.error("Extraction error:", error);
    showSnackbar("Failed to extract knowledge. Please try again.", "error");
  } finally {
    loading.value = false;
  }
};

const loadExtractions = async () => {
  loadingHistory.value = true;
  try {
    let url = `${config.public.apiBase}/api/extractions`;
    if (useBackendFilter.value) {
      const params = new URLSearchParams();
      if (searchQuery.value) params.append("search", searchQuery.value);
      if (sentimentFilter.value)
        params.append("sentiment", sentimentFilter.value);
      if (categoryFilter.value) params.append("category", categoryFilter.value);
      if (params.toString()) url += `?${params.toString()}`;
    }
    const response = await $fetch(url);
    if (useBackendFilter.value) {
      extractions.value = response;
    } else {
      allExtractions.value = response;
      applyFrontendFilters();
    }
  } catch (error) {
    console.error("Failed to load extractions:", error);
    showSnackbar("Failed to load extraction history", "error");
  } finally {
    loadingHistory.value = false;
  }
};

const applyFrontendFilters = () => {
  let filtered = [...allExtractions.value];
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(
      (ext) =>
        ext.original_text.toLowerCase().includes(query) ||
        ext.summary.toLowerCase().includes(query) ||
        (ext.structured_data.key_entities &&
          ext.structured_data.key_entities.some((entity) =>
            entity.toLowerCase().includes(query)
          ))
    );
  }
  if (sentimentFilter.value) {
    filtered = filtered.filter(
      (ext) => ext.structured_data.sentiment === sentimentFilter.value
    );
  }
  if (categoryFilter.value) {
    filtered = filtered.filter(
      (ext) =>
        ext.structured_data.categories &&
        ext.structured_data.categories.includes(categoryFilter.value)
    );
  }
  extractions.value = filtered;
};

const loadFilterOptions = async () => {
  try {
    const [s, c] = await Promise.all([
      $fetch(`${config.public.apiBase}/api/filters/sentiments`),
      $fetch(`${config.public.apiBase}/api/filters/categories`),
    ]);
    availableSentiments.value = s.sentiments;
    availableCategories.value = c.categories;
  } catch (e) {
    console.error("Failed to load filter options:", e);
  }
};

const performAdvancedSearch = async () => {
  if (!searchQuery.value.trim()) return loadExtractions();
  loadingHistory.value = true;
  try {
    const response = await $fetch(
      `${config.public.apiBase}/api/extractions/search?q=${encodeURIComponent(
        searchQuery.value
      )}`
    );
    extractions.value = response.results;
    showSnackbar(
      `Found ${response.count} results for "${response.query}"`,
      "info"
    );
  } catch (e) {
    showSnackbar("Search failed. Please try again.", "error");
  } finally {
    loadingHistory.value = false;
  }
};

const clearFilters = () => {
  searchQuery.value = "";
  sentimentFilter.value = "";
  categoryFilter.value = "";
  loadExtractions();
};

const deleteExtraction = async (id) => {
  try {
    await $fetch(`${config.public.apiBase}/api/extractions/${id}`, {
      method: "DELETE",
    });
    showSnackbar("Extraction deleted successfully", "success");
    await loadExtractions();
    if (currentExtraction.value && currentExtraction.value.id === id) {
      currentExtraction.value = null;
    }
  } catch (e) {
    showSnackbar("Failed to delete extraction", "error");
  }
};

const viewExtraction = (extraction) => {
  selectedExtraction.value = extraction;
  viewDialog.value = true;
};

const formatKey = (key) =>
  key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
const formatDate = (d) => new Date(d).toLocaleString();
const truncateText = (t, n) =>
  !t ? "" : t.length > n ? t.substring(0, n) + "..." : t;

onMounted(async () => {
  loadExtractions();
  await loadFilterOptions();
});

watch([searchQuery, sentimentFilter, categoryFilter], () => {
  if (!useBackendFilter.value) applyFrontendFilters();
});
watch(useBackendFilter, () => loadExtractions());
</script>

<style scoped>
/* ============================================================
   BACKGROUND — clean, no aurora
   ============================================================ */
:global(.v-application) {
  background: rgb(var(--v-theme-background)) !important;
}

/* ============================================================
   APP BAR
   ============================================================ */
.app-bar-glass {
  backdrop-filter: blur(18px) saturate(180%);
  -webkit-backdrop-filter: blur(18px) saturate(180%);
  background: rgba(var(--v-theme-surface), 0.85) !important;
  border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.08);
}

.brand-avatar {
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
}
.brand-avatar__ring {
  position: absolute;
  inset: -3px;
  border-radius: 15px;
  border: 1.5px solid rgba(99, 102, 241, 0.4);
  opacity: 0;
}
.brand-avatar--pulse .brand-avatar__ring {
  opacity: 1;
  animation: ringPulse 1.5s ease-out infinite;
}
@keyframes ringPulse {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1.35);
    opacity: 0;
  }
}

.beta-chip {
  background: linear-gradient(135deg, #6366f1, #a855f7) !important;
  color: white !important;
  font-size: 9px !important;
  height: 16px !important;
  letter-spacing: 0.5px;
}

.live-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #22c55e;
  margin-right: 5px;
  box-shadow: 0 0 8px #22c55e;
  animation: livePulse 2s ease-in-out infinite;
}
@keyframes livePulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}

.stat-pill {
  display: flex;
  align-items: center;
  padding: 5px 12px;
  border-radius: 999px;
  background: rgba(var(--v-theme-primary), 0.1);
  border: 1px solid rgba(var(--v-theme-primary), 0.15);
  font-size: 0.78rem;
  color: rgb(var(--v-theme-primary));
  font-weight: 600;
}
.stat-pill__num {
  font-variant-numeric: tabular-nums;
}

.theme-btn :deep(.v-icon) {
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.theme-btn:hover :deep(.v-icon) {
  transform: rotate(180deg);
}

/* ============================================================
   GLASS CARDS — solid surface, subtle shadow
   ============================================================ */
.glass-card {
  position: relative;
  background: rgb(var(--v-theme-surface)) !important;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  border-radius: 20px !important;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04), 0 8px 32px rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.35s ease, border-color 0.35s ease,
    transform 0.35s ease;
}
:global(.v-theme--dark) .glass-card {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}
.glass-card:hover {
  border-color: rgba(var(--v-theme-primary), 0.3);
  box-shadow: 0 12px 44px rgba(99, 102, 241, 0.15);
}
.tilt-card {
  will-change: transform;
}
.results-empty {
  min-height: 320px;
}

.extracting {
  animation: extractGlow 2s ease-in-out infinite;
}
@keyframes extractGlow {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.3), 0 8px 32px rgba(0, 0, 0, 0.06);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(99, 102, 241, 0),
      0 12px 44px rgba(99, 102, 241, 0.35);
  }
}

/* ============================================================
   SECTION ICONS
   ============================================================ */
.section-icon {
  width: 38px;
  height: 38px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  flex-shrink: 0;
}
.section-icon--alt {
  background: linear-gradient(135deg, #f59e0b, #ec4899);
  box-shadow: 0 4px 12px rgba(236, 72, 153, 0.3);
}
.section-icon--violet {
  background: linear-gradient(135deg, #a855f7, #6366f1);
  box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3);
}

/* ============================================================
   TEXTAREA
   ============================================================ */
.textarea-wrap {
  position: relative;
}
.textarea-glow {
  position: absolute;
  inset: -1px;
  border-radius: 16px;
  padding: 1px;
  background: linear-gradient(135deg, #6366f1, #a855f7, #06b6d4);
  opacity: 0;
  transition: opacity 0.35s ease;
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
  z-index: 1;
}
.textarea-wrap--focus .textarea-glow {
  opacity: 1;
}

.sleek-textarea :deep(.v-field) {
  border-radius: 14px !important;
  font-size: 0.95rem;
  background: rgba(var(--v-theme-on-surface), 0.03) !important;
}
.sleek-textarea :deep(.v-field--focused) {
  background: rgba(var(--v-theme-on-surface), 0.05) !important;
}
.sleek-textarea :deep(textarea) {
  line-height: 1.7;
}

.quote-bounce {
  animation: quotePop 0.4s ease;
}
@keyframes quotePop {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.25);
  }
  100% {
    transform: scale(1);
  }
}

.textarea-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.72rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
  margin-top: 6px;
  padding-left: 4px;
}
.char-count--active {
  color: rgb(var(--v-theme-primary));
  font-weight: 600;
}
.clear-link {
  margin-left: auto;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 2px;
  opacity: 0.6;
  transition: opacity 0.2s;
}
.clear-link:hover {
  opacity: 1;
  color: rgb(var(--v-theme-primary));
}

/* ============================================================
   EXTRACT BUTTON
   ============================================================ */
.extract-btn {
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
  background-size: 200% 200% !important;
  color: white !important;
  font-weight: 600;
  letter-spacing: 0.3px;
  text-transform: none;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.35) !important;
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s ease,
    background-position 0.6s ease;
  position: relative;
  overflow: hidden;
}
.extract-btn:not(:disabled) {
  animation: gradientShift 6s ease infinite;
}
@keyframes gradientShift {
  0%,
  100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}
.extract-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(99, 102, 241, 0.5) !important;
}
.extract-btn:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
}
.extract-btn:disabled {
  background: rgba(var(--v-theme-on-surface), 0.08) !important;
  box-shadow: none !important;
  color: rgba(var(--v-theme-on-surface), 0.45) !important;
}

.sparkle-icon {
  animation: sparkleTwinkle 2s ease-in-out infinite;
}
@keyframes sparkleTwinkle {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(0.9);
  }
}

/* ============================================================
   ORBITAL LOADER
   ============================================================ */
.orbital-loader {
  position: relative;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.orbital-loader__ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 1.5px dashed rgba(var(--v-theme-primary), 0.35);
  animation: orbit 8s linear infinite;
}
.orbital-loader__ring--2 {
  inset: 12px;
  border-style: solid;
  border-color: rgba(var(--v-theme-primary), 0.15);
  border-top-color: rgb(var(--v-theme-primary));
  animation: orbit 2s linear infinite reverse;
}
@keyframes orbit {
  to {
    transform: rotate(360deg);
  }
}

/* ============================================================
   EXPANSION PANELS
   ============================================================ */
.sleek-panels :deep(.v-expansion-panel) {
  background: rgba(var(--v-theme-on-surface), 0.03) !important;
  border-radius: 12px !important;
  margin-bottom: 8px;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  transition: border-color 0.25s ease;
}
.sleek-panels :deep(.v-expansion-panel:hover) {
  border-color: rgba(var(--v-theme-primary), 0.25);
}
.sleek-panels :deep(.v-expansion-panel-title) {
  font-size: 0.9rem;
  min-height: 52px;
}
.sleek-panels :deep(.v-expansion-panel-text__wrapper) {
  padding: 12px 20px 20px;
}

.summary-text {
  color: rgba(var(--v-theme-on-surface), 0.9);
}

/* ============================================================
   DATA ROWS
   ============================================================ */
.data-key {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  color: rgb(var(--v-theme-primary));
  opacity: 0.9;
  display: inline-flex;
  align-items: center;
}
.data-value {
  padding-left: 2px;
  color: rgba(var(--v-theme-on-surface), 0.9);
}
.data-row {
  animation: fadeUp 0.35s ease both;
}
@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ============================================================
   TABLE
   ============================================================ */
.sleek-table {
  background: transparent !important;
}
.sleek-table :deep(.v-data-table__th) {
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: rgba(var(--v-theme-on-surface), 0.6) !important;
  background: transparent !important;
}
.sleek-table :deep(.v-data-table__tr) {
  transition: background 0.2s ease;
}
.sleek-table :deep(.v-data-table__tr:hover) {
  background: rgba(var(--v-theme-primary), 0.06) !important;
}
.sleek-table :deep(.v-data-table__td) {
  border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  color: rgba(var(--v-theme-on-surface), 0.9);
}

.row-action {
  transition: transform 0.2s ease, background 0.2s ease;
}
.row-action:hover {
  transform: scale(1.12);
  background: rgba(var(--v-theme-primary), 0.12) !important;
}
.row-action--danger:hover {
  background: rgba(239, 68, 68, 0.12) !important;
}

/* ============================================================
   MODE TOGGLE / REFRESH
   ============================================================ */
.mode-toggle :deep(.v-btn) {
  text-transform: none;
  letter-spacing: 0;
}
.refresh-btn {
  transition: background 0.25s ease;
}
.refresh-btn:hover {
  background: rgba(var(--v-theme-primary), 0.12) !important;
}
.refresh-btn--spin :deep(.v-icon) {
  animation: orbit 1s linear infinite;
}

/* ============================================================
   DIALOG / CODE
   ============================================================ */
.dialog-card {
  border-radius: 20px !important;
  overflow: hidden;
}

.code-block {
  background: rgba(var(--v-theme-on-surface), 0.06);
  padding: 16px;
  border-radius: 12px;
  overflow-x: auto;
  font-size: 0.82rem;
  line-height: 1.6;
  font-family: "JetBrains Mono", "Fira Code", monospace;
  color: rgba(var(--v-theme-on-surface), 0.95);
}

/* ============================================================
   SPARKLES
   ============================================================ */
.sparkle-layer {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
}
.sparkle {
  position: absolute;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  animation: sparkleFly 0.85s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
  box-shadow: 0 0 8px currentColor;
}
@keyframes sparkleFly {
  0% {
    transform: translate(-50%, -50%) scale(0);
    opacity: 1;
  }
  40% {
    transform: translate(
        calc(-50% + var(--tx) * 0.6),
        calc(-50% + var(--ty) * 0.6)
      )
      scale(1.2);
    opacity: 1;
  }
  100% {
    transform: translate(calc(-50% + var(--tx)), calc(-50% + var(--ty)))
      scale(0);
    opacity: 0;
  }
}

/* ============================================================
   TRANSITIONS
   ============================================================ */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: opacity 0.35s ease, transform 0.35s cubic-bezier(0.2, 0.8, 0.2, 1);
}
.slide-up-enter-from {
  opacity: 0;
  transform: translateY(12px);
}
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.pop-in {
  animation: popIn 0.4s cubic-bezier(0.2, 1.4, 0.5, 1) both;
}
@keyframes popIn {
  from {
    opacity: 0;
    transform: scale(0.85);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.pulse-chip {
  animation: pulseChip 1.6s ease-in-out infinite;
}
@keyframes pulseChip {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

/* ============================================================
   MISC
   ============================================================ */
.gap-1 {
  gap: 4px;
}
.gap-2 {
  gap: 8px;
}
.opacity-70 {
  opacity: 0.7;
}
.mdi-spin {
  animation: orbit 1s linear infinite;
}
</style>
