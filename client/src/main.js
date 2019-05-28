import Vue from 'vue'
import VueResource from 'vue-resource'
import App from './App.vue'
import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'
import VueGoogleCharts from 'vue-google-charts'
import VueShortkey from 'vue-shortkey'
import VueMoment from 'vue-moment';

require('./assets/tree.css');
require('./assets/hover.css');
require('./assets/global.css');

Vue.use(VueMoment);
Vue.use(VueShortkey);
Vue.use(VueResource);
Vue.use(Vuetify);
Vue.use(VueGoogleCharts);
Vue.use(d3);

new Vue({
  el: '#app',
  render: h => h(App)
});
