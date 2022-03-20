<script lang="ts">

    import DataGrid from "./DataGrid.svelte";
    import LifetimeInput from "./LifetimeInput.svelte";
    import RegionPicker from "./RegionPicker.svelte";
    import RequestButton from "./RequestButton.svelte";
    import EquivalentImpacts from "./EquivalentImpacts.svelte";
    import ImpactsPieChart from "./ImpactsPieChart.svelte";

    let datagrid;
    let lifetime;
    let region;
    let disabledSearchButton;
    let numberRows;
    let scope2;
    let scope3;
    let selected_rows;

    function impactScope3(rows_selection):number{
        let scope3 = 0;
        rows_selection.forEach(row =>{
            if(row["Total (kgCO2eq)"] != undefined) {
                if(row["Total (kgCO2eq)"] != undefined && row["Manufacturing"] != undefined){
                    scope3 += row["Total (kgCO2eq)"]*row["Manufacturing"];
                }
            }
        });
        return scope3
    }

    function electricalImpactFactor(location: Location):number {
        return 1;
    }

    function impactScope2(rows_selection, lifetime, location, region):number{
        let scope2 = 0;
        if(lifetime == undefined && region == undefined){
            rows_selection.forEach(row =>{
                if(row["Total (kgCO2eq)"] != undefined) {
                    scope2 += row["Total (kgCO2eq)"]*row["Use"];
                }
            })
        }else if (lifetime != undefined && region == undefined){
            rows_selection.forEach(row => {
                if(row["Total (kgCO2eq)"] != undefined) {
                    scope2 += ((row["Total (kgCO2eq)"]*row["Use"])/row["Lifetime"])*lifetime
                }
            });
        }else if (lifetime == undefined && region != undefined){
            rows_selection.forEach(row => {
                if(row["Yearly TEC (kWh)"] != undefined) {
                    scope2 += row["Yearly TEC (kWh)"]*row["Lifetime"]*electricalImpactFactor(location)
                }
            });
        }else if (lifetime != undefined && region != undefined){
            rows_selection.forEach(row => {
                if(row["Yearly TEC (kWh)"] != undefined){
                    scope2 += row["Yearly TEC (kWh)"]*lifetime*electricalImpactFactor(location);
                }
                })
            }
        return scope2
    }

    function calculateImpacts(){
        console.log("lifetime ", lifetime)
        console.log("region ", region)
        numberRows = selected_rows.length
        console.log("numberRows ", numberRows)
        scope2 = impactScope2(selected_rows, lifetime, "",region);
        scope3 = impactScope3(selected_rows);
        console.log("scope2 ", scope2)
        console.log("scope3 ", scope3)
    }

    function onDataGridUpdate(e){
        //console.log("DataExplorer:onDataGridUpdate")
        //console.log(e.detail)
        selected_rows = e.detail

        console.log("DataExplorer:onDataGridUpdate:", numberRows.length)
    }

</script>
<div>
<DataGrid {datagrid} on:updateDataGrid={onDataGridUpdate}/>
<RegionPicker bind:region={region}/>
<LifetimeInput bind:lifetime={lifetime}/>
<RequestButton {disabledSearchButton} onClick={calculateImpacts}/>
<EquivalentImpacts gwpImpactTotal="200"/>
<ImpactsPieChart {scope2} {scope3} {numberRows}></ImpactsPieChart>
</div>
