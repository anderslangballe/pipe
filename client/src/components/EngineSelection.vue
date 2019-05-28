
<template>
  <v-flex>
    <v-container fluid>
      <v-layout row wrap>
        <v-flex v-for="(item, index) in engines" :key="index" xs4>
          <v-checkbox
                v-model="item.enabled"
                :label="item.name"></v-checkbox>
        </v-flex>
      </v-layout>
    </v-container>
  </v-flex>
</template>

<script>
export default {
  props: ['engines'],
  name: "engine-selection"
};
</script>
