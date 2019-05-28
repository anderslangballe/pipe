<template>
  <v-app id="app">
    <result-dialog
      :prefixes="prefixes"
      :visible="showDialog"
      v-if="this.result"
      :result="result"
      :query="currentQuery"
      @close="showDialog=false"
      @saveResult="saveResult"
    ></result-dialog>

    <prefix-dialog
      :prefixes="prefixes"
      :visible="showPrefixes"
      @close="showPrefixes=false"
    ></prefix-dialog>

    <history-dialog
      :history="comparisonHistory"
      :visible="showHistory"
      @openResult="openResult"
      @close="showHistory=false"
    ></history-dialog>

    <v-content>
      <v-container fluid>
        <v-layout align-center justify-center>
          <v-flex sm8 xs8 md6>
            <v-card class="elevation-10" x>
              <v-toolbar dark color="primary">
                <v-toolbar-title>PIPE</v-toolbar-title>
                <v-spacer></v-spacer>
                <v-btn flat v-on:click="toggleMode">{{ advancedMode ? 'Simple query' : 'Advanced query' }}</v-btn>
              </v-toolbar>
              <v-card-text>
                <v-alert
                  :value="this.errorMessage"
                  type="error"
                >
                  {{ this.errorMessage }}
                </v-alert>

                <keep-alive>
                  <component
                    ref="form"
                    v-bind:is="formComponent"
                    v-on:toggleMode="toggleMode()"
                    v-on:showPrefixes="showPrefixes = $event"
                  ></component>
                </keep-alive>

                <v-expansion-panel>
                  <v-expansion-panel-content>
                    <div slot="header">Settings</div>
                    <v-card>
                      <v-card-text>
                        <v-subheader>
                          Timeout
                        </v-subheader>
                        Specify the maximum duration in seconds that an engine may spend in total on a single query.
                        If the duration is 0, no timeout is enforced.

                        <v-layout row wrap>
                          <v-flex
                            shrink
                            style="width: 60px"
                          >
                            <v-text-field
                              v-model="timeout"
                              class="mt-0"
                              hide-details
                              single-line
                              type="number"
                            ></v-text-field>
                          </v-flex>

                          <v-flex>
                            <v-slider
                              :max="300"
                              v-model="timeout"
                            ></v-slider>
                          </v-flex>
                        </v-layout>
                        <v-divider />
                        <v-subheader>
                          Sources
                        </v-subheader>
                        Select the sources which may be used by the engines.
                        <source-selection :sources="sources"></source-selection>
                        <v-divider />
                        <v-subheader>
                          Engines
                        </v-subheader>
                        Select the engines to include in the comparison. Further filtering is possible when the results are ready.
                        <engine-selection :engines="engines"></engine-selection>
                      </v-card-text>
                    </v-card>
                  </v-expansion-panel-content>
                </v-expansion-panel>

                <v-expansion-panel v-show="advancedMode">
                  <v-expansion-panel-content>
                    <div slot="header">Predefined queries</div>
                    <v-card>
                      <v-card-text>
                        Select any query to load it into the query field.
                        <v-text-field
                          v-model="predefinedSearch"
                          append-icon="search"
                          label="Search"
                          single-line
                          hide-details
                        ></v-text-field>
                        <v-data-table
                          :headers="predefinedHeaders"
                          :items="predefined"
                          :search="predefinedSearch"
                        >
                          <template slot="items" slot-scope="props">
                            <tr @click="setQuery(props.item)">
                              <td>{{ props.item.name }}</td>
                              <td>{{ props.item.operators }}</td>
                              <td>{{ props.item.struct }}</td>
                              <td>{{ props.item.results }}</td>
                            </tr>
                          </template>
                        </v-data-table>
                      </v-card-text>
                    </v-card>
                  </v-expansion-panel-content>
                </v-expansion-panel>
              </v-card-text>
              <v-card-actions v-if="responseState === 1">
                  <v-progress-circular :indeterminate="true"></v-progress-circular>&nbsp;
                  {{ progressMessage }}&nbsp;
                  <v-spacer></v-spacer>
                  <v-btn
                  color="error"
                  v-on:click="cancelJob">Cancel job</v-btn>
              </v-card-actions>
              <v-card-actions v-else>
                <v-spacer />
                  <v-btn
                  color="secondary"
                  v-shortkey.once="['f4']"
                  @shortkey="showHistory=true"
                  @click="showHistory=true"
                  v-if="comparisonHistory.length > 0">History</v-btn>
                <v-btn
                  color="primary"
                  v-on:click="performQuery">Perform query</v-btn>
              </v-card-actions>
            </v-card>
          </v-flex>
        </v-layout>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
import AdvancedForm from "./components/AdvancedForm.vue";
import SimpleForm from "./components/SimpleForm.vue";
import SourceSelection from "./components/SourceSelection.vue";
import ResultDialog from "./components/ResultDialog.vue";
import PrefixDialog from "./components/PrefixDialog";
import PlanTree from "./components/PlanTree";
import EngineSelection from "./components/EngineSelection";
import HistoryDialog from "./components/HistoryDialog";
const flatted = require('flatted');

export default {
  name: "app",
  data() {
    return {
      host: '127.0.0.1:8080',
      prefixes: require('./assets/prefixes.json'),
      predefined: require('./assets/queries.json'),
      advancedMode: false,
      formComponent: SimpleForm,
      comparisonHistory: [],
      canQuery: true,
      currentJobTicket: null,
      dialog: null,
      showDialog: false,
      showPrefixes: false,
      showHistory: false,
      result: null,
      errorMessage: null,
      currentQuery: null,
      engines: null,
      sources: null,
      timeout: 30,
      responseState: 0,
      progressMessage: null,
      predefinedSearch: '',
      predefinedHeaders: [
        {
          text: 'Name',
          value: 'name'
        },
        {
          text: 'Operators',
          value: 'operators'
        },
        {
          text: 'Query structure',
          value: 'struct'
        },
        {
          text: 'Number of results',
          value: 'results'
        }
      ]
    };
  },
  watch: {
    showDialog: function(val) {
      document.querySelector('html').style.overflow = val ? 'hidden' : null
    },
    comparisonHistory: {
      handler() {
        localStorage.setItem('comparisonHistory', flatted.stringify(this.comparisonHistory));
      },
      deep: true,
    }
  },
  mounted() {
    if (localStorage.comparisonHistory) {
      this.comparisonHistory = flatted.parse(localStorage.comparisonHistory);
    }

    this.getAvailableEngines();
    this.getAvailableSources();
  },
  methods: {
    openResult: function(item) {
      this.showHistory = false;
      this.result = item.result;
      this.currentJobTicket = item.ticket;
      this.currentQuery = item.query;
      this.showDialog = true;
    },
    saveResult: function(resultName) {
      if (!resultName) {
        resultName = 'Unnamed comparison';
      }

      // Overwrite existing result
      for (const comparison of this.comparisonHistory) {
        if (comparison.ticket === this.currentJobTicket) {
          comparison.result.name = resultName;

          return;
        }
      }

      this.result.name = resultName;
      this.comparisonHistory.push({'ticket': this.currentJobTicket, 'result': this.result, 'timestamp': Date.now(), 'query': this.currentQuery});
    },
    cancelJob: function() {
      this.$http.delete(`http://${this.host}/api/job/${this.currentJobTicket}`).then(response => {
        // TODO: Should we do anything other than await the ticket to announce cancellation?
      }, response => {
        this.errorMessage = `Failed to cancel job (${response.status}).`;
      });
    },
    getSelectedEngines: function () {
      return this.engines.filter(e => e.enabled).map(e => e.id);
    },
    getSelectedSources: function () {
      return this.sources.filter(e => e.enabled).map(e => e.source);
    },
    getAvailableSources: function() {
      this.$http.get(`http://${this.host}/api/sources`).then(response => {
        if (!response.body.sources) {
          this.errorMessage = 'No available sources.';
          return;
        }
        this.sources = response.body.sources;
        this.sources.forEach(e => {
          e.enabled = true;
          e.hover = false;
        });
      }, response => {
        this.errorMessage = `Unable to retrieve available sources (${response.status}).`;
      });
    },
    getAvailableEngines: function() {
      this.$http.get(`http://${this.host}/api/engines`).then(response => {
        if (!response.body.engines) {
          this.errorMessage = 'No available engines.';
          return;
        }
        this.engines = response.body.engines;
        this.engines.forEach(e => e.enabled = true);
      }, response => {
        this.errorMessage = `Unable to retrieve available engines (${response.status}).`;
      });
    },
    checkTicketState: function(ticket) {
      this.$http.get(`http://${this.host}/api/job/${ticket}`).then(response => {
        const state = response.body.state;
        if (state === 0) {
          this.result = response.body;
          this.showDialog = true;
        } else {
          if (state === 2) {
            this.errorMessage = response.body.message;
          } else {
            this.progressMessage = response.body.message;

            setTimeout(() => this.checkTicketState(ticket), 500);
          }
        }

        this.responseState = state;
      }, response => {
        this.responseState = 0;
        this.errorMessage = `The connection to the server was interrupted (${response.status}).`;

        this.canQuery = true;
      });
    },
    toggleMode: function() {
      this.advancedMode = !this.advancedMode;

      if (this.advancedMode) {
        this.formComponent = AdvancedForm;
      } else {
        this.formComponent = SimpleForm;
      }
    },
    setQuery: function (value) {
      this.$refs.form.setQuery(value.query);
    },
    performQuery: function() {
      let query = this.$refs.form.getQuery();
      if (!query) {
        return;
      }
      this.canQuery = false;
      this.errorMessage = null; // Hides any existing error messages
      this.currentQuery = query;

      // If simple query, add prefixes add this point
      if (!this.advancedMode) {
        let prepend = "";
        for (const key in this.prefixes) {
          prepend += `PREFIX ${this.prefixes[key]}: <${key}>\n`
        }

        query = `${prepend}\n${query}`;
      }

      this.$http.post(`http://${this.host}/api/job`, {'query': query, 'timeout': this.timeout,
        'engines': this.getSelectedEngines(), 'sources': this.getSelectedSources()}).then(response => {
        this.responseState = 2; // TODO: Use consts for readability
        this.progressMessage = 'Requesting ticket';
        const ticket = response.body.ticket;
        if (ticket) {
          this.checkTicketState(ticket);
          this.currentJobTicket = ticket;
        } else {
          this.errorMessage = response.body.message;
        }
      }, response => {
        if (response.body && response.body.message) {
          this.errorMessage = response.body.message;
        } else {
          this.errorMessage = `The connection to the server was interrupted (${response.status}). Check the console for more information.`;
        }
        this.responseState = 0;

        this.canQuery = true;
      });
    }
  },
  components: {
    EngineSelection,
    AdvancedForm,
    SimpleForm,
    SourceSelection,
    ResultDialog,
    PrefixDialog,
    HistoryDialog,
    PlanTree
  }
};
</script>
