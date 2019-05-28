<template>
  <div class="text-xs-center">
    <v-dialog
      width="50%"
      v-model="show"
      transition="dialog-bottom-transition"
    >
      <v-card>
        <v-card-title
          class="headline grey lighten-2"
          primary-title
        >
          Comparison history
        </v-card-title>

        <v-card-text>
          <v-container>
            <v-text-field
              v-model="search"
              append-icon="search"
              label="Search"
              ref="search"
              v-on:keypress="keyPressed"
            ></v-text-field>
            <v-data-table
              :headers="headers"
              :search="search"
              :items="history"
              ref="dataTable"
            >
              <template slot="items" slot-scope="props">
                <td>{{ props.item.result.name }}</td>
                <td>{{ props.item.timestamp | moment("MMMM Do YYYY, HH:mm:ss") }}</td>
                <td>
                  <v-btn icon @click="$emit('openResult', props.item)"><v-icon>open_in_new</v-icon></v-btn>
                  <v-btn icon @click="history.splice(history.indexOf(props.item), 1)"><v-icon>delete</v-icon></v-btn>
                </td>
              </template>
            </v-data-table>
          </v-container>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  name: "history-dialog",
  props: ['visible', 'history'],
  computed: {
    show: {
      get() {
        return this.visible;
      },
      set(value) {
        if (!value) {
          this.$emit('close');
        }
      }
    }
  },
  methods: {
    keyPressed: function(event) {
      if (event.keyCode === 13 && this.search.length) {
        const elements = this.$refs.dataTable.filteredItems;
        if (elements && elements.length) {
          this.$emit('openResult', elements[0]);
        }
      }
    }
  },
  watch: {
    visible: {
      handler() {
        if (this.visible) {
          this.search = '';

          this.$nextTick(() => {
            this.$refs.search.focus();
          });
        }
      }
    }
  },
  data() {
    return {
      'search': '',
      'headers': [
        { text: 'Name', value: 'result.name'},
        { text: 'Saved at', value: 'timestamp'},
        { text: 'Actions', value: 'name', sortable: false }
      ]
    }
  }
};
</script>

