<template>
  <div class="text-xs-center">
    <v-dialog
      v-model="show"
      fullscreen
      transition="dialog-bottom-transition"
    >
      <v-card class="mat-elevation-0">
        <v-toolbar dark color="primary">
          <div>
            <v-text-field
              v-model="name"
              placeholder="Unnamed comparison"
            ></v-text-field>
          </div>
          <v-spacer/>
          <v-btn icon dark
            @click="close()">
            <v-icon>close</v-icon>
          </v-btn>
        </v-toolbar>

        <v-container fluid>
          <v-layout justify-left>
            <v-flex xs3 class="mr-3 mb-3">
              <v-card class="elevation-4 mb-3">
                <v-card-title>
                  <h2 class="title">Query</h2>
                </v-card-title>
                <v-card-text>
                  <pre style="white-space: pre-wrap; word-wrap: break-word;">{{ query.trim() }}</pre>
                </v-card-text>
              </v-card>

              <v-card class="elevation-4 mb-3">
                <v-card-title>
                  <h2 class="title">Engines</h2>
                </v-card-title>
                <v-card-text>
                  Checked engines are included in the current comparison.
                  <v-list>
                    <v-list-tile v-for="(item, index) in this.result.results" v-bind:key="index">
                      <v-list-tile-action>
                        <v-checkbox v-model="enabledEngines[index]" v-on:change="updatePlans()"></v-checkbox>
                      </v-list-tile-action>
                      <v-list-tile-content>
                        <v-list-tile-title>
                          {{ item.name }}
                        </v-list-tile-title>
                        <v-list-tile-sub-title>
                          <template v-if="item.state === 0">
                            Success
                          </template>
                          <template v-else-if="item.state === 1">
                            Timeout
                          </template>
                          <template v-else-if="item.state === 2">
                            Unknown error
                          </template>
                          <template v-else-if="item.state === 3">
                            Result mismatch
                          </template>
                          <template v-else-if="item.state === 4">
                            No results
                          </template>
                          <template v-if="showNumTuples && item.state !== 4">
                            ({{ item.numTuples }} tuples)
                          </template>
                        </v-list-tile-sub-title>
                      </v-list-tile-content>
                      <v-list-tile-action>
                        <v-icon v-if="item.state === 0">
                          done
                        </v-icon>
                        <v-icon v-else-if="item.state === 1">
                          timer
                        </v-icon>
                        <v-icon v-else-if="item.state === 2">
                          error
                        </v-icon>
                        <v-icon v-else>
                          warning
                        </v-icon>
                      </v-list-tile-action>
                    </v-list-tile>
                  </v-list>
                </v-card-text>
              </v-card>

              <v-card class="elevation-4 mb-3">
                <v-card-title>
                  <h2 class="title">Options</h2>
                </v-card-title>
                <v-card-text>
                  <v-switch label="Use logarithmic scale" v-model="logarithmic" />
                </v-card-text>
              </v-card>

            </v-flex>

            <v-flex xs9>
              <v-card class="elevation-4">
                <v-tabs
                  v-model="activeTab"
                >
                  <v-tab
                  :key="0">
                     <div class="tab-title">Performance</div>
                  </v-tab>

                  <v-tab
                  :key="1">
                     <div class="tab-title">Tuples</div>
                  </v-tab>

                  <v-tab
                  :key="2">
                    <div class="tab-title">Plans</div>
                  </v-tab>

                  <v-tab-item
                    :key="0"
                  >
                    <GChart
                      type="ColumnChart"
                      :data="chartData"
                      :options="chartOptions"
                    />
                  </v-tab-item>

                  <v-tab-item
                    :key="1"
                  >
                    <v-data-table
                      v-if="result.bindingNames"
                      :headers="mapHeaders(result.bindingNames)"
                      :items="result.tuples"
                    >
                      <template slot="items" slot-scope="myprops">
                        <td v-for="(header, headerIndex) in mapHeaders(result.bindingNames)"
                        :key="headerIndex">
                        <!-- namespace + localName -->
                        <v-tooltip bottom>
                          <span slot="activator">{{ getPrefix(myprops.item[header.value] ) }}</span>
                          <span>{{ myprops.item[header.value] }}</span>
                        </v-tooltip>
                        </td>
                      </template>
                    </v-data-table>
                  </v-tab-item>


                  <v-tab-item
                    :key="3"
                  >
                    <v-container fluid>
                      <v-layout row fill-height>
                        <v-flex d-flex xs6>
                          <v-card class="mr-3" flat>
                            <v-card-title>
                              <div class="title">Triple patterns</div>
                            </v-card-title>
                            <v-card-text>
                              <ul>
                                <li v-for="(item, itemIndex) in this.result.abbreviations" :key="itemIndex">
                                  <span v-bind:class="{ 'hover': isTripleHighlighted(item.abbreviation) }">{{ item.abbreviation }}: {{ item.value }}</span>
                                </li>
                              </ul>
                            </v-card-text>
                          </v-card>
                        </v-flex>

                        <v-flex xs6>
                          <v-card class="mr-3" flat>
                            <v-card-title>
                              <div class="title">Sources</div>
                            </v-card-title>
                            <v-card-text>
                              <ul style="list-style-type: none; list-style: none; padding-left: 0;">
                                <li v-for="(value, key) in this.result.sourceMap" :key="key">
                                  <span v-bind:style="{'background-color': isSourceHighlighted(key) ? colorize(key) : ''}" ><span v-bind:style="{'background-color': colorize(key)}" class="color-box"></span> {{ value.join(', ') }}</span>
                                </li>
                              </ul>
                            </v-card-text>
                          </v-card>
                        </v-flex>
                      </v-layout>
                    </v-container>

                    <v-container fluid>
                      <v-layout row wrap>
                        <v-flex class="mb-3" v-for="(item, index) in this.plans" v-bind:key="index">
                          <v-card class="mr-3">
                            <v-card-title>
                              <div class="title">{{ item.engines }}</div>
                            </v-card-title>
                            <v-card-text>
                              <plan-tree :hoverCallback="updateHovered" :sourceMap="result.sourceMap" :id="index" width="800" height="250" :tree="item.plan"></plan-tree>
                            </v-card-text>
                          </v-card>
                        </v-flex>
                      </v-layout>
                    </v-container>
                  </v-tab-item>
                </v-tabs>
              </v-card>
            </v-flex>
          </v-layout>
        </v-container>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import PlanTree from '../components/PlanTree';
import compare from '../scripts/objectCompare.js';
import colorFromStr from '../scripts/colorize.js';
import _ from 'lodash'

export default {
  name: "result-dialog",
  props: ['visible', 'result', 'query', 'prefixes'],
  computed: {
    show: {
      get () {
        return this.visible
      },
      set (value) {
        if (!value) {
          this.activeTab = 0;
          this.$emit('close');
          this.saveResult();
        }
      }
    },
    chartData: function() {
      if (!this.performances) {
        return [];
      }

      const data = [['Optimizer', 'Planning time', 'Execution time']];
      this.performances.forEach(value => {
        data.push([value.name, value.planning, value.execution]);
      });

      return data;
    },
    chartOptions: function() {
      return {
        isStacked: true,
        chartArea:{left: 150, right: 20, width: "100%", height:"70%"},
        fontSize: 18,
        bar: {groupWidth: "50%"},
        legend: {
          position: 'top'
        },
        vAxis: {
          title: 'Time (ms)',
          scaleType: this.logarithmic ? 'mirrorLog' : 'linear',
          format: this.logarithmic ? 'scientific' : null
        },
        colors: ['rgb(54, 162, 235)', 'rgb(255, 99, 132)']
      }
    }
  },
  methods: {
    close: function() {
      this.show = false;
    },
    saveResult: function() {
      this.$emit('saveResult', this.name);
    },
    colorize: function(str) {
      return colorFromStr(str);
    },
    mapHeaders: function(headers) {
      return headers.map(function(header) {
        return {'text': header, 'value': header};
      });
    },
    isTripleHighlighted(triple) {
      return this.hoveredTriples.includes(triple);
    },
    isSourceHighlighted(triple) {
      return this.hoveredSources.includes(triple);
    },
    updateHovered: function(node, remove) {
      if (node.sourceId) {
        if (remove) {
          this.hoveredSources.splice(node.sourceId);
        } else {
          this.hoveredSources.push(node.sourceId);
        }
      }

      if (node.value) {
        if (remove) {
          this.hoveredTriples.splice(node.value);
        } else {
          this.hoveredTriples.push(node.value);
        }
      }
    },
    getPrefix: function(cell) {
      if (!cell) {
        return '-';
      }

      const namespace = cell.namespace;
      const localName = cell.localName;
      const label = cell.label;

      if (namespace && localName) {
        const nsLookup = this.prefixes[cell.namespace];
        if (nsLookup) {
          return `${nsLookup}:${localName}`;
        }

        return `${cell.namespace}${localName}`;
      } else if (label) {
        if (label) {
          const properties = [];

          if (cell.datatype) {
            if (cell.datatype.localName) {
              properties.push(cell.datatype.localName);
            } else {
              properties.push(cell.datatype);
            }
          }

          if (cell.language) {
            properties.push(cell.language);
          }

          if (properties.length > 0) {
            return `${label} (${properties.join(', ')})`;
          } else {
            return label;
          }
        }
      }

      return cell;
    },
    updatePlans: function() {
      const plans = [];
      const performances = [];
      this.result.results.filter((item, index) => this.enabledEngines[index]).forEach(item => {
        //item.planString = JSON.stringify(item.plan);

        // Push performance metrics
        performances.push({'name': item.name, 'planning': item.planningTime, 'execution': item.executionTime});

        // Check if the plan already exists
        let found = false;
        for (let plan of plans) {
          if (compare(item.plan, plan.plan)) {
            plan['engines'].push(item.name);
            found = true;
            break;
          }
        }

        if (!found) {
          plans.push({'plan': item.plan, 'engines': [item.name]});
        }
      });

      plans.forEach(plan => plan.engines = plan.engines.join('/'));

      this.plans = plans;
      this.performances = performances;
    }
  },
  data() {
    return {
      hoveredTriples: [],
      hoveredSources: [],
      enabledEngines: [],
      performances: [],
      plans: null,
      panel: [true],
      name: null,
      logarithmic: false,
      showNumTuples: false,
      activeTab: 0
    }
  },
  components: {
    PlanTree
  },
  watch: {
    name: {
      handler: _.debounce(function() {
        if (this.result.name !== this.name) {
          this.saveResult();
        }
      }, 500)
    },
    result: {
      immediate: true,
      handler: function(val, oldVal) {
        this.enabledEngines = new Array(this.result.results.length).fill(1);
        this.plans = [];
        this.performances = [];
        this.showNumTuples = !this.result.results.every(r => r.state === 0);

        if (val && oldVal !== val) {
          this.updatePlans();
        }

        if (val.name) {
          this.name = val.name;
        } else {
          this.name = null;
        }
      }
    }
  }
};
</script>

