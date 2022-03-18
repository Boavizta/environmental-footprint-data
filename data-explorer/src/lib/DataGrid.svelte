<script lang="ts">
    import AgGrid from "@budibase/svelte-ag-grid";

    let data = [
            { Name: "Toyota", SubCategory: "1", Use: 35000 },

    ];


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
        //onFilterChanged: onFilterChanged
    };

</script>

<AgGrid {options} bind:data {columnDefs}/>