<script lang="ts">
    import AgGrid from "@budibase/svelte-ag-grid";
//    import csv from "../../static/boavizta-data-us.csv"
    import Papa from "papaparse";
    import {onMount} from "svelte";

    let data = [];
    let api;
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

    let options = {
        defaultColDef: {
            sortable: true,
            filter: true,
            resizable: true,
        },
        //columnDefs: columnDefs,
        rowSelection: 'multiple',
        //onSelectionChanged: onSelectionChanged,
        rowMultiSelectWithClick: true,
        pagination: true,
        //rowData: data,
        onFilterChanged: onFilterChanged
    };

    function onFilterChanged(e){
        let rowData = [];
        api.forEachNodeAfterFilter(node => {
            rowData.push(node.data);
        });
        console.log(rowData)
    }

    function gridit(csv) {
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
        data = gridit(text)
    });

    function onSelect(e){
        console.log(e)
    }
</script>

<AgGrid {options} bind:data {columnDefs} on:select={onSelect} bind:api/>