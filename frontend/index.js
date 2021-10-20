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
      field: "Manufacturer",
      width: 150
    },
    {
      field: "Name",
      width: 150
    },
    {
      field: "Category",
      width: 100
    },
    {
      field: "SubCategory",
      width: 100
    },
    {
      field: "Total (kgCO2eq)",
      filter: 'agNumberColumnFilter',
      width: 80
    },
    {
      field: "Use (%)",
      filter: 'agNumberColumnFilter',
      width: 80
    },
    {
      field: "Yearly TEC (kWh)",
      hide: true,
      width: 80
    },
    {
      field: "Lifetime",
      filter: 'agNumberColumnFilter',
      width: 50
    },
    {
      field: "Use Location",
      width: 100
    },
    {
      field: "Date",
      hide: true,
      width: 100
    },
    {
      field: "Sources",
      hide: true,
      width: 100
    },
    {
      field: "Error (%)",
      hide: true,
      filter: 'agNumberColumnFilter',
      width: 100
    },
    {
      field: "Manufacturing",
      filter: 'agNumberColumnFilter',
      width: 100
    },
    {
      field: "Weight",
      hide: true,
      filter: 'agNumberColumnFilter',
      width: 100
    },
    {
      field: "Assembly Location",
      width: 100
    },
    {
      field: "Screen size",
      hide: true,
      filter: 'agNumberColumnFilter',
      width: 100
    },
    {
      field: "Server Type",
      width: 100
    },
    {
      field: "HDD/SSD",
      hide: true,
      width: 100
    },
    {
      field: "RAM",
      hide: true,
      filter: 'agNumberColumnFilter',
      width: 100
    },
    {
      field: "CPU",
      hide: true,
      filter: 'agNumberColumnFilter',
      width: 100
    },
    {
      field: "U",
      filter: 'agNumberColumnFilter',
      width: 50
    },
  ];

  const rowData = data.data;

  const objectsData = rowData.map((row, i) => {
    return {
      'Manufacturer': row[0],
      'Name': row[1],
      'Category': row[2],
      'SubCategory': row[3],
      'Total (kgCO2eq)': row[4],
      'Use (%)': row[5],
      'Yearly TEC (kWh)': row[6],
      'Lifetime': row[7],
      'Use Location': row[8],
      'Date': row[9],
      'Sources': row[10],
      'Error (%)': row[11],
      'Manufacturing': row[12],
      'Weight': row[13],
      'Assembly Location': row[14],
      'Screen size': row[15],
      'Server Type': row[16],
      'HDD/SSD': row[17],
      'RAM': row[18],
      'CPU': row[19],
      'U': row[20],
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
    if ( objectsData.indexOf("Use Location") && ! objectsData[i]["Use Location"] == "" ) {
      if ( ! (objectsData[i]["Use Location"] in per_use_loc) ) {
        per_use_loc[objectsData[i]["Use Location"]] = {
            avg_use: 0,
            avg_manuf: 0,
            nb_use: 0,
            nb_manuf: 0
        };
      }
    }
    if (! objectsData[i]["Use (%)"] == "") {
      let res_use = parseFloat(objectsData[i]["Use (%)"].replace('%', ''));
      let res_lifetime = objectsData[i]["Lifetime"];
      if (! isNaN(res_use)) {
        avg_use = avg_use + res_use;
        if ( res_lifetime != "" ) {
            console.log("avg_lifetime="+avg_lifetime+" res_lifetime="+res_lifetime);
            avg_lifetime += parseFloat(res_lifetime);
            nb_lifetimes++;
        }
        if ( objectsData[i]["Use Location"] in per_use_loc ) {
          per_use_loc[objectsData[i]["Use Location"]]["avg_use"] = per_use_loc[objectsData[i]["Use Location"]]["avg_use"] + res_use;
          per_use_loc[objectsData[i]["Use Location"]]["nb_use"]++;
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
        if ( objectsData[i]["Use Location"] in per_use_loc ) {

          per_use_loc[objectsData[i]["Use Location"]]["avg_manuf"] = per_use_loc[objectsData[i]["Use Location"]]["avg_manuf"] + res_manuf;
          per_use_loc[objectsData[i]["Use Location"]]["nb_manuf"]++;
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
