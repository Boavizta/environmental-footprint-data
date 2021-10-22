
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
  field: "Use",
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
  field: "Error",
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

var gridOptions = {
  defaultColDef: {
    sortable: true,
    filter: true,
    resizable: true,
  },
  columnDefs: columnDefs,
  rowSelection: 'single',
  rowMultiSelectWithClick: true,
  pagination: true,
  rowData: [],
  onFilterChanged: function() {
    buildcharts()
    }
};


function buildcharts() {
  let avg_use = 0;
  let total_use = 0;
  let filtered_items = 0;
  console.log("buildcharts");
  objectsData = gridOptions.rowData;
  console.log(gridOptions);
  gridOptions.api.forEachNodeAfterFilter((rowNode, index) => {
    RowUse = parseFloat(rowNode.data.Use)
    if (!isNaN(RowUse)) {
      total_use = total_use + RowUse;
      filtered_items = filtered_items + 1;
    }
  });
  avg_use = total_use / filtered_items;
  console.log('Average use of ' + avg_use + ' on ' + filtered_items + ' items.');
  var ChartData = [
    { scope: 'Scope 2', percentage: avg_use },
    { scope: 'Scope 3', percentage: (100 - avg_use) },
  ];
  var ChartOptions = {
    container: document.querySelector('#myChart'),
    autoSize: true,
    series: [
      {
        data: ChartData,
        type: 'pie',
        labelKey: 'scope',
        angleKey: 'percentage',
        label: {
          minAngle: 0,
        },
        callout: {
          strokeWidth: 2,
        },
        highlightStyle: {
          item: {
            fill: '#94a1a1',
            stroke: '#94a1a1',
            strokeWidth: 2
          }
        },
        fills: [
          '#008a8c',
          '#003964',
        ],
        strokes: [
          '#008a8c',
          '#003964',
        ],
      },
    ],
    legend: {
      enabled: true,
    },
  };

  var chart = agCharts.AgChart.create(ChartOptions);
};
function gridit(csv) {
  data = Papa.parse(csv), {
    header: true
  };

  const rowData = data.data;

  const objectsData = rowData.map((row, i) => {
    return {
      'Manufacturer': row[0],
      'Name': row[1],
      'Category': row[2],
      'SubCategory': row[3],
      'Total (kgCO2eq)': row[4],
      'Use': row[5],
      'Yearly TEC (kWh)': row[6],
      'Lifetime': row[7],
      'Use Location': row[8],
      'Date': row[9],
      'Sources': row[10],
      'Error': row[11],
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

  objectsData.shift();
  gridOptions.api.setRowData(objectsData);
  console.log(objectsData)


  // Manufacturing % Use % Use Location . Total (kgCO2eq) .
    // use vs manuf global
    //  use vs manuf by use location
    // use vs manuf by use location & assembly & build location
    // use vs manuf by vendor
  buildcharts(objectsData)
};

document.addEventListener("DOMContentLoaded", function () {
  var eGridDiv = document.querySelector('#myGrid');
  fetch('../boavizta-data-us.csv')
      .then(response => response.text())
      .then(text => gridit(text))
  new agGrid.Grid(eGridDiv, gridOptions);
});
