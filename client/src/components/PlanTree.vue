<template>
  <div :id="this.getId()">
  </div>
</template>
<script>
import drawTree from '../scripts/tree.js';

export default {
  name: "plan-tree",
  props: ['tree', 'sourceMap', 'width', 'height', 'id', 'hoverCallback'],
  methods: {
    getId: function() {
      return `tree${this.id}`;
    },
    update: function() {
      drawTree(this.getId(), this.sourceMap, this.tree, this.hoverCallback);
    }
  },
  mounted: function() {
    this.update();
  },
  watch: {
    tree: {
      handler: function(val, oldVal) {
        // Update when the plan is updated
        if (oldVal && val) {
          this.update();
        }
      }
    }
  }
};
</script>
