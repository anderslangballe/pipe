<template>
  <div id="advanced-form">
    <v-form>
      <div class="body-1 mb-3">
        Compare the selected federated query engines using a custom SPARQL query or choose an existing query from the selection of predefined queries.
        For simple queries, a <a v-on:click="$emit('toggleMode')">simple query mode</a> is available.
      </div>
      <div id="yasqe" class="mb-3">
      </div>
      <!-- <v-textarea name="query" rows="15" label="Advanced query" v-model="query"></v-textarea> -->

      <!-- <v-select solo :items="items" label="Select a predefined query" item-text="name" item-value="value" v-on:change="predefinedChanged"></v-select> -->
    </v-form>
  </div>
</template>

<script>
module.exports = {
  name: "advanced-form",
  data() {
    return {
      query: null,
      yasqe: null,
    };
  },
  methods: {
    getQuery: function() {
      return this.yasqe.getValue();
    },
    setQuery: function(value) {
      this.yasqe.setValue(value);
    }
  },
  mounted() {
    this.yasqe = YASQE(document.getElementById("yasqe"));
  }
};
</script>
