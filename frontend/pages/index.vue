<template>
  <v-app>
    <v-app-bar color="primary" dark>
      <v-app-bar-title>LLM Knowledge Extractor</v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn icon @click="toggleTheme">
        <v-icon>{{
          isDark ? "mdi-weather-sunny" : "mdi-weather-night"
        }}</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <v-row>
          <v-col cols="12" md="6">
            <v-card class="mb-4">
              <v-card-title>
                <v-icon left>mdi-text-box-plus</v-icon>
                Extract Knowledge
              </v-card-title>
              <v-card-text>
                <v-textarea
                  v-model="inputText"
                  label="Enter text to analyze"
                  placeholder="Paste your text here..."
                  rows="10"
                  outlined
                  :disabled="loading"
                ></v-textarea>

                <v-btn
                  @click="extractKnowledge"
                  color="primary"
                  block
                  large
                  :loading="loading"
                  :disabled="!inputText.trim()"
                >
                  <v-icon left>mdi-brain</v-icon>
                  Extract with Claude
                </v-btn>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" md="6">
            <v-card v-if="currentExtraction" class="mb-4">
              <v-card-title>
                <v-icon left>mdi-lightbulb</v-icon>
                Analysis Results
              </v-card-title>
              <v-card-text>
                <v-expansion-panels>
                  <v-expansion-panel>
                    <v-expansion-panel-title>
                      <v-icon left>mdi-text-short</v-icon>
                      Summary
                    </v-expansion-panel-title>
                    <v-expansion-panel-text>
                      {{ currentExtraction.summary }}
                    </v-expansion-panel-text>
                  </v-expansion-panel>

                  <v-expansion-panel>
                    <v-expansion-panel-title>
                      <v-icon left>mdi-database</v-icon>
                      Structured Data
                    </v-expansion-panel-title>
                    <v-expansion-panel-text>
                      <div
                        v-for="(
                          value, key
                        ) in currentExtraction.structured_data"
                        :key="key"
                        class="mb-2"
                      >
                        <v-chip color="primary" size="small" class="mb-1">{{
                          formatKey(key)
                        }}</v-chip>
                        <div v-if="Array.isArray(value)" class="ml-2">
                          <v-chip
                            v-for="item in value"
                            :key="item"
                            size="small"
                            class="mr-1 mb-1"
                          >
                            {{ item }}
                          </v-chip>
                        </div>
                        <div v-else class="ml-2 text-body-2">
                          {{ value }}
                        </div>
                      </div>
                    </v-expansion-panel-text>
                  </v-expansion-panel>
                </v-expansion-panels>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12">
            <v-card>
              <v-card-title>
                <v-icon left>mdi-history</v-icon>
                Extraction History
                <v-spacer></v-spacer>

                <!-- Filter Toggle -->
                <v-tooltip bottom>
                  <template v-slot:activator="{ props }">
                    <v-btn-toggle
                      v-model="useBackendFilter"
                      mandatory
                      variant="outlined"
                      size="small"
                      class="mr-2"
                      v-bind="props"
                    >
                      <v-btn :value="true" size="small">
                        <v-icon size="small">mdi-server</v-icon>
                      </v-btn>
                      <v-btn :value="false" size="small">
                        <v-icon size="small">mdi-filter-variant</v-icon>
                      </v-btn>
                    </v-btn-toggle>
                  </template>
                  <span>{{
                    useBackendFilter
                      ? "Backend Filtering"
                      : "Frontend Filtering"
                  }}</span>
                </v-tooltip>

                <v-btn @click="loadExtractions" icon variant="text">
                  <v-icon>mdi-refresh</v-icon>
                </v-btn>
              </v-card-title>

              <!-- Search and Filters -->
              <v-card-text>
                <v-row class="mb-3">
                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model="searchQuery"
                      label="Search text..."
                      prepend-inner-icon="mdi-magnify"
                      clearable
                      variant="outlined"
                      density="compact"
                      @keyup.enter="useBackendFilter ? loadExtractions() : null"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="3">
                    <v-select
                      v-model="sentimentFilter"
                      :items="availableSentiments"
                      label="Sentiment"
                      prepend-inner-icon="mdi-emoticon"
                      clearable
                      variant="outlined"
                      density="compact"
                      @update:model-value="
                        useBackendFilter ? loadExtractions() : null
                      "
                    ></v-select>
                  </v-col>

                  <v-col cols="12" md="3">
                    <v-select
                      v-model="categoryFilter"
                      :items="availableCategories"
                      label="Category"
                      prepend-inner-icon="mdi-tag"
                      clearable
                      variant="outlined"
                      density="compact"
                      @update:model-value="
                        useBackendFilter ? loadExtractions() : null
                      "
                    ></v-select>
                  </v-col>

                  <v-col cols="12" md="2">
                    <v-btn
                      v-if="useBackendFilter"
                      @click="performAdvancedSearch"
                      color="primary"
                      block
                      :loading="loadingHistory"
                    >
                      Search
                    </v-btn>
                    <v-btn
                      v-else
                      @click="clearFilters"
                      variant="outlined"
                      block
                    >
                      Clear
                    </v-btn>
                  </v-col>
                </v-row>

                <!-- Results Summary -->
                <v-alert
                  v-if="searchQuery || sentimentFilter || categoryFilter"
                  type="info"
                  variant="tonal"
                  class="mb-3"
                >
                  <template v-slot:prepend>
                    <v-icon>mdi-information</v-icon>
                  </template>
                  Showing {{ extractions.length }} results
                  <template v-if="searchQuery">
                    for "{{ searchQuery }}"</template
                  >
                  <template v-if="sentimentFilter">
                    with {{ sentimentFilter }} sentiment</template
                  >
                  <template v-if="categoryFilter">
                    in {{ categoryFilter }} category</template
                  >
                </v-alert>

                <v-data-table
                  :headers="headers"
                  :items="extractions"
                  :loading="loadingHistory"
                  class="elevation-1"
                >
                  <template v-slot:item.created_at="{ item }">
                    {{ formatDate(item.created_at) }}
                  </template>
                  <template v-slot:item.original_text="{ item }">
                    {{ truncateText(item.original_text, 100) }}
                  </template>
                  <template v-slot:item.summary="{ item }">
                    {{ truncateText(item.summary, 150) }}
                  </template>
                  <template v-slot:item.actions="{ item }">
                    <v-btn
                      @click="viewExtraction(item)"
                      icon
                      size="small"
                      variant="text"
                    >
                      <v-icon>mdi-eye</v-icon>
                    </v-btn>
                    <v-btn
                      @click="deleteExtraction(item.id)"
                      icon
                      size="small"
                      variant="text"
                      color="error"
                    >
                      <v-icon>mdi-delete</v-icon>
                    </v-btn>
                  </template>
                </v-data-table>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>

    <!-- Snackbar for notifications -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="4000">
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.show = false"> Close </v-btn>
      </template>
    </v-snackbar>

    <!-- View Extraction Dialog -->
    <v-dialog v-model="viewDialog" max-width="800px">
      <v-card v-if="selectedExtraction">
        <v-card-title>
          Extraction Details
          <v-spacer></v-spacer>
          <v-btn @click="viewDialog = false" icon variant="text">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-tabs v-model="tab">
            <v-tab value="summary">Summary</v-tab>
            <v-tab value="structured">Structured Data</v-tab>
            <v-tab value="original">Original Text</v-tab>
          </v-tabs>
          <v-tabs-window v-model="tab">
            <v-tabs-window-item value="summary">
              <v-card-text>
                {{ selectedExtraction.summary }}
              </v-card-text>
            </v-tabs-window-item>
            <v-tabs-window-item value="structured">
              <v-card-text>
                <pre>{{
                  JSON.stringify(selectedExtraction.structured_data, null, 2)
                }}</pre>
              </v-card-text>
            </v-tabs-window-item>
            <v-tabs-window-item value="original">
              <v-card-text>
                {{ selectedExtraction.original_text }}
              </v-card-text>
            </v-tabs-window-item>
          </v-tabs-window>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-app>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useTheme } from "vuetify";

const theme = useTheme();
const isDark = ref(false);

// Reactive data
const inputText = ref("");
const loading = ref(false);
const loadingHistory = ref(false);
const currentExtraction = ref(null);
const extractions = ref([]);
const allExtractions = ref([]); // Store all data for frontend filtering
const viewDialog = ref(false);
const selectedExtraction = ref(null);
const tab = ref("summary");

// Search and filter states
const searchQuery = ref("");
const sentimentFilter = ref("");
const categoryFilter = ref("");
const availableSentiments = ref([]);
const availableCategories = ref([]);
const useBackendFilter = ref(true); // Toggle between backend and frontend filtering

const snackbar = ref({
  show: false,
  message: "",
  color: "info",
});

// Data table headers
const headers = [
  { title: "Date", key: "created_at", width: "15%" },
  { title: "Original Text", key: "original_text", width: "35%" },
  { title: "Summary", key: "summary", width: "35%" },
  { title: "Actions", key: "actions", sortable: false, width: "15%" },
];

// Get runtime config
const config = useRuntimeConfig();

// Methods
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
      headers: {
        "Content-Type": "application/json",
      },
      body: {
        text: inputText.value,
      },
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
      // Backend filtering
      const params = new URLSearchParams();
      if (searchQuery.value) params.append("search", searchQuery.value);
      if (sentimentFilter.value)
        params.append("sentiment", sentimentFilter.value);
      if (categoryFilter.value) params.append("category", categoryFilter.value);

      if (params.toString()) {
        url += `?${params.toString()}`;
      }
    }

    const response = await $fetch(url);

    if (useBackendFilter.value) {
      extractions.value = response;
    } else {
      // Frontend filtering
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

  // Text search
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

  // Sentiment filter
  if (sentimentFilter.value) {
    filtered = filtered.filter(
      (ext) => ext.structured_data.sentiment === sentimentFilter.value
    );
  }

  // Category filter
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
    const [sentimentsRes, categoriesRes] = await Promise.all([
      $fetch(`${config.public.apiBase}/api/filters/sentiments`),
      $fetch(`${config.public.apiBase}/api/filters/categories`),
    ]);

    availableSentiments.value = sentimentsRes.sentiments;
    availableCategories.value = categoriesRes.categories;

    console.log("here are the availableSentiments:", sentimentsRes.sentiments);
    console.log("here are the availableCategories:", categoriesRes.categories);
  } catch (error) {
    console.error("Failed to load filter options:", error);
  }
};

const performAdvancedSearch = async () => {
  if (!searchQuery.value.trim()) {
    await loadExtractions();
    return;
  }

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
  } catch (error) {
    console.error("Search error:", error);
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
  } catch (error) {
    console.error("Delete error:", error);
    showSnackbar("Failed to delete extraction", "error");
  }
};

const viewExtraction = (extraction) => {
  selectedExtraction.value = extraction;
  viewDialog.value = true;
};

// Utility functions
const formatKey = (key) => {
  return key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString();
};

const truncateText = (text, maxLength) => {
  if (!text) return "";
  return text.length > maxLength ? text.substring(0, maxLength) + "..." : text;
};

// Load data on component mount
onMounted(async () => {
  loadExtractions();
  await loadFilterOptions();
});

// Watch for filter changes when using frontend filtering
watch([searchQuery, sentimentFilter, categoryFilter], () => {
  if (!useBackendFilter.value) {
    applyFrontendFilters();
  }
});

// Watch for backend/frontend filter toggle
watch(useBackendFilter, () => {
  loadExtractions();
});
</script>

<style scoped>
pre {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
}

.theme--dark pre {
  background-color: rgba(255, 255, 255, 0.05);
}
</style>
