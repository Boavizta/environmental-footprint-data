document.addEventListener("DOMContentLoaded", function () {
  fetch('../boavizta-data-us.csv')
    .then(response => response.text())
    .then(text => gridit(text))
});

function gridit(csv) {
  data = Papa.parse(csv), {
    header: true
  };

  const columnDefs = [{
      field: "manufacturer",
      width: 150
    },
    {
      field: "name",
      width: 150
    },
    {
      field: "category",
      width: 100
    },
    {
      field: "subcategory",
      width: 100
    },
    {
      field: "gwp_total",
      filter: 'agNumberColumnFilter',
      width: 80
    },
    {
      field: "gwp_use_ratio",
      filter: 'agNumberColumnFilter',
      width: 80
    },
    {
      field: "yearly_tec",
      hide: true,
      width: 80
    },
    {
      field: "lifetime",
      filter: 'agNumberColumnFilter',
      width: 50
    },
    {
      field: "use_location",
      width: 100
    },
    {
      field: "report_date",
      hide: true,
      width: 100
    },
    {
      field: "sources",
      hide: true,
      width: 100
    },
    {
      field: "gwp_error_ratio",
      hide: true,
      filter: 'agNumberColumnFilter',
      width: 100
    },
    {
      field: "gwp_manufacturing_ratio",
      filter: 'agNumberColumnFilter',
      width: 100
    },
    {
      field: "weight",
      hide: true,
      filter: 'agNumberColumnFilter',
      width: 100
    },
    {
      field: "assembly_location",
      width: 100
    },
    {
      field: "screen_size",
      hide: true,
      filter: 'agNumberColumnFilter',
      width: 100
    },
    {
      field: "server_type",
      width: 100
    },
    {
      field: "hard_drive",
      hide: true,
      width: 100
    },
    {
      field: "memory",
      hide: true,
      filter: 'agNumberColumnFilter',
      width: 100
    },
    {
      field: "number_cpu",
      hide: true,
      filter: 'agNumberColumnFilter',
      width: 100
    },
    {
      field: "height",
      filter: 'agNumberColumnFilter',
      width: 50
    },
  ];

  const rowData = data.data;

  const objectsData = rowData.map((row, i) => {
    return {
      'manufacturer': row[0],
      'name': row[1],
      'category': row[2],
      'subcategory': row[3],
      'gwp_total': row[4],
      'gwp_use_ratio': row[5],
      'yearly_tec': row[6],
      'lifetime': row[7],
      'use_location': row[8],
      'report_date': row[9],
      'sources': row[10],
      'gwp_error_ratio': row[11],
      'gwp_manufacturing_ratio': row[12],
      'weight': row[13],
      'assembly_location': row[14],
      'screen_size': row[15],
      'server_type': row[16],
      'hard_drive': row[17],
      'memory': row[18],
      'number_cpu': row[19],
      'height': row[20],
    }
  })

  objectsData.shift()

  const gridOptions = {
    defaultColDef: {
      sortable: true,
      filter: true,
      resizable: true,
    },
    columnDefs: columnDefs,
    rowSelection: 'single',
    rowMultiSelectWithClick: true,
    rowData: objectsData,
    pagination: true,
  };

  const eGridDiv = document.querySelector('#myGrid');
  new agGrid.Grid(eGridDiv, gridOptions);

  // Manufacturing % Use % Use Location . Total (kgCO2eq) .
    // use vs manuf global
    //  use vs manuf by use location
    // use vs manuf by use location & assembly & build location
    // use vs manuf by vendor

  console.log(objectsData);

  let avg_use = 0;
  let avg_manuf = 0;
  let avg_lifetime = 0;
  let use_fails = 0;
  let manuf_fails = 0;
  let nb_lifetimes = 0;
  let per_use_loc = Object();
  for (let i = 0; i < objectsData.length; i++) {
    if ( objectsData.indexOf("use_location") && ! objectsData[i]["use_location"] == "" ) {
      if ( ! (objectsData[i]["use_location"] in per_use_loc) ) {
        per_use_loc[objectsData[i]["use_location"]] = {
            avg_use: 0,
            avg_manuf: 0,
            nb_use: 0,
            nb_manuf: 0
        };
      }
    }
    if (! objectsData[i]["gwp_use_ratio"] == "") {
      let res_use = parseFloat(objectsData[i]["gwp_use_ratio"].replace('%', ''));
      let res_lifetime = objectsData[i]["lifetime"];
      if (! isNaN(res_use)) {
        avg_use = avg_use + res_use;
        if ( res_lifetime != "" ) {
            console.log("avg_lifetime="+avg_lifetime+" res_lifetime="+res_lifetime);
            avg_lifetime += parseFloat(res_lifetime);
            nb_lifetimes++;
        }
        if ( objectsData[i]["use_location"] in per_use_loc ) {
          per_use_loc[objectsData[i]["use_location"]]["avg_use"] = per_use_loc[objectsData[i]["use_location"]]["avg_use"] + res_use;
          per_use_loc[objectsData[i]["use_location"]]["nb_use"]++;
        }
      } else {
        use_fails++;
      }
    } else {
      use_fails++;
    }
    if (! objectsData[i]["Manufacturing"] == "") {
      let res_manuf = parseFloat(objectsData[i]["Manufacturing"].replace('%', ''));
      if (! isNaN(res_manuf)) {
        avg_manuf = avg_manuf + res_manuf;
        if ( objectsData[i]["use_location"] in per_use_loc ) {

          per_use_loc[objectsData[i]["use_location"]]["avg_manuf"] = per_use_loc[objectsData[i]["use_location"]]["avg_manuf"] + res_manuf;
          per_use_loc[objectsData[i]["use_location"]]["nb_manuf"]++;
        }
      } else {
        manuf_fails++;
      }
    } else {
      manuf_fails++;
    }
  }
  avg_use = avg_use / (parseFloat(objectsData.length) - use_fails);
  avg_manuf = avg_manuf / (parseFloat(objectsData.length) - manuf_fails);
  var pieOptions = {
  	segmentShowStroke: false,
  	animateScale: true
  }
  var pie_elmt = document.getElementById("camembert");
  var caption = document.createElement("P");
  pie_elmt.parentNode.appendChild(caption);
  var camembert = pie_elmt.getContext("2d");
  //var camemberts = new Array();
  var pieData =
        [
          {
            value: avg_use,
  		    color: "#9277a8",
            label: "Use phase"
  	      },
  	      {
     		value: avg_manuf,
     		color: "#357dcc",
            label: "Manufacturing"
     	  },
          {
            value: (100 - avg_manuf - avg_use),
            color: "#2596be",
            label: "Rest of the lifecycle"
          }
        ];

  var positioner = "right";
  for (const u in per_use_loc) {
    if ( u != "WW") {
        let use = (parseFloat(per_use_loc[u]["avg_use"])/parseFloat(per_use_loc[u]["nb_use"]));
        let manuf = (parseFloat(per_use_loc[u]["avg_manuf"])/parseFloat(per_use_loc[u]["nb_manuf"]));
        let rest = 100 - use - manuf;
        if (isNaN(manuf) && !isNaN(use)) {
          rest = 100 - use;
          manuf = 0;
        }
        var new_camembert = document.getElementById("camembert").cloneNode(true);
        var new_camembert_ctx = new_camembert.getContext("2d");
        new_camembert.id = "loc-"+u;
        var title = document.createElement("H4");
        title.innerText = "Ratio scope 2/scope 3 par lieu d'utilisation : "+u;
        var new_div = document.createElement("DIV");
        new_div.className = "camembert-"+positioner;
        new_div.appendChild(title);
        new_div.appendChild(new_camembert);
        document.getElementById("stats").appendChild(new_div);

        var newPieData =
            [
              {
                value: use,
  		        color: "#9277a8",
                label: "Use phase"
  	          },
  	          {
         		value: manuf,
     		    color: "#357dcc",
                label: "Manufacturing"
         	  },
              {
                value: rest,
                color: "#2596be",
                label: "Rest of the lifecycle"
              }
            ];


        new Chart(new_camembert_ctx).Pie(newPieData, pieOptions);
        if (positioner == "left") {
          positioner = "right";
        } else {
          positioner = "left";
        }
    }
  }
  caption.innerText = "Average lifetime : "+(avg_lifetime/nb_lifetimes);
  new Chart(camembert).Pie(pieData, pieOptions);
};
