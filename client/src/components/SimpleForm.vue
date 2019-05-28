<template>
  <div id="simple-form">
    <v-form>
      <div class="body-1 mb-3">
        Compare the selected federated query engines using a number of triples.
        To add a new triple, press the enter key while editing an existing triple.
        To delete a triple, press the escape key while editing it.
        A selection of namespace prefixes are automatically used in the query.
        A list of these prefixes is available <a v-on:click="$emit('showPrefixes', true)">here</a>.
        For extended query operations, use the <a v-on:click="$emit('toggleMode')">advanced query mode</a>.
      </div>

      <v-layout row wrap>
        <v-flex xs12>
          <v-layout row wrap
            v-for="(item, index) in this.data"
            :key="index"
            :ref="index">
            <v-flex xs4 v-for="header in headers"
              :key="header.name">
              <v-text-field
                v-model="data[index][header.name]"
                :label="header.text"
                @keyup.native.enter="addRow(index + 1)"
                @keyup.native.esc="deleteRow(index)"
                class="ma-1"
                :ref="index"
                required></v-text-field>
            </v-flex>
          </v-layout>
        </v-flex>
      </v-layout>
    </v-form>
  </div>
</template>

<script>
export default {
  name: "simple-form",
  methods: {
    addRow: function(index) {
      this.data.splice(index, 0, {'subject': '', 'predicate': '', 'object': ''});

      this.$nextTick(function () {
        this.$refs[index][0].focus();
      })
    },
    deleteRow: function(index) {
      if (this.data.length === 1) {
        return;
      }

      this.data.splice(index, 1);

      this.$nextTick(function () {
        this.$refs[Math.max(index - 1, 0)][0].focus();
      })
    },
    getQuery: function() {
      let query = "SELECT * WHERE {\n";

      this.data.forEach(e => {
        query += `\t${e.subject} ${e.predicate} ${e.object} .\n`;
      });
      query += "}";

      return query;
    }
  },
  data() {
    return {
      headers: [{ name: "subject", text: "Subject" },
                { name: "predicate", text: "Predicate" },
                { name: "object", text: "Object" }],
      data: []
    }
  },
  mounted() {
    this.addRow(0);
  }
};
</script>
