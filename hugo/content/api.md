---
title: "API Documentation"
date: 2019-11-08T10:34:23+01:00
draft: false
type: page
---
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.24.2/swagger-ui.css" integrity="sha256-Dw3/dQaA/3PKkN2b3agvmpPhItQwRBufnIRmCYo2vo0=" crossorigin="anonymous" />
<script src="//unpkg.com/swagger-ui-dist@3/swagger-ui-bundle.js"></script>

<div id="swagger-ui"></div>

<script>
  const ui = SwaggerUIBundle({
    url: "/api.yml",
    dom_id: '#swagger-ui',
    presets: [
      SwaggerUIBundle.presets.apis,
      SwaggerUIBundle.SwaggerUIStandalonePreset
    ],
  })
</script>

<style>
    .information-container{
        display: none
    }
    .swagger-ui .wrapper{
        padding-left: 0px!important;
        padding-right: 0px!important;
    }
    .swagger-ui section.col-12{
        padding-left: 0px!important;
        padding-right: 0px!important;
    }
</style>