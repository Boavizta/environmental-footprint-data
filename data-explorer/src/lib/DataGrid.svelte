<script lang="ts">
    import { _ } from 'svelte-i18n';
    import AgGrid from "@budibase/svelte-ag-grid";
//    import csv from "../../static/boavizta-data-us.csv"
    import Papa from "papaparse";
    import {createEventDispatcher, onMount} from "svelte";

    let dataInit = [];
    let _filterApi;
    const dispatcher = createEventDispatcher();

    function updateDataGrid(rows){
        dispatcher('updateDataGrid',rows)
    }

    const columnDefs    = [{
            headerName: $_('index.manufacturer'),
            field: "Manufacturer",
            width: 150
        },
        {
            headerName: $_('index.name'),
            field: "Name",
            width: 300
        },
        {
            headerName: $_('index.category'),
            field: "Category",
            width: 120
        },
        {
            headerName: $_('index.subcategory'),
            field: "SubCategory",
            width: 120
        },
        {
            headerName: "Total (kgCO2eq)",
            field: "Total (kgCO2eq)",
            filter: false,
            width: 150
        },
        {
            headerName: $_('index.use'),
            field: "Use",
            filter: false,
            width: 120
        },
        {
            headerName: $_('index.yearlyTec'),
            field: "Yearly TEC (kWh)",
            hide: true,
            filter: false,
            width: 150
        },
        {
            headerName: $_('index.lifetime'),
            field: "Lifetime",
            //hide: true,
            filter: false,
            width: 120,
        },
        {
            field: "Use Location",
            hide: true,
            width: 100
        },
        {
            headerName: $_('index.manufacturing'),
            field: "Manufacturing",
            filter: false,
            width: 150
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
            field: "Weight",
            hide: true,
            filter: 'agNumberColumnFilter',
            width: 100
        },
        {
            field: "Assembly Location",
            hide: true,
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
            hide: true,
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
            hide: true,
            filter: 'agNumberColumnFilter',
            width: 50
        },
    ];

    let options = {
        defaultColDef: {
            sortable: false,
            filter: true,
            resizable: false,
        },
        //columnDefs: columnDefs,
        rowSelection: 'single',
        //onSelectionChanged: onSelect,
        rowMultiSelectWithClick: true,
        pagination: true,
        paginationPageSize:10,
        //rowData: data,
        onFilterChanged: onFilterChanged
    };

    function getFilterRows(filterApi){
        if(filterApi != undefined){
            _filterApi = filterApi
        }

        if(_filterApi != undefined){
            let rowData = [];
            //get selected row
            _filterApi.forEachNodeAfterFilter(node => {
                rowData.push(node.data);
            });
            //console.log(rowData)
            return rowData;
        }else{
            //no filter has been applied return all set
            return dataInit
        }
    }

    function onFilterChanged(e){
        //console.log(e)
        let filterRows = getFilterRows(e.api)
        updateDataGrid(filterRows);
    }

    function toRows(csv) {
        const csvParsed = Papa.parse(csv)

        const rowData = csvParsed.data;

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
        return objectsData;
    }

    onMount(async () => {
        const res = await fetch("./boavizta-data-us.csv");
        const text = await res.text();
        dataInit = toRows(text)
        updateDataGrid(dataInit)
    });

    function onSelect(e){
        //console.log(e)
        if(e.detail.length == 0){
            //selection is empty, return full data
            updateDataGrid(getFilterRows(e.api))
        }else{
            //return selection
            updateDataGrid(e.detail)
        }
    }
</script>

<AgGrid {options} data="{dataInit}" {columnDefs} on:select={onSelect}/>