const { algoliasearch, instantsearch } = window;

import { hitsPerPage } from "instantsearch.js/es/widgets";
import TypesenseInstantSearchAdapter from "typesense-instantsearch-adapter";

const vectorResultsLimit = 200; // limits the number of results from vector search
const ageRange = [0, 124];

const typesenseInstantsearchAdapter = new TypesenseInstantSearchAdapter({
  server: {
    apiKey: "xyz", // Be sure to use the search-only-api-key
    nodes: [
      {
        host: "localhost",
        port: 8108,
        protocol: "http"
      }
    ]
  },
  // The following parameters are directly passed to Typesense's search API endpoint.
  //  So you can pass any parameters supported by the search endpoint below.
  //  query_by is required.
  additionalSearchParameters: {
    query_by: "full_name,conditions,encounter_id,languages,period_start,embedding",
    query_by_weights: '3,3,0,1,1,0',
    text_match_type: 'sum_score', // max_score (default), max_weight, sum_score
    vector_query: `embedding:([], k: ${vectorResultsLimit})`,
    exclude_fields: 'embedding',
  }
});
const searchClient = typesenseInstantsearchAdapter.searchClient;

const search = instantsearch({
  searchClient,
  indexName: "encounters"
});


search.addWidgets([
  instantsearch.widgets.searchBox({
    container: '#searchbox',
  }),
  instantsearch.widgets.configure({
    hitsPerPage: 12
  }),
  instantsearch.widgets.hits({
    container: '#hits',
    templates: {
      item: `
        <div>
          <img src="{{image_url}}" align="left" alt="" />
          <div class="hit-name"> Patient Name: 
            {{#helpers.highlight}} {"attribute": "full_name"} {{/helpers.highlight}}
          </div>
           <div class="hit-conditions"> Encounter ID: {{encounter_id}}</div>
           <div class="hit-conditions"> Conditions: {{conditions}}</div>
          <div class="hit-period-start">Period Start: {{period_start}}</div>
          <div class="hit-period-start">Period End: {{period_end}}</div>
          <div class="hit-status">Encounter Status: {{status}}</div>
          <div class="hit-type">Encounter Type: {{type}}</div>
          <div class="hit-age">Age: {{age}}</div>
        </div>
      `,
    },
  }),
  instantsearch.widgets.pagination({
    container: '#pagination',
  }),
  instantsearch.widgets.refinementList({
    container: '#refinements',
    attribute: 'period_start'
  }),
  instantsearch.widgets.refinementList({
    container: '#age-refinements',
    attribute: 'age'
  }),
  instantsearch.widgets.refinementList({
    container: '#languages-refinements',
    attribute: 'languages'
  }),
  instantsearch.widgets.sortBy({
    container: '#sort-by',
    items: [
      {label: 'Default', value: 'encounters/sort/_text_match:desc'},
      {label: 'period_start', value: 'encounters/sort/period_start:desc'}

    ]
  })
]);

search.start();
