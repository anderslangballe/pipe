
<template>
  <v-flex>
    <v-container fluid>
      <v-layout row wrap>
        <v-flex v-for="(item, index) in sources" :key="index" xs4>
          <v-checkbox
                v-model="item.enabled"
                :label="`${item.hover ? item.source + ' - ' + item.endpoint : item.source}`"></v-checkbox>
        </v-flex>
      </v-layout>
    </v-container>
  </v-flex>
</template>

<script>
export default {
  name: "source-selection",
  props: ['sources']
};
</script>
