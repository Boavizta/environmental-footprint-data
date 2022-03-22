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
            headerName: $_('datagrid.manufacturer'),
            field: "manufacturer",
            width: 150
        },
        {
            headerName: $_('datagrid.name'),
            field: "name",
            width: 300
        },
        {
            headerName: $_('datagrid.category'),
            field: "category",
            width: 120
        },
        {
            headerName: $_('datagrid.subcategory'),
            field: "subcategory",
            width: 120
        },
        {
            headerName: $_('datagrid.total'),
            field: "gwp_total",
            filter: false,
            width: 150
        },
        {
            headerName: $_('datagrid.use'),
            field: "gwp_use_ratio",
            filter: false,
            width: 120
        },
        {
            headerName: $_('datagrid.manufacturing'),
            field: "gwp_manufacturing_ratio",
            filter: false,
            width: 150
        },
        {
            headerName: $_('datagrid.yearlyTec'),
            field: "yearly_tec",
            hide: true,
            filter: false,
            width: 150
        },
        {
            headerName: $_('datagrid.lifetime'),
            field: "lifetime",
            //hide: true,
            filter: false,
            width: 120,
        },
        {
            field: "use_location",
            hide: true,
            width: 100
        },

        {
            field: "added_date",
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
            field: "weight",
            hide: true,
            filter: 'agNumberColumnFilter',
            width: 100
        },
        {
            field: "assembly_location",
            hide: true,
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
            hide: true,
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
        }
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
        const csvParsed = Papa.parse(csv,{header:true, dynamicTyping: true})
        const rowData = csvParsed.data;
        console.log(rowData)
        rowData.shift();
        return rowData;
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
