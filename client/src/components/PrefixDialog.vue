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
          Namespace prefixes
        </v-card-title>

        <v-card-text>
          <v-container>
            <v-text-field
              v-model="search"
              append-icon="search"
              label="Search"
              ref="search"
            ></v-text-field>
            <v-data-table
              :headers="headers"
              :items="prefixItems"
              :search="search"
            >
              <template slot="items" slot-scope="props">
                <td>{{ props.item.prefix }}</td>
                <td>{{ props.item.uri }}</td>
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
  name: "prefix-dialog",
  props: ['visible', 'prefixes'],
  computed: {
    show: {
      get() {
        return this.visible
      },
      set(value) {
        if (!value) {
          this.$emit('close');
        }
      }
    },
    prefixItems: {
      get() {
        const items = [];
        for (const key in this.prefixes) {
          items.push({'prefix': this.prefixes[key], 'uri': key});
        }

        return items;
      }
    }
  },
  data() {
    return {
      'search': '',
      'headers': [
        {'text': 'Prefix', 'value': 'prefix'},
        {'text': 'URI', 'value': 'uri'}
      ]
    }
  }
};
</script>

