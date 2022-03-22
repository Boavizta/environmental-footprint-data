<script lang="ts">
    import { _ } from 'svelte-i18n';

    import DataGrid from "./DataGrid.svelte";
    import LifetimeInput from "./LifetimeInput.svelte";
    import RegionPicker from "./RegionPicker.svelte";
    import RequestButton from "./RequestButton.svelte";
    import EquivalentImpacts from "./EquivalentImpacts.svelte";
    import ImpactsPieChart from "./ImpactsPieChart.svelte";

    let datagrid;
    let lifetime;
    let selectedRegion;
    let disabledSearchButton;
    let scope2;
    let scope3;
    let selectedRows =[];

    function impactScope3(rows_selection):{result:number, lines:number}{
        let scope3 = 0;
        let processedLineNumber = 0;
        rows_selection.forEach(row =>{
            if(row["gwp_total"] != undefined) {
                if(row["gwp_total"] != undefined && row["gwp_manufacturing_ratio"] != undefined){
                    scope3 += row["gwp_total"]*row["gwp_manufacturing_ratio"];
                    processedLineNumber++
                }
            }
        });
        return {result:scope3, lines:processedLineNumber}
    }

    function impactScope2(rows_selection, lifetime, electricalImpactFactor):{result:number, lines:number}{
        let scope2 = 0;
        let processedLineNumber = 0
        if(lifetime == undefined && electricalImpactFactor == -1){
            rows_selection.forEach(row =>{
                if(row["gwp_total"] != undefined && row["gwp_use_ratio"] != undefined) {
                    scope2 += row["gwp_total"]*row["gwp_use_ratio"];
                    processedLineNumber++;
                }
            })
        }else if (lifetime != undefined && electricalImpactFactor == -1){
            rows_selection.forEach(row => {
                if(row["gwp_total"] != undefined
                    && row["gwp_use_ratio"] != undefined
                    && row["lifetime"] != undefined) {
                    scope2 += ((row["gwp_total"]*row["gwp_use_ratio"])/row["lifetime"])*lifetime
                    processedLineNumber++;
                }
            });
        }else if (lifetime == undefined && electricalImpactFactor !== -1){
            rows_selection.forEach(row => {
                if(row["yearly_tec"] != undefined) {
                    scope2 += row["yearly_tec"]*row["lifetime"]*electricalImpactFactor
                    processedLineNumber++;
                }
            });
        }else if (lifetime != undefined && electricalImpactFactor !== -1){
            rows_selection.forEach(row => {
                if(row["yearly_tec"] != undefined){
                    scope2 += row["yearly_tec"]*lifetime*electricalImpactFactor;
                    processedLineNumber++;
                }
            })
        }
        return {result:scope2, lines:processedLineNumber}
    }

    function calculateImpacts(){
        console.log("lifetime ", lifetime)
        console.log("selectedRowsNumber ", selectedRows.length)
        console.log("region ", selectedRegion)
        scope2 = impactScope2(selectedRows, lifetime, selectedRegion.value);
        scope3 = impactScope3(selectedRows);
        console.log("scope2 ", scope2)
        console.log("scope3 ", scope3)
    }

    function onDataGridUpdate(e){
        //console.log("DataExplorer:onDataGridUpdate")
        //console.log(e.detail)
        selectedRows = e.detail
        console.log("DataExplorer:onDataGridUpdate:", selectedRows.length)
    }
    function handleRegionSelect(region){
        console.log(region)
        selectedRegion = region
    }

</script>
<div>
    <DataGrid {datagrid} on:updateDataGrid={onDataGridUpdate}/>
    <div class="calculator">
        <div>
            <RegionPicker bind:value={selectedRegion} onSelect="{handleRegionSelect}"/>
        </div>
        <div>
            <LifetimeInput bind:lifetime={lifetime}/>
        </div>
        <p>{$_('index.selected_rows',{ values: {n:selectedRows.length}})}</p>
        <div>
            <RequestButton {disabledSearchButton} onClick={calculateImpacts}/>
        </div>
    </div>
    <h3 class="title-second">Ratio Scope 2 / Scope 3</h3>
    <div>
        <ImpactsPieChart {scope2} {scope3} selectedRowsNumber={selectedRows?selectedRows.length:0}/>
        <EquivalentImpacts gwpImpactTotal="--"/>
    </div>
</div>

<style>
    .calculator{
        background: #e7f2ff;
        padding: 5px;
        border-radius: .5rem;
    }
</style>
